#!/usr/bin/env python3
"""Derive the Granite notebooks from the Llama notebooks by exact, asserted string patches.

Every patch must match exactly once, so a changed source notebook fails loudly instead of
silently producing a half-patched notebook. Outputs are cleared so no Llama run output leaks in.
"""
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1])          # .../llama-stage
DST = Path(sys.argv[2])          # output root for the Granite notebooks
INPUT_LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else 5120
MAX_NEW = 12288
TOTAL_LIMIT = INPUT_LIMIT + MAX_NEW

MODEL_ID = "ibm-granite/granite-3.3-8b-instruct"
REVISION = "51dd4bc2ade4059a6bd87649d68aa11e4fb2529b"
LLAMA_ID = "meta-llama/Llama-3.1-8B-Instruct"
LLAMA_REV = "0e9e39f249a16976918f6564b8830bc894c89659"

# Optional-token block used by Notebooks 06 and 07 (the Granite model is public, not gated).
LLAMA_TOKEN_BLOCK_06 = (
    "# LLAMA RUN: Llama-3.1-8B-Instruct is gated. Expose the Kaggle secret HF_TOKEN (the same secret Notebook 00 reads) to huggingface_hub.\n"
    "try:\n"
    "    from kaggle_secrets import UserSecretsClient\n"
    "    os.environ[\"HF_TOKEN\"] = UserSecretsClient().get_secret(\"HF_TOKEN\")\n"
    "except Exception as error:\n"
    "    raise RuntimeError(\"Add the Kaggle secret HF_TOKEN (Add-ons > Secrets, attached to this notebook): the Llama model is gated.\") from error\n"
)
GRANITE_TOKEN_BLOCK = (
    "# GRANITE RUN: ibm-granite/granite-3.3-8b-instruct is public (Apache-2.0, not gated). An HF_TOKEN secret is optional;\n"
    "# when present it only raises Hugging Face rate limits.\n"
    "try:\n"
    "    from kaggle_secrets import UserSecretsClient\n"
    "    os.environ[\"HF_TOKEN\"] = UserSecretsClient().get_secret(\"HF_TOKEN\")\n"
    "except Exception:\n"
    "    pass\n"
)


def src_text(cell):
    return "".join(cell["source"])


def set_src(cell, text):
    lines = text.splitlines(keepends=True)
    cell["source"] = lines


def sub1(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"PATCH FAILED ({label}): expected exactly 1 match, found {n}: {old[:80]!r}")
    return text.replace(old, new)


def patch_cell(nb, idx, patches, label):
    cell = nb["cells"][idx]
    text = src_text(cell)
    for old, new in patches:
        text = sub1(text, old, new, f"{label} cell {idx}")
    set_src(cell, text)


def clear_outputs(nb):
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        cell.get("metadata", {}).pop("execution", None)


def load(rel):
    return json.loads((SRC / rel).read_text(encoding="utf-8"))


def save(nb, rel):
    out = DST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def assert_no_llama(nb, label, allow=()):
    for i, cell in enumerate(nb["cells"]):
        t = src_text(cell)
        for needle in ("meta-llama", "Llama", "LLAMA", "llama", LLAMA_REV[:7]):
            if needle in t and not any(a in t for a in allow):
                raise SystemExit(f"LEFTOVER {needle!r} in {label} cell {i}")


# ---------------------------------------------------------------- Notebook 00
nb = load("1_Notebook_00/Notebook 00 (Llama).ipynb")
patch_cell(nb, 6, [
    (f'MODEL_ID = "{LLAMA_ID}"', f'MODEL_ID = "{MODEL_ID}"'),
    (f'REQUESTED_MODEL_REVISION = "{LLAMA_REV}"', f'REQUESTED_MODEL_REVISION = "{REVISION}"'),
    ("MAX_RENDERED_INPUT_TOKENS = 5120", f"MAX_RENDERED_INPUT_TOKENS = {INPUT_LIMIT}"),
], "NB00")
if INPUT_LIMIT != 5120:
    patch_cell(nb, 11, [("The configured 17,408-token total ", f"The configured {TOTAL_LIMIT:,}-token total ")], "NB00")
    patch_cell(nb, 17, [("frozen 5,120-token limit", f"frozen {INPUT_LIMIT:,}-token limit")], "NB00")
patch_cell(nb, 0, [("Fresh-run release.", "Granite run (ibm-granite/granite-3.3-8b-instruct). Fresh-run release.")], "NB00")
clear_outputs(nb)
assert_no_llama(nb, "NB00")
save(nb, "1_Notebook_00/Notebook 00 (Granite).ipynb")

# --------------------------------------------------------------- Notebook 00b
nb = load("2_Notebook_00b_Reexport_Stage_00/Notebook 00b Re-export Stage 00 (Llama).ipynb")
patch_cell(nb, 0, [
    ("(Llama run)", "(Granite run)"),
    ("completed Llama Stage 00", "completed Granite Stage 00"),
], "NB00b")
patch_cell(nb, 1, [("# LLAMA RUN: only the new Stage 00", "# GRANITE RUN: only the new Stage 00")], "NB00b")
clear_outputs(nb)
assert_no_llama(nb, "NB00b")
save(nb, "2_Notebook_00b_Reexport_Stage_00/Notebook 00b Re-export Stage 00 (Granite).ipynb")

# ---------------------------------------------------------------- Notebook 06
nb = load("3_Notebook_06_Main/Notebook 06 Main (Llama).ipynb")
patch_cell(nb, 1, [
    (LLAMA_TOKEN_BLOCK_06, GRANITE_TOKEN_BLOCK),
    ("# LLAMA RUN: the new Stage 00 replaces", "# GRANITE RUN: the new Stage 00 replaces"),
], "NB06")
patch_cell(nb, 14, [(f'"{LLAMA_REV}"', f'"{REVISION}"')], "NB06")
patch_cell(nb, 15, [("MAX_RENDERED_INPUT_TOKENS = 5120", f"MAX_RENDERED_INPUT_TOKENS = {INPUT_LIMIT}")], "NB06")
clear_outputs(nb)
assert_no_llama(nb, "NB06")
save(nb, "3_Notebook_06_Main/Notebook 06 Main (Granite).ipynb")

# ---------------------------------------------------------------- Notebook 07
nb = load("4_Notebook_07_Main/Notebook 07 Main (Llama).ipynb")
patch_cell(nb, 1, [(LLAMA_TOKEN_BLOCK_06.replace("\n    ", "\n    "), GRANITE_TOKEN_BLOCK)], "NB07")
patch_cell(nb, 2, [("if not 0 < int(task[\"prompt_tokens\"]) <= 5120:",
                    f"if not 0 < int(task[\"prompt_tokens\"]) <= {INPUT_LIMIT}:")], "NB07")
patch_cell(nb, 3, [
    (f'if MODEL_ID != "{LLAMA_ID}":', f'if MODEL_ID != "{MODEL_ID}":'),
    ('RUNTIME["max_total_tokens"] != 17408', f'RUNTIME["max_total_tokens"] != {TOTAL_LIMIT}'),
], "NB07")
patch_cell(nb, 5, [
    ("# Load exact pinned Llama model", "# Load exact pinned Granite model"),
    ("isinstance(x, int) and x >= 17408", f"isinstance(x, int) and x >= {TOTAL_LIMIT}"),
], "NB07")
patch_cell(nb, 6, [("if len(development_ids) > 5120 or not development_ids:",
                    f"if len(development_ids) > {INPUT_LIMIT} or not development_ids:")], "NB07")
clear_outputs(nb)
assert_no_llama(nb, "NB07")
save(nb, "4_Notebook_07_Main/Notebook 07 Main (Granite).ipynb")

# ---------------------------------------------------------------- Notebook 08
nb = load("5_Notebook_08_Main/Notebook 08 Main (Llama).ipynb")
clear_outputs(nb)
assert_no_llama(nb, "NB08")
save(nb, "5_Notebook_08_Main/Notebook 08 Main (Granite).ipynb")

# ---------------------------------------------------------------- Notebook 11
nb = load("6_Notebook_11_Main/Notebook 11 Main (Llama).ipynb")
patch_cell(nb, 2, [("# LLAMA RUN: model_id, model_revision and tokenizer_revision differ from the Qwen pilot by design.",
                    "# GRANITE RUN: model_id, model_revision and tokenizer_revision differ from the Qwen pilot by design.")], "NB11")
if INPUT_LIMIT != 5120:
    patch_cell(nb, 3, [("require(x <= 5120 and y <= 5120 and x > 0 and y > 0,",
                        f"require(x <= {INPUT_LIMIT} and y <= {INPUT_LIMIT} and x > 0 and y > 0,")], "NB11")
    patch_cell(nb, 2, [(
        'generation_keys = ("decoding", "dtype", "generation", "max_input_tokens", "max_new_tokens",\n                   "max_total_tokens")',
        'generation_keys = ("decoding", "dtype", "generation", "max_new_tokens")  # GRANITE RUN: input/total token budgets are tokenizer-specific',
    )], "NB11")
clear_outputs(nb)
assert_no_llama(nb, "NB11")
save(nb, "6_Notebook_11_Main/Notebook 11 Main (Granite).ipynb")

print("OK limit", INPUT_LIMIT, "total", TOTAL_LIMIT)
