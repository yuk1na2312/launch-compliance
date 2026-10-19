# Report template

Write the report to `.launch-compliance/REPORT.md` with this structure. Keep findings short: one line of "what", evidence, one line of "fix". The user will scan it.

```markdown
# LaunchCompliance report — <project name>

_Generated <YYYY-MM-DD> · LaunchCompliance v0.1.0 · This is an automated developer checklist, not legal advice._

## Summary

<One sentence: what the app is and what personal data it handles, from code.>

| Severity | Fail | Partial | Needs input |
|---|---|---|---|
| Critical | n | n | n |
| High | n | n | n |
| Medium | n | n | n |
| Low | n | n | n |

**Launch blockers:** <list Critical IDs, or "None found">

**Assumed audience:** <markets / age> (<"from user" or "assumed: global incl. EU">)

## Data inventory

| Data | Where collected | Where stored | Sent to |
|---|---|---|---|
| Email | signup form `app/signup/page.tsx:11` | `profiles.email` | Supabase, Resend, PostHog |

## Third parties

| Vendor | Purpose | Data sent | Loaded | In privacy policy? |
|---|---|---|---|---|

## Findings

### Critical

#### SEC-01 · Secrets exposed in client code — Fail
- **Evidence:** `lib/supabase.ts:2` uses `NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY` in a client module
- **Risk:** anyone can read and modify every table
- **Fix:** move service-role usage to server-only code, use the anon key on the client, rotate the key in the Supabase dashboard
- **Auto-fixable:** partly (code yes; key rotation is manual)

### High
...

### Medium
...

### Low
...

## Passed
- PRV-xx · <title> — <one-line evidence>

## Not applicable
- SEC-04 · Uploaded files — no file uploads found

## Needs your input
1. Where will your users be? (EU/UK, US, Vietnam, other)
2. Could anyone under 13 (or under 16 in the EU) use the app?
3. Legal business name, address, and contact email to show on the site
4. Are the testimonials on the homepage from real customers with permission?
5. Your refund terms

## Next steps
Reply with check IDs to fix (e.g. `SEC-01 SEC-02 PRV-03`) or "all critical".
```

Rules:
- Order findings by severity, then ID.
- Every Fail/Partial has evidence with a path (and line where possible).
- Mask secrets: variable name plus first 4 characters at most.
- Don't include checks you dropped as false positives.
