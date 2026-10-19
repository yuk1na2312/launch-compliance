# Jurisdiction notes

A short orientation, not legal advice. Laws change; when a finding depends on a specific rule, tell the user to confirm the current requirement with the official source or a lawyer. Use these notes to adjust severity and to word "Why" lines, not to quote law.

Default when the user doesn't say: assume a global audience that includes the EU, which is usually the strictest common baseline.

## EU / EEA and UK (GDPR, UK GDPR, ePrivacy)

- Needs a legal basis for each processing purpose; consent must be opt-in, specific, and as easy to withdraw as to give.
- Non-essential cookies/trackers need prior consent (PRV-03 is Critical with ads or session replay).
- Data subject rights: access, rectification, erasure, portability, objection; respond within one month.
- International transfers (e.g. US-hosted vendors) must be disclosed and covered by a transfer mechanism; most major vendors offer one in their DPA.
- Age of digital consent 13–16 depending on the member state.
- Accessibility: the European Accessibility Act applies to many consumer e-commerce and digital services (micro-enterprises providing services are exempt).
- Consumer: 14-day withdrawal right for distance purchases, with a digital-content exception only if the consumer expressly agrees and acknowledges losing the right.

## United States

- No single federal privacy law. California (CCPA/CPRA) gives rights to know, delete, correct, and opt out of "sale/sharing" (which can include ad-tracking pixels); thresholds apply, but CalOPPA requires a posted privacy policy for any site collecting personal info from California residents. Many other states have similar laws.
- COPPA: verifiable parental consent before collecting personal information from children under 13 on child-directed services or with actual knowledge.
- CAN-SPAM: opt-out in commercial email, honored within 10 business days, physical postal address, no deceptive headers or subjects.
- FTC Act Section 5: unfair or deceptive practices (unsupported claims, dark patterns, broken privacy promises). FTC rules on fake reviews and on certain hidden fees; ROSCA for recurring charges.
- Accessibility: ADA Title III litigation commonly targets websites; WCAG 2.1/2.2 AA is the practical benchmark.

## Vietnam

- Personal data protection is governed by the Law on Personal Data Protection No. 91/2025/QH15 (effective 1 January 2026), building on Decree 13/2023/ND-CP. Expect requirements for consent, notice of processing purposes, data subject rights, special handling of sensitive data, children's data with parental consent, and cross-border transfer obligations. Verify current implementing decrees before relying on specifics.
- E-commerce websites must display seller information (business name, address, contact, registration details) under e-commerce rules.
- Advertising email and messages require prior consent and an opt-out under anti-spam regulations.

## Other common markets

- Brazil (LGPD), Canada (PIPEDA and Quebec Law 25), Australia (Privacy Act), India (DPDP Act), Japan (APPI), Singapore (PDPA), Thailand (PDPA) all share the core pattern: notice, lawful basis or consent, rights to access/correct/delete, security, and cross-border transfer rules. Treat the GDPR-level checks as a good baseline and recommend local review.

## Sector flags (recommend a lawyer)

Health or medical data (HIPAA in the US, special-category data in the EU), financial services, children's products, biometrics, precise location, employment data, and anything sold to governments. Mark these in the report as needing professional review regardless of findings.
