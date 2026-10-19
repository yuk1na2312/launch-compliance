# Signal map (manual fallback)

Use this when `scripts/detect_signals.py` can't run. Each signal decides which checks apply. Search dependency manifests first, then source code.

| Signal | Look for | Turns on |
|---|---|---|
| auth / user_accounts | next-auth, @clerk/*, auth0, lucia, better-auth, passport, spring-boot-starter-security, Supabase/Firebase auth calls, `users`/`profiles` tables, signup routes | PRV-01, PRV-05, PRV-08, PRV-09, SEC-03, LEG-01 |
| collects_email / pii_fields | email inputs and columns; DOB, phone, address, gender, national ID fields | PRV-01, PRV-04, PRV-05, PRV-07 |
| payments | stripe, paypal, lemonsqueezy, paddle, razorpay, revenuecat, VNPay, MoMo | PRV-01, LEG-01, LEG-02, LEG-03, CON-02 |
| subscriptions | `mode: "subscription"`, recurring prices, billing cycles | LEG-04, CON-01 |
| email | resend, sendgrid, nodemailer, postmark, mailgun, SES, spring-boot-starter-mail, mailchimp | CON-05 |
| analytics | GA/gtag/GTM, PostHog, Mixpanel, Amplitude, Segment, Firebase Analytics | PRV-02, PRV-03, PRV-06 |
| analytics_cookieless | Plausible, Umami | PRV-06 only (consent usually not needed) |
| session_replay | Hotjar, Clarity, LogRocket, FullStory, Datadog RUM replay, PostHog recordings | PRV-03 (Critical), PRV-13 |
| ads | Meta Pixel `fbq`, TikTok pixel, Google Ads, AdSense, LinkedIn Insight | PRV-03 (Critical), PRV-02 |
| ai | openai, @anthropic-ai/sdk, @google/genai, Vercel AI SDK `ai`, langchain, spring-ai | PRV-12, PRV-06 |
| error_tracking | @sentry/*, bugsnag | PRV-11 |
| supabase / firebase | @supabase/*, firebase, `*.supabase.co`, rules files | SEC-02, PRV-10 |
| file_upload / storage | `type="file"`, multer, MultipartFile, S3, UploadThing, Cloudinary | SEC-04 |
| exposed_secret | public-prefixed vars containing SECRET/SERVICE_ROLE/PRIVATE; `sk_live_`, `sk-`, private keys, `AKIA...` | SEC-01 |
| env_committed | `.env` files not covered by `.gitignore` | SEC-01 |
| pii_logging | log/print calls that include email, password, token, request body | PRV-11 |
| kids_audience | "for kids", ages under 13, school/student products | PRV-07 |
| testimonials / claims / urgency / prechecked_consent / confirmshaming / fees | hardcoded reviews, compliance or superlative claims, countdowns, pre-ticked boxes, guilt-trip declines, added fees | CON-01..04 |
| ui | any UI files (jsx/tsx/vue/svelte/html/templates) | A11Y-01..04, LEG-05 |
| international | i18n libraries | LEG-03, jurisdiction defaults |

Presence signals (suggest a check may already pass, still verify): legal pages by route name (privacy, terms, refund, cookie, contact), consent managers, deletion/export flows, unsubscribe handling, billing portal, retention jobs, age gates, business details in footer.
