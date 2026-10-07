PUBLICATION EVIDENCE GATE

Purpose
Every new or changed article after the baseline commit needs a review receipt
in quality/reviews/<slug>.json. The deployment workflow blocks before Hugo and
GitHub Pages if evidence is absent, stale or incomplete. Existing unchanged
articles are not declared reviewed. The baseline must not be advanced merely
to bypass a failed check. A later push is checked against the same baseline,
so cancelling an earlier failed workflow cannot skip its article changes.

Author/reviewer workflow
1. Finish the article, its schema and its cover. Do not inflate word count.
2. Run: python3 tools/publication_gate.py inventory --slug <slug>
3. Review the full document against current primary sources. Inventory flags
   numeric, model/version, price and benchmark blocks; it is not an exhaustive
   semantic fact checker. Correct title, tables, conclusions, schema and cover.
4. Use an existing receipt as the JSON shape, not as an approval to copy.
   Record article/schema/cover SHA256, reviewer identity, review timestamp,
   primary source IDs/URLs/check times, seven checks and commercial status.
   Every inventory block requires its exact hash, kind, sources and a specific
   rationale. Classify calculations and procedures honestly. First-party tests
   require a repository-local sanitized run record, hash and methodology.
   Do not label a new performance claim as a correction to bypass evidence.
5. Run: python3 tools/publication_gate.py check --slug <slug>
6. Build, commit only the intended files and the review receipt, then deploy.
7. After the matching Deploy Hugo AND Pages deployments succeed, run:
   python3 tools/publication_gate.py verify-live --slug <slug>
     --rendered public --commit <intended-main-sha> --output <local-result.json>
   This compares canonical URL, heading, description, full article text,
   links, schema and cover with the local reviewed build. HTTP 200 alone is
   insufficient. A result from an old document hash is not reusable.
8. Only then mark publication complete and update runtime bookkeeping.

Receipt checks: numbers, model_ids, pricing, dates_versions, benchmarks,
sponsorship, cover. Every check needs pass/not_applicable and a rationale.
Claim kinds: source, calculation, procedure, correction, scope,
first_party_test. Factual source claims require linked primary evidence.
Paid placements need the exact visible disclosure and explicit sponsored or
nofollow attributes on destination links. Keep private email/payment details
and credentials out of public receipts and run records.

Limits
An approved receipt is the reviewer's attestation. The program verifies its
coverage, hashes and structure; it does not establish that an external source
is true or a reviewer has interpreted it correctly. No script auto-approves
drafts. No GA4 authorization, email, link submission or external posting is
performed by this validator.
