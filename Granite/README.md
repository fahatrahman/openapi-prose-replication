# Granite run: `ibm-granite/granite-3.3-8b-instruct`

Revision `51dd4bc2ade4059a6bd87649d68aa11e4fb2529b` (public, Apache-2.0). Main run only (850 operation pairs). Sampling settings, output cap (12,288 new tokens), prompts, L0/L1 pairs, oracles, evaluator and statistics are those of the other two runs. One protocol setting differs.

## The one protocol change: input budget 5,120 to 5,376 tokens

No prompt may be truncated or exceed the input budget. Granite's tokenizer counts the same prompts differently. Measured on all 1,700 frozen prompts with Granite's chat template:

| | Granite | Llama |
|---|---|---|
| Longest prompt (tokens) | 5,247 | 5,107 |
| Prompts over 5,120 | 7 (all L1, 7 different operations) | 0 |
| Mean tokens | 1,870 | 1,790 |

Notebook 06 stops on any prompt over the budget, and dropping the seven pairs would change the frozen sample. The Granite notebooks therefore use 5,376 input tokens (17,664 total). All prompts fit and none is altered. Every pair still has more L1 tokens than L0 tokens. Per-prompt counts are in `verification/granite_prompt_token_counts.csv`.

Because the pilot used 5,120, notebook 11's check that main and pilot generation settings match compares decoding, data type, sampling and output cap, but not the two token budgets.

## Notebooks

| File | Purpose | Outputs |
|---|---|---|
| `notebooks/00p_fp16_preflight.ipynb` | Optional float16 safety check | cleared |
| `notebooks/00_protocol_runtime.ipynb` | Protocol freeze and runtime qualification | cleared |
| `notebooks/00b_reexport_stage_00.ipynb` | Re-export of the stage 00 release | cleared |
| `notebooks/06_main_freeze_tasks.ipynb` | Frozen tasks and prompts | cleared |
| `notebooks/07a_main_generation_first_half.ipynb` | Generation, tasks 1 to 850 | cleared |
| `notebooks/07b_main_generation_second_half.ipynb` | Generation, tasks 851 to 1700 | cleared |
| `notebooks/07m_merge_checkpoints.ipynb` | Checks and merges the two halves | cleared |
| `notebooks/07_main_final_package.ipynb` | Finishes any remaining task and packages stage 07 | cleared |
| `notebooks/08_main_evaluation_session1.ipynb` | Evaluation, creates the blinded review packets | executed |
| `notebooks/08_main_evaluation_session2.ipynb` | Reads reviewers 1 and 2, creates the adjudication packet | executed |
| `notebooks/08_main_evaluation_session3.ipynb` | Adds the adjudication and finishes stage 08 | cleared |
| `notebooks/11_main_report.ipynb` | Main report | cleared |

Generation was split into two halves that share one task ledger and run fingerprint; each L0/L1 pair stays in the same half.

Notebook 11 also needs the stage 05 main release and the stage 10 patch from [`../Qwen/findings/`](../Qwen/findings/) (folders `12_main_stage_05_oracle_review` and `11_main_stage_10_corrected_sample_plan`), and the pilot releases from the pilot folders `06_` to `10_` of [`../Qwen/findings/`](../Qwen/findings/) together with pilot stages 03 to 05. It compares Granite with the Qwen pilot.

## Results

| Folder | Content |
|---|---|
| `results/stage_00/`, `results/stage_00_provenance/` | Runtime and protocol releases |
| `results/stage_06/` | Frozen tasks |
| `results/stage_07/` | Generated tests and raw outputs |
| `results/stage_08/` | Evaluation evidence and completed claim reviews |
| `results/stage_11/` | Main report (`reports/main_report.md` inside the archive) |

## Review files (`review/`)

Blinded packets, the adjudication instructions and the three completed label files. Reviewer 1 labelled all 5,348 claims, reviewer 2 a frozen sample of 300, and reviewer 3 adjudicated the disagreements.

## Verification scripts (`verification/`)

Development checks written while porting the Llama notebooks to Granite: notebook generators and diff, token counting, and CPU tests of the preflight, long-context patch and split-generation logic. They expect the original working-folder layout, so adjust paths before running them.
