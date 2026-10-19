# Demo app: .env.local is committed on purpose so the scanner flags it.

# vibe-app (intentionally broken)

A tiny Next.js + Supabase + Stripe + Resend + OpenAI app that contains the mistakes LaunchCompliance looks for: a service-role key behind a `NEXT_PUBLIC_` variable, a committed `.env.local`, a table without RLS, trackers without consent, pre-ticked marketing consent, confirmshaming, fake testimonials, unsupported claims, a hidden service fee, PII in logs, and missing alt text and labels.

Values in `.env.local` are placeholders, not real keys. Do not deploy this app.
