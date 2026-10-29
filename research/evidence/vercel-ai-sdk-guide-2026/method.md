# Method - vercel-ai-sdk-guide-2026 research verification

Run: 2026-10-26, RockB v2.1 research stage, task BLO-4368.

## What was done
1. `curl -L https://ai-sdk.dev/llms.txt` (HTTP 200, 4,937,216 bytes) saved as `ai-sdk-docs-llms.txt`.
2. Split the corpus into per-page markdown (`---\ntitle:` delimiter) and saved the four pages used as sources: migration guide 7.0, 6.0, 5.0, and the `useChat` reference.
3. `curl https://registry.npmjs.org/-/package/ai/dist-tags` -> `npm-dist-tags-ai.json`.
4. `gh api repos/vercel/ai` -> `gh-repo-vercel-ai.json` (stars, license, pushed_at).
5. Built `research/vercel-ai-sdk-guide-2026.json` with a script that asserts every `sources[].excerpt` is an exact substring of the saved file.

## What was NOT done here
This stage collected the sources above only. The compile matrix in `original_evidence_plan` was not executed in the research stage (stage time limit); it was executed later in the same task during the write stage, and its artifacts are in this directory: `run_matrix.sh` (the script), `results/summary.jsonl`, the per-file `results/v*.log` tsc outputs and `results/matrix.json` (machine-readable summary, with `executed_at_utc`). See `README.md` for the run environment, exact installed versions and the explicit list of things the matrix did not exercise.

What was never done, by either stage: no provider or model call (no API key was used), no runtime execution, no bundler build, no React or Next.js render. Every snippet statement in the article is a `tsc --noEmit` result.

## Reproduction
Re-run the four fetches above; page content is versioned by the vendor, so re-check `dist-tags` before quoting a version. For the compile results, run `bash run_matrix.sh` (needs network access to the npm registry) and compare `results/matrix.json`.
