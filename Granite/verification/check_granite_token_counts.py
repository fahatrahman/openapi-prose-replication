import json, hashlib, statistics, sys
from pathlib import Path
from transformers import AutoTokenizer
root = Path("s06/stage_06_main/prose_operation_experiment")
tok = AutoTokenizer.from_pretrained("tok", trust_remote_code=False)
print("class", type(tok).__name__, "vocab", len(tok), "pad/eos/bos", tok.pad_token_id, tok.eos_token_id, tok.bos_token_id)
system_template = (root/"config/system_prompt.txt").read_text(encoding="utf-8")
user_template = (root/"config/user_prompt.txt").read_text(encoding="utf-8")
study = {"study_id": "prose-operation-study"}
selection = json.loads((root/"data/inventory/final_selected_operations.json").read_text())
llama_rows = {(r["op_id"], r["condition"]): r for r in map(json.loads, (root/"data/audits/cell15_prompt_token_ledger.jsonl").read_text().splitlines())}
rows = []
mismatch_llama_text = 0
for op in selection:
    op_id = op["op_id"]
    boundary = hashlib.sha256(f"{study['study_id']}|{op_id}".encode()).hexdigest()[:24]
    for cond in ("L0", "L1"):
        llama_prompt = (root/f"data/prompts/main/{op_id}/{cond}.txt").read_text(encoding="utf-8")
        begin = f"-----BEGIN OPENAPI {boundary}-----\n"
        end = f"\n-----END OPENAPI {boundary}-----"
        b = llama_prompt.index(begin) + len(begin); e = llama_prompt.index(end)
        canon = llama_prompt[b:e]
        user_message = user_template.replace("{BOUNDARY}", boundary).replace("{CANONICAL_OPENAPI_JSON}", canon)
        if user_message not in llama_prompt or system_template not in llama_prompt:
            mismatch_llama_text += 1
        rendered = tok.apply_chat_template([{"role":"system","content":system_template},{"role":"user","content":user_message}], tokenize=False, add_generation_prompt=True)
        ids = tok.encode(rendered, add_special_tokens=False)
        rows.append({"op_id": op_id, "condition": cond, "granite": len(ids), "llama": llama_rows[(op_id, cond)]["prompt_tokens"], "stratum": op.get("stratum")})
print("rows", len(rows), "text mismatches vs Llama prompts:", mismatch_llama_text)
g = [r["granite"] for r in rows]; l = [r["llama"] for r in rows]
print("granite max", max(g), "mean", round(statistics.mean(g)), "llama max", max(l), "mean", round(statistics.mean(l)))
for c in ("L0","L1"):
    gg=[r["granite"] for r in rows if r["condition"]==c]; ll=[r["llama"] for r in rows if r["condition"]==c]
    print(c, "granite max", max(gg), "mean", round(statistics.mean(gg)), "| llama max", max(ll), "mean", round(statistics.mean(ll)), "| ratio mean", round(statistics.mean(a/b for a,b in zip(gg,ll)),3))
for lim in (5120, 5632, 6144, 6656, 7168, 8192):
    over=[r for r in rows if r["granite"]>lim]
    pairs={r["op_id"] for r in over}
    print(f"limit {lim}: prompts over {len(over)}, pairs affected {len(pairs)}")
json.dump(rows, open("granite_token_counts.json","w"))
print("top 5 granite:", sorted(g)[-5:])
print("L1>L0 all pairs:", all(next(r for r in rows if r['op_id']==o and r['condition']=='L1')['granite']>next(r for r in rows if r['op_id']==o and r['condition']=='L0')['granite'] for o in {r['op_id'] for r in rows}))
