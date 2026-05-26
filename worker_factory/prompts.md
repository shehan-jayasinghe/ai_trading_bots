# Factory prompts (drafts)

Use with Bedrock in Phase 3–4. Version via git.

## Triage

Input: FailureBundle JSON, short platform context (which service failed).

Output (GitHub comment): **Component**, **Severity**, **Likely cause**, **Suggested files**, **Next steps**. Do not invent log lines.

## Fix

Output **only** a unified diff. Allowlisted paths only; no secrets. Minimal fix for `scenario_id`. Empty diff + `<!-- cannot fix: reason -->` if unsure.

## PR summary

Title + body: CI link, S3 prefix, scenario_id, what failed, what changed, how to verify, risks.
