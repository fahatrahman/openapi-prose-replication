"""End-to-end CPU test of the split flow with a tiny random Granite model and 12 synthetic tasks.
Runs the REAL cell 7/8/9 code of the Granite notebooks (halves patched, final unchanged) in fresh namespaces
to simulate separate Kaggle sessions: 07a (interrupted, resumed), 07b, 07m merge, unchanged 07 final.
Also checks split output == unsplit output."""
import json, os, sys, shutil, hashlib, tempfile, csv, io, time, types, importlib.util, contextlib, re
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM

SCR = Path("scratch")  # adjust to your working folder
OUT = SCR / "split/out"
NB07 = Path("granite_run/4_Notebook_07_Main/Notebook 07 Main (Granite).ipynb")  # adjust
N, H = 12, 6
T = Path(tempfile.mkdtemp(prefix="splitE2E_"))

def cells(path):
    return ["".join(c["source"]) for c in json.load(open(path))["cells"]]

orig = cells(NB07)
A = cells(next((OUT / "4a_Notebook_07a_Main_FirstHalf").glob("*.ipynb")))
B = cells(next((OUT / "4b_Notebook_07b_Main_SecondHalf").glob("*.ipynb")))
M = cells(next((OUT / "4c_Notebook_07m_Merge_Checkpoints").glob("*.ipynb")))
assert len(A) == 10 and len(B) == 10 and len(M) == 2

# tiny model + real tokenizer
tok = AutoTokenizer.from_pretrained(SCR / "tok")
cfg = AutoConfig.from_pretrained(SCR / "tok")
cfg.num_hidden_layers = 2; cfg.hidden_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.intermediate_size = 256
torch.manual_seed(0)
model = AutoModelForCausalLM.from_config(cfg).to(torch.float32).eval()
torch.cuda.synchronize = lambda *a, **k: None

head = orig[1].split("def find_frozen_stage")[0]
module_src = (orig[7].split("# BEGIN_STAGE07_" + "GENERATION_MODULE", 1)[1].split("# END_STAGE07_" + "GENERATION_MODULE", 1)[0].strip() + "\n")

# synthetic ledger
tasks = []
for i in range(1, N + 1):
    pair = (i + 1) // 2
    tasks.append({"task_id": f"op{pair:03d}_{'L0' if i % 2 else 'L1'}_r1", "pair_id": f"pair{pair:03d}", "op_id": f"op{pair:03d}",
                  "partition": "main", "condition": "L0" if i % 2 else "L1", "replicate": "1", "seed": str(1000 + pair),
                  "order": str(i), "model_revision": "r", "prompt_path": f"prompts/{i:03d}.txt", "prompt_sha256": "",
                  "prompt_tokens": "20", "expected_output_path": ""})
for t in tasks:
    t["expected_output_path"] = f"runs/main/raw/{t['task_id']}.txt"
ledger = io.StringIO(); w = csv.DictWriter(ledger, fieldnames=list(tasks[0]), lineterminator="\n"); w.writeheader(); w.writerows(tasks)
LEDGER_BYTES = ledger.getvalue().encode()

def session(name, cell_texts, source_dirs, edits=(), tasks_in=None):
    """Fresh namespace == fresh Kaggle session. Returns namespace."""
    root = T / name; shutil.rmtree(root, ignore_errors=True); root.mkdir(parents=True)
    src = root / "input"; src.mkdir()
    for d in source_dirs:
        for f in Path(d).rglob("*"):
            if f.is_file():
                (src / f.relative_to(d)).parent.mkdir(parents=True, exist_ok=True); shutil.copy(f, src / f.relative_to(d))
    os.environ["STAGE07_SOURCE_BASE"] = str(src)
    os.environ["STAGE07_PROJECT_ROOT"] = str(root / "work/prose_operation_experiment_stage07_main")
    os.environ["STAGE07_DATASET_ROOT"] = str(root / "work/stage_07_main_dataset")
    ns = {"__name__": "nbtest"}
    exec(compile(head, "cell1head", "exec"), ns)
    P = ns["PROJECT_ROOT"]
    ns.update(MAIN_TASKS=N, MAIN_OPERATIONS=N // 2, torch=torch, model=model, tokenizer=tok, embedding_device=torch.device("cpu"),
              MODEL_ID="ibm-granite/granite-3.3-8b-instruct", MODEL_REVISION="rev", TOKENIZER_REVISION="rev",
              RUNTIME={"dtype": "float16", "max_rendered_input_tokens": 5376, "max_new_tokens": 8, "max_total_tokens": 5384},
              GENERATION_SETTINGS=dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.1, num_beams=1),
              PACKAGE_VERSIONS={"x": "1"}, MODEL_LOAD_RECORD={"device_map": {"0": "0", "1": "1"}},
              SOURCE_IDENTITIES={"00": {"internal_manifest_sha256": "a" * 64, "external_manifest_sha256": "b" * 64},
                                 "06": {"internal_manifest_sha256": "c" * 64, "external_manifest_sha256": "d" * 64}},
              TASK_LEDGER_BYTES=LEDGER_BYTES)
    ts = [dict(t) for t in tasks]
    for t in ts:
        p = P / t["prompt_path"]; p.parent.mkdir(parents=True, exist_ok=True)
        data = tok.apply_chat_template([{"role": "system", "content": "S"}, {"role": "user", "content": "hello " + t["task_id"]}],
                                       tokenize=False, add_generation_prompt=True).encode()
        p.write_bytes(data); t["prompt_sha256"] = hashlib.sha256(data).hexdigest()
    # prompt hashes feed the task rows only; the ledger bytes stay constant (hash of rows is not used by cell 8)
    ns["TASKS"] = ts
    # emulate cell 7: write + import generation module, then mark cells passed
    ns["write_bytes_immutable"](P / "src/generation.py", module_src.encode())
    spec = importlib.util.spec_from_file_location("stage07_generation_" + name, P / "src/generation.py")
    gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
    ns["generation"] = gen; ns["generation_module_path"] = P / "src/generation.py"
    ns["report_cell"](7)
    for n, (old, new) in enumerate(edits):
        pass
    for k, text in enumerate(cell_texts):
        for old, new in edits:
            text = text.replace(old, new)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(text, f"{name}-cell{k}", "exec"), ns)
        ns.setdefault("_out", []).append(buf.getvalue())
    return ns

def fast(text):
    return text.replace("CHECKPOINT_INTERVAL = 500", "CHECKPOINT_INTERVAL = 3")

def half_texts(h, cell8_extra=()):
    base = A if h == "a" else B
    c8 = base[8].replace("HALF_LAST_ORDER = 850", f"HALF_LAST_ORDER = {H}").replace("HALF_FIRST_ORDER = 851", f"HALF_FIRST_ORDER = {H+1}") \
                .replace("HALF_LAST_ORDER = 1700", f"HALF_LAST_ORDER = {N}")
    return [fast(c8), base[9]]

def zips(ns):
    return sorted(p.name for p in ns["CHECKPOINT_EXPORT_DIRECTORY"].glob("*.zip"))

ART = lambda ns: ns["CHECKPOINT_EXPORT_DIRECTORY"]

# ---------------------------------------------------------------- reference: unsplit, unmodified notebook cells 8+9
ref = session("ref", [fast(orig[8]), orig[9]], [])
ref_raw = {p.name: p.read_bytes() for p in (ref["PROJECT_ROOT"] / "runs/main/raw").glob("*.txt")}
assert len(ref_raw) == N, len(ref_raw)
print("reference unsplit run:", zips(ref))

# ---------------------------------------------------------------- 07a session 1: stops via count-based guard patch (after 4 tasks)
guard_cond = "if time.time() - RUN_T0 >= TIME_GUARD_SECONDS:"
t_a1 = half_texts("a"); assert guard_cond in t_a1[1]
t_a1[1] = t_a1[1].replace(guard_cond, "if len(list(CHECKPOINT_DIRECTORY.glob('*.json'))) >= 4:")
a1 = session("a1", t_a1, [])
print("07a session 1:", zips(a1)); assert a1["TIME_GUARD_TRIPPED"] and a1["completed"] == 4
assert zips(a1) == ["stage07a_checkpoint_0003_of_0006.zip", "stage07a_checkpoint_0004_of_0006.zip"], zips(a1)
assert "TIME GUARD" in a1["_out"][-1]

# ---------------------------------------------------------------- 07a session 2: resume from newest checkpoint ONLY (dataset granite-stage-07a-ckpt)
ckA = T / "ds_a"; ckA.mkdir(); shutil.copy(ART(a1) / "stage07a_checkpoint_0004_of_0006.zip", ckA)
a2 = session("a2", half_texts("a"), [ckA])
print("07a session 2:", zips(a2), "reused", a2["reused_outcomes"], "new", a2["new_generated"])
assert a2["reused_outcomes"] == 4 and a2["new_generated"] == 2 and not a2["TIME_GUARD_TRIPPED"] and a2["completed"] == 6
assert "stage07a_checkpoint_0006_of_0006.zip" in zips(a2)

# ---------------------------------------------------------------- 07b: one session
b1 = session("b1", half_texts("b"), [])
print("07b:", zips(b1)); assert b1["completed"] == 6 and "stage07b_checkpoint_0006_of_0006.zip" in zips(b1)
# a half must never touch the other half's tasks
assert sorted(p.stem for p in (b1["PROJECT_ROOT"] / "checkpoints/tasks").glob("*.json")) == sorted(t["task_id"] for t in tasks[H:])
assert sorted(p.stem for p in (a2["PROJECT_ROOT"] / "checkpoints/tasks").glob("*.json")) == sorted(t["task_id"] for t in tasks[:H])
# half outputs equal the unsplit run, byte for byte
for sess in (a2, b1):
    for p in (sess["PROJECT_ROOT"] / "runs/main/raw").glob("*.txt"):
        assert p.read_bytes() == ref_raw[p.name], p.name
print("split raw outputs == unsplit raw outputs (byte identical)")
# same fingerprint everywhere
fp = {s["GENERATION_FINGERPRINT"] for s in (ref, a1, a2, b1)}; assert len(fp) == 1, fp
print("one shared fingerprint across unsplit/07a/07b:", fp.pop()[:16])

# ---------------------------------------------------------------- 07m merge (inputs: both halves; also an older partial 07a zip to test selection)
dsA = T / "in_a"; dsB = T / "in_b"; dsA.mkdir(); dsB.mkdir()
for f in ART(a2).glob("stage07a_*.zip"): shutil.copy(f, dsA)   # includes 0003, 0004, 0006
shutil.copy(ART(b1) / "stage07b_checkpoint_0006_of_0006.zip", dsB)
mroot = T / "merge"; shutil.rmtree(mroot, ignore_errors=True); (mroot / "input").mkdir(parents=True)
for d in (dsA, dsB):
    for f in d.glob("*.zip"): shutil.copy(f, mroot / "input" / f.name)
mt = M[1].replace("EXPECTED_TASKS_PER_HALF = 6\n".replace("6", "850"), f"EXPECTED_TASKS_PER_HALF = {H}\n") \
         .replace('INPUT_ROOT = Path("/kaggle/input")', f'INPUT_ROOT = Path("{mroot / "input"}")') \
         .replace('OUTPUT_DIRECTORY = Path("/kaggle/working/stage07_main_checkpoints")', f'OUTPUT_DIRECTORY = Path("{mroot / "work/stage07_main_checkpoints"}")')
assert f"EXPECTED_TASKS_PER_HALF = {H}" in mt and str(mroot) in mt
mns = {"__name__": "merge"}
buf = io.StringIO()
with contextlib.redirect_stdout(buf): exec(compile(mt, "merge", "exec"), mns)
print(buf.getvalue()[-400:])
merged = mroot / "work/stage07_main_checkpoints/stage07_main_checkpoint_0012_of_0012.zip".replace("0012_of_0012", "0012_of_%04d" % (2 * H))
assert merged.is_file(), list((mroot / "work/stage07_main_checkpoints").iterdir())
# the merge must refuse an incomplete half
bad = T / "merge_bad"; shutil.rmtree(bad, ignore_errors=True); (bad / "input").mkdir(parents=True)
shutil.copy(ART(a1) / "stage07a_checkpoint_0004_of_0006.zip", bad / "input"); shutil.copy(ART(b1) / "stage07b_checkpoint_0006_of_0006.zip", bad / "input")
mt_bad = mt.replace(str(mroot), str(bad))
try:
    with contextlib.redirect_stdout(io.StringIO()): exec(compile(mt_bad, "merge_bad", "exec"), {"__name__": "m"})
    raise SystemExit("MERGE ACCEPTED AN INCOMPLETE HALF")
except RuntimeError as e:
    print("merge refuses incomplete half:", str(e)[:90])
# ...and a half from a different configuration
alt = T / "merge_alt"; shutil.rmtree(alt, ignore_errors=True); (alt / "input").mkdir(parents=True)
import zipfile
shutil.copy(ART(a2) / "stage07a_checkpoint_0006_of_0006.zip", alt / "input")
with zipfile.ZipFile(ART(b1) / "stage07b_checkpoint_0006_of_0006.zip") as zin, zipfile.ZipFile(alt / "input/stage07b_checkpoint_0006_of_0006.zip", "w") as zout:
    for n in zin.namelist():
        d = zin.read(n)
        if n.endswith("config/generation_frozen.json"):
            c = json.loads(d); c["dtype"] = "bfloat16"; d = (json.dumps(c)).encode()
        zout.writestr(n, d)
try:
    with contextlib.redirect_stdout(io.StringIO()): exec(compile(mt.replace(str(mroot), str(alt)), "merge_alt", "exec"), {"__name__": "m"})
    raise SystemExit("MERGE ACCEPTED A DIFFERENT CONFIG")
except RuntimeError as e:
    print("merge refuses mismatched config:", str(e)[:100])

# ---------------------------------------------------------------- final UNCHANGED notebook 07 cells 8 + 9 with ONLY the merged checkpoint attached
ds_m = T / "ds_merged"; ds_m.mkdir(); shutil.copy(merged, ds_m)
fin = session("final", [fast(orig[8]), orig[9]], [ds_m])
print("final unchanged Nb07 cell 8:", [l for l in fin["_out"][0].splitlines() if "Restored" in l])
print("final: reused", fin["reused_outcomes"], "new", fin["new_generated"], "completed", fin["completed"])
assert fin["reused_outcomes"] == N and fin["new_generated"] == 0 and fin["completed"] == N
fin_raw = {p.name: p.read_bytes() for p in (fin["PROJECT_ROOT"] / "runs/main/raw").glob("*.txt")}
assert fin_raw == ref_raw
print("final raw outputs == unsplit reference (byte identical)")
# final run also works when partial merge (a1's 4 tasks + b) is attached: it generates only the missing 2
ds_p = T / "ds_partial"; ds_p.mkdir()
partial_in = T / "merge_part"; shutil.rmtree(partial_in, ignore_errors=True); (partial_in / "input").mkdir(parents=True)
shutil.copy(ART(a1) / "stage07a_checkpoint_0004_of_0006.zip", partial_in / "input"); shutil.copy(ART(b1) / "stage07b_checkpoint_0006_of_0006.zip", partial_in / "input")
mt_p = mt.replace(str(mroot), str(partial_in)).replace("REQUIRE_COMPLETE = True", "REQUIRE_COMPLETE = False")
with contextlib.redirect_stdout(io.StringIO()): exec(compile(mt_p, "merge_part", "exec"), {"__name__": "m"})
pz = next((partial_in / "work/stage07_main_checkpoints").glob("*.zip")); print("partial merge:", pz.name)
shutil.copy(pz, ds_p)
fin2 = session("final2", [fast(orig[8]), orig[9]], [ds_p])
print("final2: reused", fin2["reused_outcomes"], "new", fin2["new_generated"]); assert fin2["reused_outcomes"] == 10 and fin2["new_generated"] == 2
assert {p.name: p.read_bytes() for p in (fin2["PROJECT_ROOT"] / "runs/main/raw").glob("*.txt")} == ref_raw
print("\nSPLIT E2E: ALL CHECKS PASSED")
