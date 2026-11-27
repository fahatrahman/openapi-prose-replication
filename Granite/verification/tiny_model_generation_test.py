import ast, json, time, random, hashlib, types
import torch
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM

tok = AutoTokenizer.from_pretrained("tok")
cfg = AutoConfig.from_pretrained("tok")
print("arch", cfg.architectures, "ctx", cfg.max_position_embeddings, "mults", cfg.embedding_multiplier, cfg.logits_scaling, cfg.residual_multiplier, cfg.attention_multiplier)
cfg.num_hidden_layers = 2; cfg.hidden_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2
cfg.intermediate_size = 256
torch.manual_seed(0)
model = AutoModelForCausalLM.from_config(cfg).to(torch.float32).eval()
print("tiny model", type(model).__name__, sum(p.numel() for p in model.parameters()))

# --- pull generated_continuation out of Notebook 07 cell 7 exactly as shipped
nb = json.load(open("granite_run/4_Notebook_07_Main/Notebook 07 Main (Granite).ipynb"))
src = "".join(nb["cells"][7]["source"])
tree = ast.parse(src)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "generated_continuation"][0]
mod = ast.Module(body=[fn], type_ignores=[])
ns = {"random": random, "time": time, "json": json,
      "module_hash": lambda b: hashlib.sha256(b).hexdigest()}
exec(compile(mod, "nb07_cell7", "exec"), ns)
torch.cuda.synchronize = lambda *a, **k: None   # CPU stand-in only

# --- real settings from the Granite runtime (same as Llama/Qwen) and a real ~5k-token prompt
gs = dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.1, num_beams=1,
          max_input_tokens=5376, max_new_tokens=48, max_total_tokens=5376 + 12288)
rows = json.load(open("granite_token_counts.json"))
big = max(rows, key=lambda r: r["granite"])
import pathlib
root = pathlib.Path("s06/stage_06_main/prose_operation_experiment")
system_template = (root/"config/system_prompt.txt").read_text(); user_template = (root/"config/user_prompt.txt").read_text()
op, cond = big["op_id"], big["condition"]
boundary = hashlib.sha256(f"prose-operation-study|{op}".encode()).hexdigest()[:24]
lp = (root/f"data/prompts/main/{op}/{cond}.txt").read_text()
b = lp.index(f"-----BEGIN OPENAPI {boundary}-----\n") + len(f"-----BEGIN OPENAPI {boundary}-----\n"); e = lp.index(f"\n-----END OPENAPI {boundary}-----")
um = user_template.replace("{BOUNDARY}", boundary).replace("{CANONICAL_OPENAPI_JSON}", lp[b:e])
prompt = tok.apply_chat_template([{"role":"system","content":system_template},{"role":"user","content":um}], tokenize=False, add_generation_prompt=True)
print("rendered head:", repr(prompt[:140])); print("rendered tail:", repr(prompt[-90:]))
assert "Today's Date" not in prompt and "Knowledge Cutoff" not in prompt, "template injected a date!"
assert prompt == tok.apply_chat_template([{"role":"system","content":system_template},{"role":"user","content":um}], tokenize=False, add_generation_prompt=True)
ids = tok.encode(prompt, add_special_tokens=False); print("prompt tokens", len(ids), "(expected", big["granite"], ")"); assert len(ids) == big["granite"]

out1, meta1 = ns["generated_continuation"](model, tok, prompt.encode(), 20261104, gs, torch.device("cpu"))
out2, meta2 = ns["generated_continuation"](model, tok, prompt.encode(), 20261104, gs, torch.device("cpu"))
print("meta", meta1)
assert meta1["generated_token_ids_sha256"] == meta2["generated_token_ids_sha256"], "seeded generation not reproducible"
assert meta1["input_tokens"] == len(ids) and meta1["generated_tokens"] > 0
# over-budget guard behaves
try:
    ns["generated_continuation"](model, tok, prompt.encode(), 1, {**gs, "max_input_tokens": 5120}, torch.device("cpu")); print("GUARD FAILED")
except ValueError as err: print("budget guard OK:", err)
# EOS path: force the tiny model to emit <|end_of_text|> immediately and check finish_reason/pad==eos handling
class Force(torch.nn.Module):
    pass
with torch.no_grad():
    model.lm_head.weight.zero_(); model.lm_head.weight[0] += 5.0   # token 0 = <|end_of_text|> dominates
    # make hidden states non-zero positive so logit for id 0 is largest
    model.model.norm.weight.fill_(1.0)
o3, m3 = ns["generated_continuation"](model, tok, prompt.encode(), 7, {**gs, "repetition_penalty": 1.0, "temperature": 0.7}, torch.device("cpu"))
print("eos-path meta", m3)
print("ALL TINY-MODEL CHECKS DONE")
