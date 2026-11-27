import json, sys
from pathlib import Path

OUT = Path(sys.argv[1])
MODEL_ID = "ibm-granite/granite-3.3-8b-instruct"
REVISION = "51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"

MD = """# Notebook 00p · Granite fp16 preflight (about 15 minutes, optional but recommended)

Run this FIRST, on a fresh Kaggle **GPU T4 x2** session with **Internet on**. No other inputs are needed.
It loads `ibm-granite/granite-3.3-8b-instruct` exactly as Notebook 07 does (float16, two T4s) and checks, before you spend hours in Notebook 00 and 07:

1. the chat template renders deterministically with a system prompt (no date injected) and ends with the assistant header;
2. a 5,300-token chunked prefill (512-token chunks, exactly as Notebook 07) produces only finite activations in fp16 (Granite was trained in bfloat16; T4 GPUs cannot run bfloat16);
3. frozen-setting sampling (temperature 0.7, top-p 0.8, top-k 20, repetition penalty 1.1, chunked prefill) runs without error and is reproducible for a fixed seed;
4. memory and speed, so you can estimate the whole run.

The last cell prints `PREFLIGHT: PASS` or `PREFLIGHT: FAIL` with the reason. Do not continue to Notebook 00 if it fails.
"""

CELL_LOAD = '''import json, os, time, platform
import torch
from huggingface_hub import HfApi
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "%(model)s"
REVISION = "%(rev)s"
MAX_INPUT_TOKENS = 5376
MAX_NEW_TOKENS_PROBE = 96

try:  # optional: the model is public
    from kaggle_secrets import UserSecretsClient
    os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
except Exception:
    pass

assert torch.cuda.is_available() and torch.cuda.device_count() == 2, "Need GPU T4 x2"
for i in (0, 1):
    p = torch.cuda.get_device_properties(i)
    assert "T4" in p.name.upper(), "Expected Tesla T4, found " + p.name
for i in (0, 1):  # a model still loaded from an earlier run of this cell would make the load fail with a false OOM
    free_gib, total_gib = (x / 2**30 for x in torch.cuda.mem_get_info(i))
    assert free_gib > total_gib - 1.0, ("GPU %d already holds %.1f GiB from an earlier run in this session. "
        "Restart the session (Run > Restart session) and run the cells once from the top." % (i, total_gib - free_gib))
info = HfApi().model_info(MODEL_ID, revision=REVISION)
assert info.sha == REVISION, "Unexpected revision " + str(info.sha)

started = time.perf_counter()
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=REVISION, trust_remote_code=False)
model_config = AutoConfig.from_pretrained(MODEL_ID, revision=REVISION, trust_remote_code=False)
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, revision=REVISION, trust_remote_code=False,
    dtype=torch.float16, device_map="auto",
    max_memory={0: "13GiB", 1: "13GiB", "cpu": "20GiB"},
    low_cpu_mem_usage=True,
)
model.eval()
device_map = {str(k): str(v) for k, v in getattr(model, "hf_device_map", {}).items()}
assert device_map and not any(v in ("cpu", "disk") for v in device_map.values()), "Weights were offloaded off-GPU"
assert {v for v in device_map.values()} >= {"0", "1"}, "Model is not split across both T4s"
assert next(model.parameters()).dtype == torch.float16
input_device = model.get_input_embeddings().weight.device
LOAD_SECONDS = round(time.perf_counter() - started, 1)
print({"loaded": True, "seconds": LOAD_SECONDS, "model_class": type(model).__name__,
       "layers": model_config.num_hidden_layers, "ctx": model_config.max_position_embeddings,
       "multipliers": {k: getattr(model_config, k, None) for k in
                       ("embedding_multiplier", "logits_scaling", "residual_multiplier", "attention_multiplier")}})
''' % {"model": MODEL_ID, "rev": REVISION}

CELL_CHECK = '''import statistics

REPORT = {"status": "PASS", "problems": []}


def problem(text):
    REPORT["status"] = "FAIL"
    REPORT["problems"].append(text)
    print("PROBLEM:", text)


SYSTEM = "You generate one executable Python pytest module from the supplied OpenAPI operation."
USER = "Using the OpenAPI operation below, generate a self-contained Python pytest module.\\n{}\\n"

# 1. chat template
msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER.format("{}")}]
a = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
b = tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
if a != b:
    problem("chat template is not deterministic")
if "Today" in a or "Knowledge Cutoff" in a:
    problem("chat template injected a date or default system prompt")
if not a.endswith("<|start_of_role|>assistant<|end_of_role|>"):
    problem("rendered prompt does not end with the assistant header")
if tokenizer.eos_token_id != 0 or tokenizer.pad_token_id != 0:
    problem("unexpected eos/pad ids: %s/%s" % (tokenizer.eos_token_id, tokenizer.pad_token_id))
REPORT["template_tail"] = a[-60:]

# 2. a long prompt close to the frozen budget, with fp16 activation hooks on every decoder layer
snippet = json.dumps({"paths": {"/users/{id}": {"get": {"summary": "Fetch one user by identifier",
    "description": "Returns the stored user record, including contact details and role.",
    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]}}}}, sort_keys=True)
body = ""
while True:
    candidate = tokenizer.apply_chat_template(
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": USER.format(body + snippet)}],
        tokenize=False, add_generation_prompt=True)
    if len(tokenizer.encode(candidate, add_special_tokens=False)) > 5300:
        break
    body += snippet + "\\n"
long_prompt = candidate
long_ids = tokenizer.encode(long_prompt, add_special_tokens=False)
assert len(long_ids) <= MAX_INPUT_TOKENS, "synthetic prompt too long"
REPORT["long_prompt_tokens"] = len(long_ids)

stats, hooks = [], []


def make_hook(index):
    def hook(module, args, output):
        value = output[0] if isinstance(output, (tuple, list)) else output
        stats.append((index, bool(torch.isfinite(value).all().item()), float(value.float().abs().max().item())))
    return hook


for index, layer in enumerate(model.model.layers):
    hooks.append(layer.register_forward_hook(make_hook(index)))
ids = torch.tensor([long_ids], dtype=torch.long, device=input_device)
# Same path as Notebook 07: generate() with chunked prefill (512 tokens). A one-shot 5,300-token forward would
# materialise multi-GiB attention buffers on a 15 GiB T4 and is NOT what the real run does.
logits_finite = False
with torch.inference_mode():
    probe = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=2,
                           do_sample=False, pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id,
                           use_cache=True, prefill_chunk_size=512, cache_implementation="dynamic",
                           return_dict_in_generate=True, output_logits=True)
    logits_finite = all(bool(torch.isfinite(step).all().item()) for step in probe.logits)
    del probe
for h in hooks:
    h.remove()
non_finite_layers = [i for i, ok, _ in stats if not ok]
peak = max(v for _, _, v in stats)
REPORT["fp16_activation_peak_abs"] = round(peak, 1)
REPORT["fp16_max_representable"] = 65504
REPORT["non_finite_layers"] = non_finite_layers
if non_finite_layers or not logits_finite:
    problem("non-finite values in fp16 prefill (layers %s, logits finite=%s)" % (non_finite_layers[:5], logits_finite))
elif peak > 60000:
    problem("fp16 activations within 8%% of overflow (peak %.0f)" % peak)

# 3. frozen-setting sampling, twice with the same seed
settings = dict(do_sample=True, temperature=0.7, top_p=0.8, top_k=20, repetition_penalty=1.1, num_beams=1)


def sample(seed):
    import random
    random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    ids = torch.tensor([long_ids], dtype=torch.long, device=input_device)
    torch.cuda.synchronize(); t0 = time.perf_counter()
    with torch.inference_mode():
        seq = model.generate(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=MAX_NEW_TOKENS_PROBE,
                             pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id,
                             use_cache=True, prefill_chunk_size=512, cache_implementation="dynamic", **settings)
    torch.cuda.synchronize()
    return seq[0, len(long_ids):].tolist(), time.perf_counter() - t0


try:
    g1, t1 = sample(20261104)
    g2, t2 = sample(20261104)
    if g1 != g2:
        problem("same seed produced different tokens")
    if not g1:
        problem("no tokens generated")
    REPORT["generated_tokens"] = len(g1)
    REPORT["seconds_for_5k_prompt_plus_%d_tokens" % MAX_NEW_TOKENS_PROBE] = round(statistics.mean([t1, t2]), 2)
    REPORT["sample_text"] = tokenizer.decode(g1[:60], skip_special_tokens=True)
except Exception as error:
    problem("generation raised %s: %s" % (type(error).__name__, str(error)[:300]))

REPORT["gpu_memory_gib"] = [{"index": i, "peak_allocated": round(torch.cuda.max_memory_allocated(i) / 2**30, 2),
                             "peak_reserved": round(torch.cuda.max_memory_reserved(i) / 2**30, 2)} for i in (0, 1)]
# 3b. project the peak memory at the full frozen length (5,376 input + 12,288 new = 17,664 tokens).
# The probe above only grew the KV cache to about prompt + MAX_NEW_TOKENS_PROBE tokens; the real run grows it to 17,664.
layers_on = {0: 0, 1: 0}
for _name, _dev in device_map.items():
    if _name.startswith("model.layers."):
        layers_on[int(_dev)] += 1
kv_bytes_per_token_per_layer = 2 * model_config.num_key_value_heads * (model_config.hidden_size // model_config.num_attention_heads) * 2
reached = len(long_ids) + MAX_NEW_TOKENS_PROBE
extra_tokens = 5376 + 12288 - reached
projected = []
for i in (0, 1):
    extra_gib = layers_on[i] * kv_bytes_per_token_per_layer * extra_tokens / 2**30
    projected.append(round(torch.cuda.max_memory_reserved(i) / 2**30 + extra_gib + 0.3, 2))  # 0.3 GiB allocator slack
REPORT["layers_per_gpu"] = layers_on
REPORT["projected_peak_reserved_gib_at_17664_tokens"] = projected
REPORT["t4_usable_gib"] = round(min(torch.cuda.get_device_properties(i).total_memory for i in (0, 1)) / 2**30, 2)
if max(projected) > REPORT["t4_usable_gib"] - 0.2:
    problem("projected GPU memory at full length %s GiB does not fit a T4 (%s GiB). Do not start Notebook 07." % (projected, REPORT["t4_usable_gib"]))
REPORT["load_seconds"] = LOAD_SECONDS
print(json.dumps(REPORT, indent=2))
print("\\nPREFLIGHT: " + REPORT["status"])
'''

nb = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": MD.splitlines(keepends=True)},
        {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": CELL_LOAD.splitlines(keepends=True)},
        {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": CELL_CHECK.splitlines(keepends=True)},
    ],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4, "nbformat_minor": 5,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("written", OUT)
