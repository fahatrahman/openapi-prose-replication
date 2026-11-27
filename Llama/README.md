# Llama run: `meta-llama/Llama-3.1-8B-Instruct`

Revision `0e9e39f249a16976918f6564b8830bc894c89659`. Main run only (850 operation pairs). Prompts, sampling settings and token budgets are those of the Qwen main run. The model is gated on Hugging Face.

## Notebooks

| File | Purpose | Outputs |
|---|---|---|
| `notebooks/00_protocol_runtime.ipynb` | Protocol freeze and runtime qualification | cleared |
| `notebooks/00b_reexport_stage_00.ipynb` | Re-export of the stage 00 release | cleared |
| `notebooks/06_main_freeze_tasks.ipynb` | Frozen tasks and prompts | cleared |
| `notebooks/07_main_generation.ipynb` | Generation (GPU), stops itself after 10 h 15 min and resumes from a checkpoint | cleared |
| `notebooks/08_main_evaluation_session1.ipynb` | Evaluation, creates the blinded review packets | executed |
| `notebooks/08_main_evaluation_session2.ipynb` | Reads reviewers 1 and 2, creates the adjudication packet | executed |
| `notebooks/08_main_evaluation_session3.ipynb` | Adds the adjudication and finishes stage 08 | executed |
| `notebooks/11_main_report.ipynb` | Main report | executed |

"Cleared" means the notebook is included as source only. Its results are in the matching `results/` folder.

Notebook 11 also needs the stage 05 main release and the stage 10 patch from [`../Qwen/findings/`](../Qwen/findings/) (folders `12_main_stage_05_oracle_review` and `11_main_stage_10_corrected_sample_plan`), and the pilot releases from the pilot folders `06_` to `10_` of [`../Qwen/findings/`](../Qwen/findings/) together with pilot stages 03 to 05.

## Results

| Folder | Content |
|---|---|
| `results/stage_00/`, `results/stage_00_provenance/` | Runtime and protocol releases |
| `results/stage_06/` | Frozen tasks |
| `results/stage_07/` | Generated tests and raw outputs |
| `results/stage_08/` | Evaluation evidence and completed claim reviews |
| `results/stage_11/` | Main report (`reports/main_report.md` inside the archive) |

## Review files (`review/`)

Reviewer instructions (`reviewer_*_prompt.*`), the blinded packets, and the three completed label files. Reviewer 1 labelled all 2,823 claims, reviewer 2 a frozen sample of 300, and reviewer 3 adjudicated the 63 disagreements.
