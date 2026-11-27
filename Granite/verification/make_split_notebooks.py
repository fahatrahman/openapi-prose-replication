#!/usr/bin/env python3
"""Derive Granite Notebook 07a / 07b (half-generators) and 07m (merge) from the shipped Granite Notebook 07.

Exact asserted string patches (each must match once). Notebook 07 itself is NOT modified; it is used
unchanged as the final step after the merge.
usage: make_split.py SRC_NB07.ipynb DST_ROOT [first_half_last_order] [total_tasks]
"""
import json, sys
from pathlib import Path

SRC = Path(sys.argv[1]); DST = Path(sys.argv[2])
HALF = int(sys.argv[3]) if len(sys.argv) > 3 else 850
TOTAL = int(sys.argv[4]) if len(sys.argv) > 4 else 1700
assert TOTAL == 2 * HALF


def text(c): return "".join(c["source"])
def setsrc(c, t): c["source"] = t.splitlines(keepends=True)


def sub1(t, old, new, label):
    n = t.count(old)
    if n != 1:
        raise SystemExit(f"PATCH FAILED ({label}): {n} matches for {old[:90]!r}")
    return t.replace(old, new)


def patch(nb, idx, pairs, label):
    c = nb["cells"][idx]; t = text(c)
    for old, new in pairs:
        t = sub1(t, old, new, f"{label} cell {idx}")
    setsrc(c, t)


def clear(nb):
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []; c["execution_count"] = None


def half_notebook(label, first, last, title_word, other):
    nb = json.loads(SRC.read_text(encoding="utf-8"))
    assert len(nb["cells"]) == 15
    n = last - first + 1
    # --- markdown
    setsrc(nb["cells"][0], f"""# Notebook 07{label} Main (Granite) · {title_word} half: tasks {first} to {last} of {TOTAL}

Generates ONLY the frozen tasks whose ledger `order` is {first} to {last} (whole L0/L1 pairs stay together). It is built to run **at the same time** as Notebook 07{other}; the two halves are merged afterwards by Notebook 07m, then the unchanged Notebook 07 does the final packaging.

Use a fresh Kaggle **GPU T4 ×2** session, **Internet on**, run as **Save & Run All**. Attach the one input dataset `granite-stage-07-input` (it holds `granite-stage-00-prov` and `stage_06_main_dataset`). **To resume** after a stop, attach the latest checkpoint dataset of THIS half only: `granite-stage-07{label}-ckpt`.

What it keeps: `stage07{label}_checkpoint_NNNN_of_{n:04d}.zip` in Output (written every 500 tasks, when the half is complete, and when the time guard fires).

**Time guard:** after 10.25 hours it stops starting new tasks, writes the checkpoint ZIP and ends normally (so Kaggle's 12-hour kill never catches it mid-write). If the half is not finished, download the newest ZIP, publish it as a new version of `granite-stage-07{label}-ckpt`, attach it and Save & Run All again.

The run fingerprint, the settings and the generation code are identical to Notebook 07 (this notebook only selects which tasks to run and renames the checkpoint ZIPs), so the two halves and the final Notebook 07 accept each other's checkpoints. Both halves must run in the same Kaggle environment (same package versions, same two-GPU split); if the fingerprints differ the final step refuses the merged checkpoint instead of silently mixing runs.
""")
    # --- cell 8
    patch(nb, 8, [
        ("require_cell_pass(7)\nGENERATION_CONFIG = {",
         f'''require_cell_pass(7)

# GRANITE SPLIT RUN {label.upper()}: generate only tasks with HALF_FIRST_ORDER <= order <= HALF_LAST_ORDER.
# GENERATION_CONFIG below is deliberately unchanged. It hashes the FULL task ledger, so both halves and the
# final Notebook 07 share one run fingerprint and their checkpoints can be merged.
HALF_LABEL = "{label}"
HALF_FIRST_ORDER = {first}
HALF_LAST_ORDER = {last}
HALF_PREFIX = "stage07" + HALF_LABEL
if "ALL_TASKS" not in globals():
    ALL_TASKS = list(TASKS)
TASKS = [task for task in ALL_TASKS if HALF_FIRST_ORDER <= int(task["order"]) <= HALF_LAST_ORDER]
HALF_TASKS = len(TASKS)
_pair_sizes = {{}}
for _task in TASKS:
    _pair_sizes[_task["pair_id"]] = _pair_sizes.get(_task["pair_id"], 0) + 1
if (len(ALL_TASKS) != MAIN_TASKS or HALF_TASKS != HALF_LAST_ORDER - HALF_FIRST_ORDER + 1
        or set(_pair_sizes.values()) != {{2}}):
    raise RuntimeError("Half selection is not a whole number of L0/L1 pairs of the frozen ledger")
print(f"Half {{HALF_LABEL.upper()}}: {{HALF_TASKS}} tasks (order {{HALF_FIRST_ORDER}}-{{HALF_LAST_ORDER}}, {{len(_pair_sizes)}} pairs) of {{len(ALL_TASKS)}}", flush=True)

GENERATION_CONFIG = {{'''),
        ('CHECKPOINT_EXPORT_DIRECTORY = PROJECT_ROOT.parent / "stage07_main_checkpoints"',
         'CHECKPOINT_EXPORT_DIRECTORY = PROJECT_ROOT.parent / "stage07_main_checkpoints"\n'
         'TIME_GUARD_SECONDS = 36900  # 10.25 h: stop starting new tasks; a 12,288-token task can take ~75 min and Kaggle ends a session at 12 h\n'
         'RUN_T0 = CELL01_STARTED'),
        ('archives = set(SOURCE_BASE.rglob("stage07_main_checkpoint_*.zip"))\n    archives.update(SOURCE_BASE.rglob("stage07_main_resume*.zip"))',
         'archives = set(SOURCE_BASE.rglob(HALF_PREFIX + "_checkpoint_*.zip"))\n    archives.update(SOURCE_BASE.rglob(HALF_PREFIX + "_resume*.zip"))'),
        ('output = CHECKPOINT_EXPORT_DIRECTORY / f"stage07_main_checkpoint_{completed:04d}_of_{MAIN_TASKS:04d}.zip"',
         'output = CHECKPOINT_EXPORT_DIRECTORY / f"{HALF_PREFIX}_checkpoint_{completed:04d}_of_{HALF_TASKS:04d}.zip"'),
        ('print(f"Checkpoint ready to download ({completed}/{MAIN_TASKS}): {output}", flush=True)',
         'print(f"Checkpoint ready to download ({completed}/{HALF_TASKS}): {output}", flush=True)'),
    ], "split")
    # --- cell 9
    patch(nb, 9, [
        ("if completed % CHECKPOINT_INTERVAL == 0 or completed == MAIN_TASKS:",
         "if completed % CHECKPOINT_INTERVAL == 0 or completed == HALF_TASKS:"),
        ("if index % 10 == 0 or index == 1 or index == MAIN_TASKS:",
         "if index % 10 == 0 or index == 1 or index == HALF_TASKS:"),
        ('print({"completed_position": index, "total": MAIN_TASKS,',
         'print({"completed_position": index, "completed": completed, "total": HALF_TASKS,\n               "hours": round((time.time() - RUN_T0) / 3600, 2),'),
        ("for index, task in enumerate(TASKS, 1):",
         "TIME_GUARD_TRIPPED = False\n\n\nfor index, task in enumerate(TASKS, 1):"),
        ('    if raw_path.is_file():\n        raise RuntimeError("Existing raw output must be reconciled before generation")',
         '    if time.time() - RUN_T0 >= TIME_GUARD_SECONDS:\n'
         '        TIME_GUARD_TRIPPED = True  # nothing for this task has been written yet\n'
         '        break\n'
         '    if raw_path.is_file():\n        raise RuntimeError("Existing raw output must be reconciled before generation")'),
    ], "split")
    t = text(nb["cells"][9])
    cut = t.index("if completed != MAIN_TASKS:")
    tail = f'''if TIME_GUARD_TRIPPED:
    export_checkpoint_zip(completed)
    print("=" * 72)
    print(f"TIME GUARD: stopped cleanly after {{(time.time() - RUN_T0) / 3600:.2f}} h with {{completed}}/{{HALF_TASKS}} tasks accounted for.")
    print("Nothing is lost. Download the newest {{0}}_checkpoint_*.zip from Output, publish it as a new version of dataset".format(HALF_PREFIX))
    print("granite-stage-07{label}-ckpt, attach that dataset (plus granite-stage-07-input) and Save & Run All again.")
    print("=" * 72)
else:
    if completed != HALF_TASKS:
        raise RuntimeError(f"Expected {{HALF_TASKS}} accounted tasks, found {{completed}}")
    final_zip = CHECKPOINT_EXPORT_DIRECTORY / f"{{HALF_PREFIX}}_checkpoint_{{HALF_TASKS:04d}}_of_{{HALF_TASKS:04d}}.zip"
    if not final_zip.is_file():
        export_checkpoint_zip(HALF_TASKS)
    print("=" * 72)
    print(f"HALF {{HALF_LABEL.upper()}} COMPLETE: {{HALF_TASKS}}/{{HALF_TASKS}} tasks. Download {{final_zip.name}} from Output.")
    print("Publish it as dataset granite-stage-07{label}-ckpt, then run Notebook 07m once both halves are complete.")
    print("=" * 72)

report_cell(9, half=HALF_LABEL, half_task_count=HALF_TASKS, completed=completed,
            time_guard_tripped=TIME_GUARD_TRIPPED, newly_generated=new_generated,
            new_no_output_runtime_failures=new_no_output, reused_existing_outcomes=reused_outcomes,
            half_complete=(completed == HALF_TASKS))
'''
    setsrc(nb["cells"][9], t[:cut] + tail)
    # --- drop packaging cells 10-14 (they belong to the final Notebook 07)
    nb["cells"] = nb["cells"][:10]
    clear(nb)
    return nb


for label, first, last, word, other in (("a", 1, HALF, "first", "b"), ("b", HALF + 1, TOTAL, "second", "a")):
    nb = half_notebook(label, first, last, word, other)
    folder = {"a": "4a_Notebook_07a_Main_FirstHalf", "b": "4b_Notebook_07b_Main_SecondHalf"}[label]
    name = f"Notebook 07{label} Main (Granite, {word} half).ipynb"
    out = DST / folder / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("wrote", out)


# ====================================================================== Notebook 07m (merge)
MERGE_MD = f"""# Notebook 07m (Granite) · merge the two half checkpoints (CPU, a few minutes)

Run this **after Notebook 07a and 07b have both finished** (each shows `HALF ... COMPLETE`). It needs no GPU and no Internet.

**Attach** (both are checkpoint datasets you published from the halves):
- `granite-stage-07a-ckpt` (contains `stage07a_checkpoint_{HALF:04d}_of_{HALF:04d}.zip`)
- `granite-stage-07b-ckpt` (contains `stage07b_checkpoint_{HALF:04d}_of_{HALF:04d}.zip`)

(Shortcut: instead of the two datasets you may attach the Output of the 07a and 07b notebooks directly with Add Input → Notebook Output; the cell searches `/kaggle/input` recursively.)

**Run All.** The cell checks each half (ZIP integrity, one shared run fingerprint, every raw output matches its stored SHA-256, no task in both halves, {HALF} terminal tasks per half) and writes ONE combined checkpoint ZIP in the exact layout Notebook 07 reads:

`stage07_main_checkpoint_{TOTAL:04d}_of_{TOTAL:04d}.zip` (Output) plus `merge_report.json`.

**Keep:** download `stage07_main_checkpoint_{TOTAL:04d}_of_{TOTAL:04d}.zip` and publish it as dataset `granite-stage-07-ckpt`. The final, unchanged Notebook 07 attaches it, finds all {TOTAL} tasks done, does no generation, and builds `stage_07_main_dataset`.

If a half is unfinished, the cell stops with a clear message. Set `REQUIRE_COMPLETE = False` only if you deliberately want to merge a partial half; the final Notebook 07 then generates just the missing tasks.
"""

MERGE_CODE = f'''from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

INPUT_ROOT = Path("/kaggle/input")
OUTPUT_DIRECTORY = Path("/kaggle/working/stage07_main_checkpoints")
EXPECTED_TASKS_PER_HALF = {HALF}
TOTAL_TASKS = 2 * EXPECTED_TASKS_PER_HALF
REQUIRE_COMPLETE = True  # keep True unless you knowingly merge a partial half

CONFIG_MEMBER = "config/generation_frozen.json"
TASK_PREFIX = "checkpoints/tasks/"
RAW_PREFIX = "runs/main/raw/"
TERMINAL_STATES = {{"GENERATED", "RAW_RECOVERED", "NO_OUTPUT_RUNTIME_FAILURE"}}
HALF_PATTERNS = {{"a": "stage07a_checkpoint_*.zip", "b": "stage07b_checkpoint_*.zip"}}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_half(path):
    """Return (prefix, config_bytes, config, records, raws, terminal_count); raise on any inconsistency."""
    with ZipFile(path) as archive:
        bad = archive.testzip()
        if bad is not None:
            raise RuntimeError(f"ZIP integrity failure at {{bad}}")
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise RuntimeError("duplicate ZIP member")
        configs = [n for n in names if n == CONFIG_MEMBER or n.endswith("/" + CONFIG_MEMBER)]
        if len(configs) != 1:
            raise RuntimeError("expected exactly one frozen generation config")
        prefix = configs[0][:-len(CONFIG_MEMBER)]
        config_bytes = archive.read(configs[0])
        config = json.loads(config_bytes)
        if not isinstance(config.get("run_fingerprint"), str):
            raise RuntimeError("config has no run fingerprint")
        records, raws = {{}}, {{}}
        for name in names:
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix):]
            if relative.startswith(TASK_PREFIX) and relative.endswith(".json"):
                records[relative] = archive.read(name)
            elif relative.startswith(RAW_PREFIX) and relative.endswith(".txt"):
                raws[relative] = archive.read(name)
    terminal = 0
    for relative, data in records.items():
        record = json.loads(data)
        task_id = Path(relative).stem
        if record.get("task_id") != task_id:
            raise RuntimeError(f"{{relative}}: task id does not match file name")
        if record.get("fingerprint") != config["run_fingerprint"]:
            raise RuntimeError(f"{{task_id}}: record belongs to a different generation fingerprint")
        raw_name = RAW_PREFIX + task_id + ".txt"
        if record.get("expected_output_path") != raw_name:
            raise RuntimeError(f"{{task_id}}: unexpected output path {{record.get('expected_output_path')!r}}")
        state = record.get("state")
        if state in ("GENERATED", "RAW_RECOVERED"):
            if raw_name not in raws or sha256_bytes(raws[raw_name]) != record.get("raw_sha256"):
                raise RuntimeError(f"{{task_id}}: raw output missing or changed")
            terminal += 1
        elif state == "NO_OUTPUT_RUNTIME_FAILURE":
            if raw_name in raws:
                raise RuntimeError(f"{{task_id}}: unexpected raw output for a no-output task")
            terminal += 1
        elif state != "STARTED":
            raise RuntimeError(f"{{task_id}}: unknown state {{state!r}}")
    orphans = {{n for n in raws if TASK_PREFIX + Path(n).stem + ".json" not in records}}
    if orphans and REQUIRE_COMPLETE:
        raise RuntimeError(f"{{len(orphans)}} raw outputs without a task record")
    return prefix, config_bytes, config, records, raws, terminal


chosen = {{}}
for half, pattern in HALF_PATTERNS.items():
    candidates = sorted(INPUT_ROOT.rglob(pattern))
    if not candidates:
        raise RuntimeError(f"Half {{half.upper()}}: no {{pattern}} found under {{INPUT_ROOT}}. "
                           f"Attach dataset granite-stage-07{{half}}-ckpt.")
    best = None
    for path in candidates:
        try:
            result = read_half(path)
        except (RuntimeError, OSError, ValueError, BadZipFile) as error:
            print(f"Half {{half.upper()}}: ignored {{path}}: {{error}}")
            continue
        print(f"Half {{half.upper()}}: {{path.name}} -> {{result[5]}} terminal tasks, {{len(result[3])}} records")
        if best is None or result[5] > best[1][5]:
            best = (path, result)
    if best is None:
        raise RuntimeError(f"Half {{half.upper()}}: no usable checkpoint ZIP")
    chosen[half] = best
    if REQUIRE_COMPLETE and best[1][5] != EXPECTED_TASKS_PER_HALF:
        raise RuntimeError(f"Half {{half.upper()}} has {{best[1][5]}}/{{EXPECTED_TASKS_PER_HALF}} tasks finished. "
                           "Finish that half first (resume Notebook 07" + half + " with its latest checkpoint).")

(path_a, (prefix_a, config_bytes_a, config_a, records_a, raws_a, terminal_a)) = chosen["a"]
(path_b, (prefix_b, config_bytes_b, config_b, records_b, raws_b, terminal_b)) = chosen["b"]
if config_a != config_b:
    differing = sorted(k for k in set(config_a) | set(config_b) if config_a.get(k) != config_b.get(k))
    raise RuntimeError("The two halves were generated under different configurations (fields: "
                       + ", ".join(differing) + "). They must not be merged.")
overlap = {{Path(n).stem for n in records_a}} & {{Path(n).stem for n in records_b}}
if overlap:
    raise RuntimeError(f"{{len(overlap)}} tasks appear in both halves, for example {{sorted(overlap)[:3]}}")
if len(records_a) > EXPECTED_TASKS_PER_HALF or len(records_b) > EXPECTED_TASKS_PER_HALF:
    raise RuntimeError("A half contains more tasks than its share")

merged_records = {{**records_a, **records_b}}
merged_raws = {{**raws_a, **raws_b}}
terminal_total = terminal_a + terminal_b
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
output = OUTPUT_DIRECTORY / f"stage07_main_checkpoint_{{terminal_total:04d}}_of_{{TOTAL_TASKS:04d}}.zip"
with tempfile.NamedTemporaryFile(dir=OUTPUT_DIRECTORY, suffix=".tmp", delete=False) as stream:
    temporary = Path(stream.name)
try:
    with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=3) as archive:
        archive.writestr(prefix_a + CONFIG_MEMBER, config_bytes_a)
        for relative in sorted(merged_records):
            archive.writestr(prefix_a + relative, merged_records[relative])
        for relative in sorted(merged_raws):
            archive.writestr(prefix_a + relative, merged_raws[relative])
    with ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("merged ZIP failed its integrity test")
        names = archive.namelist()
        if len(set(names)) != len(names):
            raise RuntimeError("merged ZIP has duplicate members")
    temporary.replace(output)
finally:
    temporary.unlink(missing_ok=True)

REPORT = {{
    "status": "PASS", "run_fingerprint": config_a["run_fingerprint"],
    "half_a": {{"file": path_a.name, "sha256": sha256_file(path_a), "terminal_tasks": terminal_a}},
    "half_b": {{"file": path_b.name, "sha256": sha256_file(path_b), "terminal_tasks": terminal_b}},
    "merged": {{"file": output.name, "sha256": sha256_file(output), "terminal_tasks": terminal_total,
               "task_records": len(merged_records), "raw_outputs": len(merged_raws)}},
    "complete": terminal_total == TOTAL_TASKS,
}}
(OUTPUT_DIRECTORY.parent / "merge_report.json").write_text(json.dumps(REPORT, indent=2) + "\\n", encoding="utf-8")
print(json.dumps(REPORT, indent=2))
print()
print("MERGE:", "COMPLETE" if REPORT["complete"] else "PARTIAL", f"({{terminal_total}}/{{TOTAL_TASKS}} tasks)")
print("Download", output.name, "from Output and publish it as dataset granite-stage-07-ckpt.")
'''

nb = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": MERGE_MD.splitlines(keepends=True)},
        {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
         "source": MERGE_CODE.splitlines(keepends=True)},
    ],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4, "nbformat_minor": 5,
}
out = DST / "4c_Notebook_07m_Merge_Checkpoints" / "Notebook 07m Merge checkpoints (Granite).ipynb"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", out)
