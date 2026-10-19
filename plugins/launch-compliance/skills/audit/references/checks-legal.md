# Legal and commercial checks (LEG)

---

## LEG-01 Terms of service — High

**Why.** Terms set the rules of use, limit liability, define account termination, govern user content, and state a minimum age. Payment providers and app stores expect them for paid or account-based products.

**Verify.** Find the page and links (footer, signup "By signing up you agree...", checkout). If it exists, check it matches the product: paid plans and billing terms if there are payments, user-content license if users post content, AI output disclaimer if the app generates content, minimum age, governing law, contact.

**Pass when** Terms exist, are linked at signup and checkout, and match the product's actual features.

**Fix.** Draft via `policy-docs` with the features found in code. Add an acceptance line at signup ("By creating an account you agree to the Terms and Privacy Policy") and store the accepted version/date.

---

## LEG-02 Refund policy — High

**Why.** Card networks and payment processors expect a visible refund/cancellation policy; consumer laws (e.g. the EU's 14-day withdrawal right for online purchases, with conditions for digital content) apply.

**Verify.** Find a refund page or section. Check it covers subscriptions vs one-time purchases, trial conversion, how to request, timeframe, and any EU withdrawal-right handling for digital goods (the user must explicitly agree to immediate delivery and acknowledge losing the right).

**Pass when** a refund policy is linked from pricing and checkout and matches how billing works in code.

**Fix.** Ask the user for their refund terms (don't invent generosity or strictness), then draft via `policy-docs` and link it from pricing and checkout.

---

## LEG-03 Business details and contact — Medium (needs input)

**Why.** Many jurisdictions require sellers to identify themselves: legal name, address, contact email, and registration/tax numbers where applicable (EU e-commerce rules, German Impressum, Vietnam e-commerce rules for business websites). Payment providers and users also expect it.

**Verify.** Look for a contact page, footer details, an "About" or legal notice page.

**Pass when** the site shows legal entity name (or the individual operator), a contact email that works, and an address/registration number where the target market requires it.

**Fix.** Ask the user for the details. Never invent a company name, address, or registration number. Add a footer block and a contact/legal notice page.

---

## LEG-04 Easy subscription cancellation — High

**Why.** Several laws require a simple online way to cancel recurring charges (the US Restore Online Shoppers' Confidence Act enforced by the FTC, California's automatic renewal law and similar state laws, EU consumer rules). Hidden cancellation is also a top source of chargebacks.

**Verify.** With subscriptions detected, find the cancel path: Stripe customer portal link, in-app cancel button, or provider equivalent. Check that it's reachable from account settings without contacting support, and that the renewal terms (price, interval, how to cancel) are shown before purchase.

**Pass when** users can cancel online in a few clicks from settings, and recurring terms are disclosed at checkout.

**Fix.** Add a "Manage billing" button that opens the provider's customer portal (e.g. Stripe Billing Portal) or a cancel endpoint; show renewal terms near the subscribe button; send a confirmation email on cancel if email is set up.

---

## LEG-05 Licensed fonts, images and assets — Low (needs input)

**Why.** Commercial fonts, stock photos, icons, and illustrations need licenses that cover web/app use; AI-generated or scraped images may carry rights issues.

**Verify.** List local font files (`.woff2`, `.ttf`, `.otf`, `next/font/local`), image directories, icon packs, and remote stock image URLs. Google Fonts and Fontsource fonts are typically under the SIL Open Font License, which allows commercial use. Note fonts with names of known commercial foundries.

**Pass when** each non-open asset has a known source and license the user confirms.

**Fix.** Produce an asset inventory in the report with a "license?" column for the user to fill. Suggest open alternatives (Google Fonts, OFL fonts, Unsplash under its license, open icon sets like Lucide/Heroicons) for anything unclear. Add a `CREDITS.md` or attributions section if any license requires attribution.
