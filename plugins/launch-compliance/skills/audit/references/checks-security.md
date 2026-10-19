# Code-level privacy leaks (SEC)

These are the issues that actually expose user data in vibe-coded apps. A perfect privacy policy does not help if the database is world-readable. This is not a full security review; it covers the leaks that most often turn into privacy incidents.

---

## SEC-01 Secrets exposed to the client or committed — Critical

**Why.** Anything prefixed `NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`, `EXPO_PUBLIC_`, `PUBLIC_`, or `NUXT_PUBLIC_` is bundled into the browser or app. A Supabase service-role key, Stripe secret key, or OpenAI key there gives anyone full access. Committed `.env` files leak the same way through git history.

**Verify.**
- Each `exposed_secret` hit: is it a secret (service role, `sk_live_`, `sk-`, private key, AWS key) or a public key by design (Supabase anon key, Stripe publishable key, Firebase web config)? Public-by-design keys are fine.
- Is the variable used in a file that runs in the browser (`"use client"`, components, `src/` of a SPA, mobile app code)?
- `env_committed`: is the `.env*` file tracked by git? (`git ls-files | grep -E '(^|/)\.env'`)

**Pass when** no secret key is reachable from client code or tracked files.

**Fix.**
- Rename to a server-only variable (no public prefix) and move the call into a server route, server action, or backend endpoint.
- Supabase: client code uses the anon key only; the service-role client lives in server-only code (`import "server-only"` in Next.js).
- Add `.env*` (except `.env.example`) to `.gitignore`, `git rm --cached` the tracked file, and add a `.env.example` with placeholder names.
- Tell the user plainly: **the key must be rotated in the provider dashboard**, because it is already in git history and possibly in deployed bundles. Removing it from code does not revoke it.

---

## SEC-02 Database access rules — Critical when missing

**Why.** With Supabase and Firebase the client talks to the database directly; access rules are the only thing between any visitor and every row. Tables without Row Level Security and `allow read, write: if true` rules are the most common mass-leak in AI-built apps.

**Verify.**
- Supabase: list every table in `supabase/migrations/*.sql` (and any `schema.sql`). Each table in an exposed schema (usually `public`) needs `alter table ... enable row level security` and policies scoped to `auth.uid()`. Check policies aren't `using (true)` for personal data. If migrations aren't in the repo, mark Needs input and give the user the SQL to check: `select tablename, rowsecurity from pg_tables where schemaname = 'public';`
- Firebase: read `firestore.rules`, `storage.rules`, `database.rules.json`. Any `if true` or rules that only check `request.auth != null` for per-user data are failures.
- Also check storage buckets (Supabase storage policies, Firebase storage rules) for user uploads.

**Pass when** every table/collection holding personal data enforces per-user access, and public data is explicitly read-only.

**Fix.** Write a migration enabling RLS on each table and adding owner-scoped policies (`using (auth.uid() = user_id)` for select/update/delete, `with check (auth.uid() = user_id)` for insert). For Firebase, rewrite rules to `request.auth.uid == resource.data.userId` (or path-based ownership). Explain how to test with two accounts.

---

## SEC-03 API routes don't return other users' data — High

**Why.** Endpoints like `GET /api/users?id=...` that fetch by a client-supplied ID without checking the caller (IDOR), or that use a service-role/admin client, leak everyone's data.

**Verify.** For each route handler, controller, server action, or edge function that reads personal data: Does it authenticate the caller? Does it scope the query to the caller's ID (or check ownership/role)? Does it return only needed columns? Spring: check `@PreAuthorize`/security config and that repository queries are scoped by the principal.

**Pass when** every personal-data route requires auth and enforces ownership server-side.

**Fix.** Derive the user ID from the session/token, not from query params or bodies; add ownership checks; switch from admin clients to user-scoped clients where possible; select explicit columns.

---

## SEC-04 Uploaded files are not publicly listable — Medium

**Why.** Public buckets with predictable paths expose IDs, avatars, invoices, and documents.

**Verify.** Check bucket visibility (Supabase `public: true`, S3 ACLs/bucket policy, Firebase storage rules, Cloudinary delivery type) and how URLs are generated.

**Pass when** private user files are in private buckets served via short-lived signed URLs, and only intentionally public assets are public.

**Fix.** Make the bucket private, serve via signed URLs with short expiry, scope storage policies to the owner's folder (`(storage.foldername(name))[1] = auth.uid()::text` in Supabase).
