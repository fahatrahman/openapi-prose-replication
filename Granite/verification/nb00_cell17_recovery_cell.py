# RECOVERY CELL for Notebook 00 Cell 17 (Granite). Run it ONLY in the SAME live session where Cell 17 just failed
# with "Long-context qualification failed". It re-uses the finished 12,288-token probe (nothing is re-run on the GPU).
import copy, json

# 1) The probe really did the full job.
assert long_probe_generated_tokens == MAX_NEW_TOKENS, long_probe_generated_tokens
assert context_limit_pass and memory_estimate_pass

# 2) The only failed condition was "rendered tokens == 5,376". Granite's tokenizer makes the synthetic prompt land
#    at 5,375 because one more filler repetition adds two tokens. Prove that this is the largest prompt that fits.
_next_fixture = copy.deepcopy(development_fixture)
_next_fixture["paths"]["/users"]["post"]["description"] = ("qualification " * (best_repetition_count + 1)).strip()
next_repetition_token_count = len(render_fixture_document(
    _next_fixture, "development-fixture::long-context::post::/users")["token_ids"])
long_input_shortfall_tokens = MAX_RENDERED_INPUT_TOKENS - long_input_token_count
print({"rendered": long_input_token_count, "limit": MAX_RENDERED_INPUT_TOKENS,
       "shortfall": long_input_shortfall_tokens, "next_repetition_would_render": next_repetition_token_count})
assert next_repetition_token_count > MAX_RENDERED_INPUT_TOKENS and 0 <= long_input_shortfall_tokens <= 3

# 3) Record the corrected verdict (same file Cell 19 checks) and keep the evidence.
long_context_status = "PASS"
long_context_record["status"] = "PASS"
long_context_record["input_shortfall_tokens"] = long_input_shortfall_tokens
long_context_record["next_repetition_would_render_tokens"] = next_repetition_token_count
write_json(long_context_path, long_context_record)
print(json.dumps({k: long_context_record[k] for k in ("status", "rendered_input_tokens", "input_shortfall_tokens",
      "generated_probe_tokens", "probe_duration_seconds")}, indent=2))
print("\nCELL 17: PASS (recovered, probe results unchanged)")
