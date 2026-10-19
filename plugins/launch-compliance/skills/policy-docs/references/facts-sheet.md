# Facts sheet

Fill this from verified code evidence before drafting. Keep the evidence column; it lets the user re-check the policy when code changes. Save the filled sheet as `.launch-compliance/facts.md`.

## Operator (from user)
- Legal name:
- Country of establishment:
- Privacy contact email:
- Postal address (if required):
- Target markets:
- Minimum user age:
- Effective date:

## Data we collect

| Category | Fields | How collected | Purpose | Evidence |
|---|---|---|---|---|
| Account | email, password hash | signup form | create and secure account | `app/signup/page.tsx`, `profiles` table |
| Usage / analytics | page views, device, IP-derived location | analytics SDK | improve product | `posthog-js` in `app/providers.tsx` |
| Payment | handled by processor; we store customer ID | checkout | billing | `stripe` in `app/api/checkout` |
| Content | notes, uploads, prompts | app features | provide the service | `notes` table |

## Recipients / third parties

| Vendor | Role | Data received | Region (if known) | Evidence |
|---|---|---|---|---|

## Cookies and local storage

| Name / provider | Category (necessary / preferences / analytics / marketing) | Purpose | Duration | Evidence |
|---|---|---|---|---|

## Features that change the policy
- Payments: one-time / subscription / free trial
- AI processing: provider, what is sent, whether outputs are stored
- User-generated content: public or private, moderation
- Location, camera, microphone, contacts access (mobile)
- Children: directed at children? (from user)

## User rights mechanisms in code
- Delete account:
- Export data:
- Unsubscribe:
- Cookie settings:
- Correct data (edit profile):

## Retention
| Data | Period | Enforced by |
|---|---|---|

## Security measures (only what's true)
- e.g. hosting provider encryption at rest, HTTPS, RLS policies, hashed passwords via auth provider
