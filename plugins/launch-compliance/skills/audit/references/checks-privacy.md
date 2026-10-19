# Privacy and data protection checks (PRV)

Each check: **Why**, **Verify**, **Pass when**, **Fix**. Severity is the default; Phase 3 of SKILL.md adjusts it.

---

## PRV-01 Privacy policy — Critical

**Why.** Nearly every privacy law (GDPR, UK GDPR, CCPA/CPRA, Vietnam's personal data protection law, CalOPPA) requires a clear notice when you collect personal data. App stores and payment providers also require a link. Collecting emails through auth is enough to need one.

**Verify.**
- Find the page: routes/files named `privacy`, footer links, links in signup forms, or an external URL (Termly, iubenda, Notion).
- If it exists, read it and compare with what the code actually does: data fields stored (schema/migrations/models), third parties from `signals.json`, cookies set, AI providers, analytics, payment processor, where data is hosted.

**Pass when** a policy is linked from every page (footer) and every data-collection point, and it covers: who you are and how to contact you; what data you collect (matching the schema); why (purposes) and, for EU users, the legal basis; who receives it (every third party found in code); international transfers; retention; user rights and how to exercise them; children; cookies; last-updated date.

**Fix.** Generate a draft with the `policy-docs` skill from the verified data inventory. Add a `/privacy` route in the project's routing style and link it from the footer, signup, and any email-capture form.

---

## PRV-02 Cookie policy — High

**Why.** EU/UK ePrivacy rules require telling users which cookies and similar technologies (localStorage, pixels, SDK identifiers) you use and why.

**Verify.** List every cookie and storage key set by the app (`document.cookie`, `cookies().set`, `res.cookie`, auth libraries' session cookies, `localStorage.setItem`) and by each third party (analytics, ads, chat widgets, Stripe.js fraud cookies).

**Pass when** a cookie section or page lists categories (strictly necessary, preferences, analytics, marketing), each cookie or provider, purpose, and duration; and it is reachable from the consent banner.

**Fix.** Generate from the inventory via `policy-docs`. It can be a section of the privacy policy if short.

---

## PRV-03 Consent banner that actually blocks — High (Critical with ads or session replay)

**Why.** In the EU/UK, non-essential cookies and trackers may only load after opt-in consent. A banner that shows while GA or Meta Pixel already fired does not comply. Regulators fine for exactly this.

**Verify.**
- Find where each analytics/ads/replay script is loaded (`<Script>`, `layout`, `_app`, `index.html`, GTM container, SDK `init` calls).
- Check whether loading is conditional on a stored consent value. Check that "Reject" is as easy as "Accept" (same layer, same prominence) and consent can be withdrawn later (a footer "Cookie settings" link).
- Cookieless analytics (Plausible, Umami, Vercel Analytics in default mode) usually don't need consent under the ePrivacy cookie rule; note it rather than failing.

**Pass when** no non-essential script, pixel, or SDK initializes before opt-in; reject is one click; preferences can be changed later; consent choice is stored with a timestamp.

**Fix.** Either add a lightweight consent component (prefer an existing open-source library that fits the stack, such as vanilla-cookieconsent) or write a small one. Then gate every non-essential `init`/script on consent. For GA4/GTM, set Google Consent Mode defaults to `denied` before the tag loads and update on choice. Add a "Cookie settings" footer link.

---

## PRV-04 Consent and purpose on forms — Medium

**Why.** Forms must say why data is collected; marketing opt-in must be a separate, unticked choice (GDPR consent; also many anti-spam laws).

**Verify.** For each form (signup, waitlist, contact, checkout): Is there a purpose line and a privacy link near the submit button? Is marketing consent bundled into the Terms checkbox or pre-ticked? Is a required checkbox forcing newsletter consent?

**Pass when** every form has a short purpose/privacy line; marketing opt-in is optional, unticked, and separate from Terms acceptance; consent is stored (what, when, which text version).

**Fix.** Add the notice line and link. Split checkboxes. Remove `defaultChecked`. Store `marketing_consent_at` (and the policy version) alongside the user.

---

## PRV-05 Data minimization — Medium

**Why.** Collecting fields you don't use increases breach impact and is itself a GDPR violation (Art. 5(1)(c)). Vibe-coded schemas often add DOB, phone, gender, and address "just in case".

**Verify.** For each personal field in forms and schema, search where it is read. A field that is written but never used for a feature is a candidate. Also check `select('*')` responses that send every column to the client.

**Pass when** each personal field has a feature that uses it, or is optional and explained.

**Fix.** Ask the user before removing a field. Then remove it from forms and validation, stop writing it, and add a migration to drop the column (or null it out). Replace `select('*')` with explicit columns in client-facing queries.

---

## PRV-06 Third-party SDK audit and sub-processors — High

**Why.** Every SDK that receives user data is a recipient you must disclose, and for B2B/EU customers often a sub-processor that needs a data processing agreement.

**Verify.** Start from `third_parties` in `signals.json`. For each: what data it receives (read the call sites: what is passed to `identify`, `capture`, `setUser`, prompts sent to AI APIs), whether it's loaded client-side or server-side, and whether the privacy policy names it. Flag SDKs that are installed but unused (remove them).

**Pass when** each third party is necessary, receives only what it needs, is named in the privacy policy (or a linked sub-processor list), and has a DPA where the user's customers will ask for one.

**Fix.** Produce a table (vendor, purpose, data sent, location of call, client/server, policy link) in the report. Remove unused SDKs. Strip unnecessary fields from `identify`/`setUser` calls (e.g. send a user ID, not email). Add the list to the privacy policy.

---

## PRV-07 Age gate and children's data — High (needs input)

**Why.** US COPPA requires verifiable parental consent before collecting data from children under 13; GDPR sets the age of digital consent at 13–16 depending on the country; Vietnam's rules require parental consent for children's data. Apps aimed at or likely used by children have stricter rules.

**Verify.** Determine the audience: marketing copy, onboarding, and any "kids/students/school" signals. Check for a DOB or age field and what happens for under-age input.

**Pass when** either (a) the user confirms the app is not directed at children, the terms state a minimum age, and signup does not collect DOB unnecessarily; or (b) for child-directed apps, there is a parental consent flow and minimal data collection — and you recommend legal review.

**Fix.** Add a minimum-age clause to Terms and a confirmation or age check at signup. If child-directed, flag for legal review; do not attempt to build "verifiable parental consent" casually.

---

## PRV-08 Account and data deletion — High

**Why.** GDPR right to erasure, CCPA right to delete, and both Apple App Store and Google Play require an account deletion path for apps that let users create accounts.

**Verify.** Look for a delete-account UI and the backend handler. Check that it deletes or anonymizes rows in every table keyed to the user, removes files in storage, deletes the auth user (e.g. `auth.admin.deleteUser`), and cancels subscriptions with the payment provider. Check third parties too (analytics person profiles, email lists).

**Pass when** a signed-in user can delete their account from settings (or request it via a documented email), and deletion reaches all stores, with a confirmation step.

**Fix.** Add a "Delete account" section in settings with confirmation; implement a server-side handler using cascading deletes or explicit per-table deletes; cancel the subscription; remove the contact from the email provider; document the process in the privacy policy.

---

## PRV-09 Data access and export — Medium

**Why.** GDPR access and portability rights; CCPA right to know.

**Verify.** Is there an "Export my data" action, or a documented request process (email + response window)?

**Pass when** users can get a copy of their data in a machine-readable format (JSON/CSV), self-serve or on request within the legal window (one month under GDPR).

**Fix.** Add an authenticated endpoint that collects the user's rows across tables into JSON, plus a settings button. For small apps a documented email process is acceptable; put it in the privacy policy.

---

## PRV-10 Data retention — Medium

**Why.** Keeping data forever violates storage limitation and increases breach impact.

**Verify.** Look for TTLs, scheduled cleanup jobs, soft-delete purge, log retention settings, and what happens to inactive accounts, abandoned signups, uploaded files, and AI chat logs.

**Pass when** each data category has a stated retention period in the policy and something enforces it (cron, DB TTL, provider setting).

**Fix.** Ask the user for periods, then add a scheduled job (Supabase `pg_cron`, Vercel cron, Spring `@Scheduled`, etc.) that purges expired data, and state the periods in the policy.

---

## PRV-11 No personal data in logs or error reports — High

**Why.** Logs are rarely access-controlled or deleted. Logging passwords, tokens, or full request bodies is a common leak. Error trackers capture request data and user context by default.

**Verify.** Read each `pii_logging` hit. Check Sentry/Bugsnag config: `sendDefaultPii`, `beforeSend` scrubbing, replay settings. Check backend request logging middleware (e.g. logging full bodies).

**Pass when** no passwords, tokens, payment data, or full request bodies are logged; error tracking scrubs PII or sends only user IDs.

**Fix.** Remove or redact the log statements (log IDs, not values). Configure `beforeSend` scrubbing and keep `sendDefaultPii: false`. Add a small redaction helper if the project logs a lot.

---

## PRV-12 AI provider disclosure — High

**Why.** Sending user content to an AI API is sharing personal data with a third party. Users must be told, and you should know the provider's retention and training terms for API data.

**Verify.** Read each AI call: what user data goes into prompts (names, emails, uploaded documents, chat history)? Is the provider named in the privacy policy? Is there any notice in the UI where users submit content?

**Pass when** the privacy policy names each AI provider and what is sent; prompts contain only what the feature needs; sensitive fields are stripped; the UI tells users their input is processed by AI where it matters.

**Fix.** Strip unnecessary personal fields before the call. Add the provider to the policy. Add a short notice near AI inputs. Note the provider's API data retention setting in the report for the user to confirm.

---

## PRV-13 Session replay masking — High

**Why.** Session replay tools (Hotjar, Clarity, LogRocket, FullStory, PostHog recordings, Datadog RUM replay) can record everything typed, including passwords, card details, and health data, and they always need consent in the EU.

**Verify.** Check initialization options for input/text masking and per-element suppression on sensitive screens (checkout, settings, any medical or financial form).

**Pass when** all inputs are masked by default, sensitive pages are excluded, and replay loads only after consent (PRV-03).

**Fix.** Enable mask-all-inputs (and mask-all-text where available); add the provider's block/suppress attribute to sensitive containers; gate init on consent.
