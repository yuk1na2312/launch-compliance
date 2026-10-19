# Contributing to LaunchCompliance

Thanks for helping. The project has two halves that must stay in sync:

1. **The detector** (`plugins/launch-compliance/skills/audit/scripts/detect_signals.py`) finds candidate signals. Standard library only, Python 3.8+.
2. **The references** (`plugins/launch-compliance/skills/audit/references/`) tell Claude how to verify and fix each check.

## Adding a vendor

Add a tuple to `VENDORS`: display name, kind (an existing signal such as `analytics`, `payments`, `ai`), a regex for dependency names (anchored as a full match), and an optional regex for code (script URLs, init calls). If the kind is new, map it to checks in `CHECKS` and document it in `references/signals.md`.

## Adding a check

1. Pick the next ID in its category (`PRV-14`, `CON-06`, ...).
2. Add it to `CHECKS` with its trigger signals, default severity, and an optional "present" signal or legal page key.
3. Add any new code signals to `CODE_SIGNALS`.
4. Write the entry in the matching `references/checks-*.md` using the same four headings: **Why**, **Verify**, **Pass when**, **Fix**.
5. Add a case to `examples/` that triggers it and confirm the scanner reports it:

```bash
python3 plugins/launch-compliance/skills/audit/scripts/detect_signals.py examples/vibe-app --md > /dev/null
```

6. Update the table in `README.md`.

## Writing guidance

- Keep "Why" factual and cite the kind of rule (e.g. "EU consumer law", "CAN-SPAM") rather than quoting statutes. Laws change; prefer wording that tells users what to confirm.
- Fixes should match the project's existing stack and avoid new dependencies when a few lines will do.
- Anything that changes business decisions (prices, refunds, deleting data, removing reviews) must say "ask the user first".

## Validating the plugin

```bash
claude plugin validate .
claude plugin validate ./plugins/launch-compliance
```
