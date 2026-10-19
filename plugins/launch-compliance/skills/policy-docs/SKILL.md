---
name: policy-docs
description: Draft a privacy policy, terms of service, refund policy, or cookie policy for an app based on what its code actually does - the data fields it stores, the third parties it sends data to, the cookies it sets, its payments and AI features - then add the pages and footer links to the project. Use when the user asks for any of these documents, or when the LaunchCompliance audit finds them missing or out of date.
---

# Policy documents from real code

Generic policy generators ask the founder what the app does. This skill reads the repo instead, so the document lists the real data, vendors, and cookies, and the user only supplies business facts the code can't know.

Every document you produce is a **draft for human review**, not legal advice. Say so once when you hand it over, and put a short HTML/MD comment at the top of each file marking it as a draft generated from code on a given date.

## Step 1 - Build the facts sheet

If `.launch-compliance/signals.json` or `.launch-compliance/REPORT.md` exists (from the `audit` skill), start from it. Otherwise run the detector from the audit skill's folder:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/audit/scripts/detect_signals.py" <repo-root> --out <repo-root>/.launch-compliance/signals.json
```

If the script isn't available (for example, this skill was installed on its own), read dependency manifests, schema/migrations/models, and third-party call sites yourself.

Then verify and fill in `references/facts-sheet.md`: data categories with their source files, purposes, third parties with what each receives, cookies and storage keys, payment model, AI usage, user-generated content, retention, user-rights mechanisms that exist in code (deletion, export, unsubscribe). Only include what you confirmed in code.

## Step 2 - Ask for business facts (one message)

Ask only for what's missing, in one compact list. Typical items:

- Legal name of the operator (company or individual) and country of establishment
- Contact email for privacy requests, and postal address if required by their markets
- Target markets (EU/UK, US, Vietnam, other) and minimum user age
- Refund terms (window, conditions, subscriptions vs one-time) - for refund policy
- Governing law / courts - for terms
- Retention periods they want, if not in code
- Effective date

Never invent these. If the user wants to proceed without some, leave a clearly marked placeholder like `[[COMPANY LEGAL NAME]]` and list the placeholders at the end.

## Step 3 - Draft

Use the outlines in `references/outlines.md`. Write in plain language: short sentences, second person ("we collect your email to..."), headings users can scan. Match facts exactly to the facts sheet:

- Name each third party and what it receives. Don't write "trusted partners".
- List cookies by provider and purpose; tie categories to the consent banner's categories.
- Describe user rights with the real mechanism ("Delete your account in Settings → Account", or "email privacy@...").
- If the code does something the user may not want disclosed this way (e.g. sends full chat history to an AI API), flag it in your message rather than softening the wording.

Jurisdiction sections: include an EU/UK section (legal bases, transfers, supervisory authority complaint right), a California section (CCPA/CPRA rights, "do not sell or share" if ad pixels are used), and a Vietnam section when relevant to the markets the user named. Keep each focused on what differs.

Language: write in the language(s) the site uses. If the site is bilingual (e.g. Vietnamese and English), produce both, with the same structure.

## Step 4 - Put it in the project

- Create pages in the project's routing and content style (e.g. `app/privacy/page.tsx` or `app/(legal)/privacy/page.mdx` for Next.js, `src/pages/privacy.astro`, Thymeleaf template for Spring MVC, `privacy.html` for static sites). Prefer Markdown/MDX if the project supports it, so non-developers can edit.
- Add footer links (Privacy, Terms, Cookies, Refunds as applicable) and a "Cookie settings" link if a consent banner exists.
- Link Privacy and Terms from signup; Refunds and Terms from pricing/checkout.
- Show "Last updated" on each page.

## Step 5 - Hand over

Tell the user in a few lines: which documents were created and where, which placeholders remain, which facts came from code (so they know what to keep in sync), and the recommendation to have a lawyer review before launch for regulated sectors or large EU audiences. Suggest re-running the LaunchCompliance audit after code changes that add data or vendors, since the policy must change with them.
