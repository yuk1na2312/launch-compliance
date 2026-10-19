# Consumer protection checks (CON)

These come from consumer protection law (FTC Act and FTC rules in the US, the EU Unfair Commercial Practices Directive and Digital Services Act, and similar national laws). Copy written quickly by AI tools often contains exactly what these laws prohibit.

Do not remove or rewrite marketing copy, prices, or reviews without asking the user. Point out the issue, explain the risk, propose replacement text, and wait for approval.

---

## CON-01 No dark patterns — Medium (High when found)

**Why.** Regulators treat manipulative design as unfair or deceptive, and under GDPR consent obtained through dark patterns is invalid.

**Verify.** Look for:
- Pre-ticked consent or marketing checkboxes
- Confirmshaming decline links ("No thanks, I don't like saving money")
- Fake urgency or scarcity: countdown timers that reset, "only 3 left" not backed by real inventory data, "12 people viewing" generated randomly (check whether the number comes from data or `Math.random`/hardcoded values)
- Asymmetric choices: bright "Accept" vs hidden "Reject"; cancel flows longer than signup
- Forced continuity: trials that convert without clear notice
- Sneaking items into the cart; default-selected add-ons

**Pass when** none are present, or urgency/scarcity claims are backed by real data.

**Fix.** Unticked checkboxes; neutral decline wording ("No thanks"); remove fake timers/counters or wire them to real data; equal-weight buttons; clear trial-to-paid notice.

---

## CON-02 No hidden fees / drip pricing — High

**Why.** Showing a low headline price and adding mandatory fees late in checkout is targeted by the FTC's rule on unfair or deceptive fees (live-event tickets and short-term lodging) and by consumer laws in the EU, UK, and several US states. Mandatory fees should be in the first price shown.

**Verify.** Trace the price from pricing page through checkout. Look for fees added in code (`service fee`, `processing fee`, line items added at checkout), taxes shown inconsistently, and currency conversions.

**Pass when** the first price shown includes all mandatory fees (taxes may be separate where local rules allow, but say so), and optional extras are clearly optional.

**Fix.** Show the total including mandatory fees on the pricing page and product cards; label optional extras; ask the user before changing actual prices.

---

## CON-03 No fake or unverifiable reviews — High (needs input)

**Why.** The FTC's rule on fake reviews and testimonials (in effect since 2024) prohibits fake or AI-generated reviews, reviews from people who don't exist, and misrepresenting reviews; EU law requires telling users how reviews are verified.

**Verify.** Find hardcoded testimonials, ratings, logos ("Trusted by..."), and user counts. Placeholder content from templates or AI ("Sarah K., Marketing Director") is the usual culprit. Ask the user whether each is real, with permission to publish.

**Pass when** every testimonial is real, attributable, and published with permission; stats ("50,000+ users") reflect real numbers; customer logos have permission.

**Fix.** Remove placeholders or replace with real ones the user provides; remove made-up numbers; if reviews come from a database, state how they're collected and verified.

---

## CON-04 No unsupported claims — Medium (High when found)

**Why.** Claims like "GDPR compliant", "HIPAA compliant", "bank-level encryption", "100% secure", "#1 rated", or "clinically proven" must be substantiated. Security and compliance claims that turn out false have led to regulatory action.

**Verify.** Grep marketing pages, metadata, and app store copy for the `claims` signals. For each, ask: is there evidence (certification, audit, real ranking source, study)? Compliance claims should be checked against this audit's own findings — "GDPR compliant" with no consent banner is false.

**Pass when** each claim is backed by evidence the user can produce, or is phrased as an accurate, specific statement ("Data encrypted in transit and at rest by our hosting provider").

**Fix.** Propose accurate replacements; remove superlatives without a source.

---

## CON-05 Unsubscribe link in marketing emails — High

**Why.** CAN-SPAM (US) requires a working opt-out in commercial email honored within 10 business days and a valid physical postal address; GDPR/ePrivacy and Vietnam's anti-spam rules require consent and easy opt-out. Gmail and Yahoo bulk-sender requirements also expect one-click unsubscribe (`List-Unsubscribe` headers).

**Verify.** Find every email send (Resend, SendGrid, Nodemailer, SES, Spring Mail, Mailchimp). Classify as transactional (receipts, password reset — no unsubscribe required) or marketing (newsletters, product updates, promotions, "we miss you" — required). For marketing: is there an unsubscribe link, a `List-Unsubscribe` header, a handler that records the opt-out, and a check before sending? Is a postal address in the footer?

**Pass when** every marketing email has a working unsubscribe link and header, opt-outs are stored and respected, and the footer has the sender's identity and address.

**Fix.** Add an unsubscribe token per user, an `/unsubscribe` route that records the opt-out, a `List-Unsubscribe` + `List-Unsubscribe-Post` header, a pre-send check of the opt-out flag, and a footer with business name and address (ask the user for it).
