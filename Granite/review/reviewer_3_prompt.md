You are Reviewer 3 in a blinded review of LLM-generated API test assertions.
You adjudicate ONLY the 59 claims on which Reviewer 1 and Reviewer 2 gave different labels. Please work alone and do not discuss your labels with anyone, including the other reviewers.

FILES (unzip stage_08_main_adjudication_packet.zip)
- Fill in ONLY: reviewer_3_template.csv (59 rows).
- prior_decisions.jsonl: for each blind_claim_id, the label and reasoning from Reviewer 1 and from Reviewer 2. Use them as input, you may agree with either or choose a different label.
- context_bundle.jsonl: one JSON object per claim, keyed by blind_claim_id.
- test_context.jsonl: the generated test source, looked up by test_context_id.
- specification_context.jsonl: the OpenAPI document, looked up by spec_context_id.
- REVIEW_INSTRUCTIONS.md: the same rules as this message.

FOR EACH ROW in reviewer_3_template.csv
1. Find the same blind_claim_id in context_bundle.jsonl. Read normalized_claim and source_span, plus line and column in the test.
2. Read both earlier decisions in prior_decisions.jsonl.
3. Open the test (test_context_id) and the OpenAPI spec (spec_context_id). Work out what scenario and inputs the assertion applies to.
4. If reachability is REACHED, use reached_case_evidence to see what was actually sent and returned. Otherwise judge from the spec and the test alone.
5. Choose exactly one final label:
   supported: the spec justifies the expectation.
   contradicted: the spec conflicts with the expectation.
   undocumented_or_unsupported: the expectation is clear, but the spec does not establish it.
   ambiguous_or_unverifiable: a needed value, scenario or rule cannot be resolved from the evidence.
6. Fill in these columns:
   label: one of the four strings above, spelled exactly.
   reasoning: one or two sentences. Never leave it empty.
   requirement_id + evidence_pointer: required for supported and contradicted. Copy BOTH from the SAME entry in that claim's candidate_evidence list. evidence_pointer is that entry's source_pointer, character for character. For the other two labels, leave both blank.
   If no candidate_evidence entry fits a claim you would call supported or contradicted, use undocumented_or_unsupported or ambiguous_or_unverifiable instead.
   adjudication_status: change NOT_REQUIRED to COMPLETED on EVERY row, including the ones you label ambiguous.
7. Leave reviewer_id (reviewer_3) and blind_claim_id exactly as they are.

DO NOT
- add, remove, rename or reorder columns, or add or delete rows
- try to guess which prose style produced a test; just judge the claim

RETURN
All 59 rows must be filled. Save as CSV UTF-8 and name it exactly: reviewer_3_completed.csv
(In Excel choose "CSV UTF-8 (Comma delimited)".)
