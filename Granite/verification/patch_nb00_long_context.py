"""Documents the one change made to Notebook 00 (Granite) after the first real Kaggle run.
Cell 17 required the synthetic long prompt to be EXACTLY 5,376 tokens. With Granite's tokenizer one repeated filler
word adds two tokens, so the largest prompt that fits is 5,375 and the check failed after the 75-minute probe.
New rule: exact, or (one more repetition would exceed the limit AND the shortfall is at most 3 tokens).
The patch itself is already applied in '1_Notebook_00/Notebook 00 (Granite).ipynb' (cell 17); the recovery cell for a
live session that already failed is in nb00_cell17_recovery_cell.py."""
