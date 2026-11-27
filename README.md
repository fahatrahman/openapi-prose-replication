# Replication package: OpenAPI prose obfuscation and LLM-generated API tests

This package accompanies an anonymous submission. It holds the notebooks and stage outputs of an experiment that asks whether obfuscating the natural-language prose in an OpenAPI operation changes the `pytest` tests a language model generates for it.

- **L0** is the original operation. **L1** is the same operation with obfuscated prose (schema-defined `summary` and `description` fields, obfuscation seed 42).
- The main run covers **850 operation pairs** (1,700 generation tasks) per model. A pilot of 100 pairs was run with Qwen only.
- The stage 11 reports describe the main results as **exploratory**; the registered confirmatory run was not completed.

## Models

| Where | Model | Revision | Input budget |
|---|---|---|---|
| [`Qwen/`](Qwen/) | `Qwen/Qwen2.5-Coder-7B-Instruct` | `c03e6d358207e414f1eca0bb1891e29f1db0e242` | 5,120 tokens |
| [`Llama/`](Llama/) | `meta-llama/Llama-3.1-8B-Instruct` | `0e9e39f249a16976918f6564b8830bc894c89659` | 5,120 tokens |
| [`Granite/`](Granite/) | `ibm-granite/granite-3.3-8b-instruct` | `51dd4bc2ade4059a6bd87649d68aa11e4fb2529b` | 5,376 tokens (see its README) |

The Qwen run was done first. Its notebooks `00` to `16` are in `Qwen/notebooks/` and its stage outputs in `Qwen/findings/`; the stages that do not depend on a model (01 to 05 and 10) were produced once and are reused by the Llama and Granite runs.

Shared generation settings: sampling with temperature 0.7, top-p 0.8, top-k 20, repetition penalty 1.1, one beam, generation seed 20261104, float16, at most 12,288 new tokens, one sample per condition.

## Where to look first

| Question | File |
|---|---|
| Main results for Qwen | `Qwen/findings/16_main_stage_11_final_results/stage_11_main.zip`, file `reports/main_report.md` (also `primary_results.csv`, `primary_effects.png`) |
| Main results for Llama and Granite | `<Model>/results/stage_11/stage_11_main.zip` |
| Generated tests and raw outputs | the `stage_07` archive of each model (Qwen: `Qwen/findings/14_main_stage_07_1700_outputs/`) |
| Claim reviews and agreement | the `stage_08` archive of each model, and `<Model>/review/` (Qwen: `Qwen/findings/15_main_stage_08_evaluation_and_review/`) |
| Prompts and system prompt | the `stage_00` archive of each model (`config/`) and the `stage_06` archive |
| L0 and L1 inputs | `Qwen/findings/` folders `02` to `05` and each model's `stage_06` archive |
| Qwen results as a spreadsheet | `Qwen/findings/16_main_stage_11_final_results/stage_11_results_summary.xlsx` |

## Layout

```
README.md            this file
ANONYMIZATION.md     what was changed in these copies, with checksums
FILES.sha256         SHA-256 of every file in this package
Qwen/                the Qwen run and the shared pipeline
  notebooks/         notebooks 00-16 in pipeline order (executed, outputs kept)
  findings/          stage outputs, one folder per notebook
Llama/               notebooks, results, review files
Granite/             notebooks, results, review files, verification scripts
large_files/         archives above GitHub's 100 MB limit (not tracked by git)
```

## Pipeline stages (Qwen run and shared pipeline)

| Notebook | Stage | Content | Outputs in `Qwen/findings/` |
|---|---|---|---|
| 00 | 00 | Protocol and runtime freeze | `00_stage_00_protocol_runtime` |
| 01 | 01 | Corpus preparation | `01_stage_01_corpus_preparation` |
| 02 | 02 | Operation slicing and prose measurement | archive in `large_files/` |
| 03 | 00 to 02 | Re-export of verified provenance | `03_reexport_stage_00_to_02_provenance` |
| 04 | 03 | Matched L0/L1 inputs and evaluator feasibility | manifest in `04_...`, archive in `large_files/` |
| 05 | 04 | Strata and selection | `05_stage_04_strata_and_sample_freeze` |
| 06 | 05 (pilot) | Test oracles | `06_pilot_stage_05_reviewed_oracles` |
| 07 | 06 (pilot) | Frozen task and prompt ledger | `07_pilot_stage_06_evaluator_and_tasks` |
| 08 | 07 (pilot) | Test generation (GPU) | `08_pilot_stage_07_model_outputs` |
| 09 | 08 (pilot) | Offline evaluation and claim review | `09_pilot_stage_08_corrected_review` |
| 10 | 09 (pilot) | Adjudication and rescoring | `10_pilot_stage_09_adjudicated` |
| 11 | 10 | Power qualification and protocol amendment | `11_main_stage_10_corrected_sample_plan` |
| 12 | 05 (main) | Test oracles | `12_main_stage_05_oracle_review` |
| 13 | 06 (main) | Frozen task and prompt ledger | `13_main_stage_06_evaluator_and_tasks` |
| 14 | 07 (main) | Test generation (GPU) | `14_main_stage_07_1700_outputs` |
| 15 | 08 (main) | Offline evaluation and blinded claim review | `15_main_stage_08_evaluation_and_review` |
| 16 | 11 | Main report | `16_main_stage_11_final_results` |

The Llama and Granite runs repeat stages 00 and 06 to 08 and 11 with their own models; see their READMEs.

## Running the notebooks

The notebooks were written for Kaggle. Each stage reads the previous stages as attached datasets and checks their SHA-256 manifests.

- CPU is enough for every stage except generation (07) and the runtime qualification (00), which used two T4 GPUs.
- Package versions recorded for generation: `torch 2.11.0+cu130`, `transformers 5.20.2`, `tokenizers 0.23.3`, `accelerate 1.15.0`, `safetensors 0.8.0`, `huggingface-hub 1.33.0`, `PyYAML 6.0.3`. The full lock file is in the stage 00 archive (`config/requirements.lock.txt`).
- Input paths contain placeholder account names (`anonuser...`). Point them at your own dataset locations.
- The corpus is a collection of public OpenAPI documents in the APIs.guru directory layout. It is not included separately; the stage 01 and 02 archives contain the processed documents.
- Because account names were replaced, some archives no longer match the checksums recorded inside the original pipeline, so a notebook's integrity check can stop on them. See [`ANONYMIZATION.md`](ANONYMIZATION.md).
- Llama 3.1 is a gated model on Hugging Face and needs your own access token.

## Not included

Reviewer blinding keys, private operator checkpoints, intermediate generation checkpoints and duplicate upload bundles are not part of this package. No access tokens or credentials are included. The stage 02 provenance archive (about 739 MB) is not included either.

The corpus documents contain example e-mail addresses and example keys written by the API publishers. They are part of the public input data.
