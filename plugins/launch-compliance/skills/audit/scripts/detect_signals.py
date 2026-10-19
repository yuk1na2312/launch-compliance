#!/usr/bin/env python3
"""
LaunchCompliance signal detector.

Walks a repository, reads dependency manifests and source files, and produces
*candidate* findings: which compliance checks are likely to apply, why, and
where the evidence is. It does not decide anything final; the audit skill
verifies each candidate by reading the code.

Standard library only. Python 3.8+.

Usage:
    python3 detect_signals.py <repo_path> [--out signals.json] [--md]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

# --------------------------------------------------------------------------
# Walk configuration
# --------------------------------------------------------------------------
SKIP_DIRS = {
    ".git", "node_modules", ".next", ".nuxt", ".svelte-kit", ".output", "dist",
    "build", "out", "target", "vendor", ".venv", "venv", "env", "__pycache__",
    ".gradle", ".idea", ".vscode", "coverage", ".turbo", ".vercel", ".expo",
    "Pods", ".dart_tool", ".launch-compliance", "bin", "obj",
}
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
    ".html", ".htm", ".css", ".scss", ".sass", ".less", ".md", ".mdx",
    ".py", ".rb", ".php", ".java", ".kt", ".kts", ".go", ".rs", ".dart",
    ".swift", ".cs", ".sql", ".json", ".yaml", ".yml", ".toml", ".xml",
    ".gradle", ".env", ".rules", ".prisma", ".graphql", ".txt", ".erb",
    ".hbs", ".ejs", ".njk", ".liquid", ".jinja", ".j2", ".mjml", ".properties",
}
UI_EXT = {".jsx", ".tsx", ".vue", ".svelte", ".astro", ".html", ".htm", ".erb",
          ".hbs", ".ejs", ".njk", ".liquid", ".jinja", ".j2", ".php", ".dart"}
STYLE_EXT = {".css", ".scss", ".sass", ".less"}
MAX_FILE_BYTES = 1_000_000
MAX_EVIDENCE = 8

# --------------------------------------------------------------------------
# Third-party vendors, matched against dependency names (regex, full match
# on the lowercase name) and against code (regex search).
# kind -> also emitted as a signal.
# --------------------------------------------------------------------------
VENDORS = [
    # payments
    ("Stripe", "payments", r"(@stripe/.*|stripe|stripe-java|com\.stripe:.*)", r"js\.stripe\.com|sk_(live|test)_|pk_(live|test)_"),
    ("PayPal", "payments", r"(@paypal/.*|paypal.*)", r"paypal\.com/sdk"),
    ("Lemon Squeezy", "payments", r"(@lemonsqueezy/.*|lemonsqueezy.*)", r"lemonsqueezy\.com"),
    ("Paddle", "payments", r"(@paddle/.*|paddle.*)", r"cdn\.paddle\.com"),
    ("Polar", "payments", r"(@polar-sh/.*)", None),
    ("Razorpay", "payments", r"(razorpay)", r"checkout\.razorpay\.com"),
    ("RevenueCat", "payments", r"(react-native-purchases|purchases_flutter|@revenuecat/.*)", None),
    ("VNPay", "payments", r"(vnpay.*)", r"vnpayment\.vn|vnp_TmnCode"),
    ("MoMo", "payments", r"(momo.*)", r"test-payment\.momo\.vn|payment\.momo\.vn"),
    # auth
    ("NextAuth / Auth.js", "auth", r"(next-auth|@auth/.*)", None),
    ("Clerk", "auth", r"(@clerk/.*)", None),
    ("Auth0", "auth", r"(@auth0/.*|auth0.*|com\.auth0:.*)", None),
    ("Lucia", "auth", r"(lucia)", None),
    ("Better Auth", "auth", r"(better-auth)", None),
    ("Passport", "auth", r"(passport|passport-.*)", None),
    ("Spring Security", "auth", r"(org\.springframework\.boot:spring-boot-starter-security|spring-boot-starter-security|spring-security-.*)", None),
    ("Firebase Auth", "auth", r"(@react-native-firebase/auth|firebase_auth)", r"getAuth\(|signInWith(Email|Popup|Redirect)"),
    ("Supabase Auth", "auth", None, r"supabase\.auth\.(signUp|signIn|signInWith)"),
    # database / backend-as-a-service
    ("Supabase", "supabase", r"(@supabase/.*|supabase|supabase_flutter)", r"\.supabase\.co"),
    ("Firebase", "firebase", r"(firebase|firebase-admin|@firebase/.*|firebase_core|com\.google\.firebase:.*)", r"firebaseio\.com|firebaseapp\.com"),
    ("Prisma", "database", r"(prisma|@prisma/client)", None),
    ("Drizzle", "database", r"(drizzle-orm)", None),
    ("Mongoose", "database", r"(mongoose|mongodb)", None),
    ("JPA / Hibernate", "database", r"(org\.springframework\.boot:spring-boot-starter-data-jpa|spring-boot-starter-data-jpa|hibernate-core|org\.hibernate.*)", None),
    ("SQLAlchemy / Django ORM", "database", r"(sqlalchemy|django|psycopg2.*|psycopg)", None),
    ("Convex", "database", r"(convex)", None),
    # email
    ("Resend", "email", r"(resend|@react-email/.*)", None),
    ("SendGrid", "email", r"(@sendgrid/.*|sendgrid.*|com\.sendgrid:.*)", None),
    ("Nodemailer", "email", r"(nodemailer)", None),
    ("Postmark", "email", r"(postmark)", None),
    ("Mailgun", "email", r"(mailgun.*|mailgun\.js)", None),
    ("Amazon SES", "email", r"(@aws-sdk/client-ses|@aws-sdk/client-sesv2|software\.amazon\.awssdk:ses.*)", None),
    ("Spring Mail", "email", r"(org\.springframework\.boot:spring-boot-starter-mail|spring-boot-starter-mail)", None),
    ("Mailchimp", "email", r"(@mailchimp/.*|mailchimp.*)", r"list-manage\.com"),
    ("Loops", "email", r"(loops)", r"app\.loops\.so"),
    ("ConvertKit / Kit", "email", r"(convertkit.*)", None),
    # analytics
    ("Google Analytics / GTM", "analytics", r"(react-ga4|react-ga|@next/third-parties|vue-gtag|ga-4-react)", r"googletagmanager\.com|gtag\(|google-analytics\.com"),
    ("Vercel Analytics", "analytics", r"(@vercel/analytics|@vercel/speed-insights)", None),
    ("PostHog", "analytics", r"(posthog-js|posthog-node|posthog-react-native|posthog)", r"posthog\.com|posthog\.init"),
    ("Mixpanel", "analytics", r"(mixpanel.*)", None),
    ("Amplitude", "analytics", r"(@amplitude/.*|amplitude-js)", None),
    ("Segment", "analytics", r"(@segment/.*|analytics-node)", r"cdn\.segment\.com"),
    ("Plausible", "analytics_cookieless", r"(next-plausible|plausible-tracker)", r"plausible\.io/js"),
    ("Umami", "analytics_cookieless", None, r"umami\.(is|js)|data-website-id"),
    ("Firebase Analytics", "analytics", r"(@react-native-firebase/analytics|firebase_analytics)", r"getAnalytics\("),
    # session replay
    ("Hotjar", "session_replay", r"(@hotjar/.*|react-hotjar)", r"static\.hotjar\.com|hotjar"),
    ("Microsoft Clarity", "session_replay", r"(@microsoft/clarity|react-microsoft-clarity)", r"clarity\.ms"),
    ("LogRocket", "session_replay", r"(logrocket.*)", None),
    ("FullStory", "session_replay", r"(@fullstory/.*)", None),
    # error tracking
    ("Sentry", "error_tracking", r"(@sentry/.*|sentry-sdk|io\.sentry:.*|sentry_flutter)", r"ingest\.sentry\.io"),
    ("Bugsnag", "error_tracking", r"(@bugsnag/.*)", None),
    ("Datadog RUM", "session_replay", r"(@datadog/browser-rum.*)", None),
    # ads / marketing pixels
    ("Meta Pixel", "ads", r"(react-facebook-pixel)", r"connect\.facebook\.net|fbq\("),
    ("TikTok Pixel", "ads", None, r"analytics\.tiktok\.com|ttq\.load"),
    ("Google Ads", "ads", None, r"googleadservices\.com|AW-\d{6,}"),
    ("Google AdSense", "ads", None, r"pagead2\.googlesyndication\.com"),
    ("LinkedIn Insight", "ads", None, r"snap\.licdn\.com"),
    # AI providers (user data leaves your system)
    ("OpenAI", "ai", r"(openai|@ai-sdk/openai|com\.openai:.*)", r"api\.openai\.com"),
    ("Anthropic", "ai", r"(@anthropic-ai/sdk|anthropic|@ai-sdk/anthropic|com\.anthropic:.*)", r"api\.anthropic\.com"),
    ("Google Gemini", "ai", r"(@google/generative-ai|@google/genai|google-generativeai|@ai-sdk/google)", r"generativelanguage\.googleapis\.com"),
    ("Vercel AI SDK", "ai", r"(ai)", None),
    ("Replicate", "ai", r"(replicate)", None),
    ("Spring AI", "ai", r"(org\.springframework\.ai:.*|spring-ai-.*)", None),
    ("LangChain", "ai", r"(langchain|@langchain/.*|langchain4j.*|dev\.langchain4j:.*)", None),
    # storage / uploads
    ("UploadThing", "storage", r"(uploadthing|@uploadthing/.*)", None),
    ("Cloudinary", "storage", r"(cloudinary|next-cloudinary)", r"res\.cloudinary\.com"),
    ("AWS S3", "storage", r"(@aws-sdk/client-s3|boto3|software\.amazon\.awssdk:s3|aws-sdk)", None),
    # support / chat widgets
    ("Intercom", "support_widget", r"(@intercom/.*|react-use-intercom)", r"widget\.intercom\.io"),
    ("Crisp", "support_widget", r"(crisp-sdk-web)", r"client\.crisp\.chat"),
    ("Tawk.to", "support_widget", r"(@tawk\.to/.*)", r"embed\.tawk\.to"),
    # maps / location
    ("Google Maps", "location", r"(@react-google-maps/.*|@googlemaps/.*)", r"maps\.googleapis\.com"),
    ("Mapbox", "location", r"(mapbox-gl|react-map-gl)", None),
    # consent managers (good signal)
    ("Consent manager", "consent_manager", r"(vanilla-cookieconsent|react-cookie-consent|cookieconsent|klaro|@cookiehub/.*|@osano/.*|react-cookie-banner|@c15t/.*|c15t)", r"cookiebot\.com|cdn\.cookielaw\.org|onetrust|iubenda\.com|termly\.io|osano\.com|cookieyes\.com"),
    # i18n (signals international audience)
    ("i18n", "international", r"(next-intl|react-i18next|i18next|vue-i18n|next-i18next|@nuxtjs/i18n|svelte-i18n|@lingui/.*|flutter_localizations)", None),
]

FRAMEWORKS = [
    ("Next.js", r"next"), ("React", r"react"), ("Vue", r"vue"), ("Nuxt", r"nuxt"),
    ("SvelteKit", r"@sveltejs/kit"), ("Svelte", r"svelte"), ("Astro", r"astro"),
    ("Remix", r"@remix-run/.*"), ("Express", r"express"), ("NestJS", r"@nestjs/core"),
    ("Hono", r"hono"), ("React Native", r"react-native"), ("Expo", r"expo"),
    ("Django", r"django"), ("Flask", r"flask"), ("FastAPI", r"fastapi"),
    ("Spring Boot", r"(org\.springframework\.boot:.*|spring-boot-starter.*)"),
    ("Laravel", r"laravel/framework"), ("Rails", r"rails"), ("Flutter", r"flutter"),
]

# --------------------------------------------------------------------------
# Code signals: regex searched per line. (signal, regex, extensions or None)
# --------------------------------------------------------------------------
I = re.IGNORECASE
CODE_SIGNALS = [
    # data collection
    ("collects_email", re.compile(r"type=[\"']email[\"']|name=[\"']email[\"']|\bemail\s*[:=]\s*(z\.|String|varchar|text|str\b)|@Email\b|EmailField|\"email\"\s*:\s*\{", I), None),
    ("pii_fields", re.compile(r"\b(date_?of_?birth|dob|birth_?date|birthday|phone_?(number)?|home_?address|street_?address|gender|ssn|national_?id|passport|id_?card|cccd|cmnd|tax_?id)\b", I), None),
    ("collects_dob", re.compile(r"\b(date_?of_?birth|dob|birth_?date|birthday)\b", I), None),
    ("cookies", re.compile(r"document\.cookie\s*=|cookies\(\)\.set|res\.cookie\(|setCookie\(|Set-Cookie|new Cookie\(|response\.addCookie|js-cookie|universal-cookie|set_cookie\(", I), None),
    ("forms", re.compile(r"<form\b|onSubmit=|@PostMapping|@app\.post|router\.post\(|app\.post\(|useForm\(|action=\{", I), None),
    ("newsletter", re.compile(r"newsletter|subscribe to (our|the)|join (our|the) (list|waitlist)|waitlist", I), None),
    ("file_upload", re.compile(r"type=[\"']file[\"']|multer|MultipartFile|UploadFile|formidable|busboy|createSignedUploadUrl|\.upload\(", I), None),
    ("user_accounts", re.compile(r"\b(signUp|sign_up|register(User)?|createUser|users?\s*table|model\s+User\b|class\s+User\b|CREATE TABLE\s+\"?(public\.)?(users|profiles|accounts)\b)", I), None),
    ("ugc", re.compile(r"\b(comments?|posts?|reviews?)\b\s*(table|model|schema|collection)|create table\s+\"?(public\.)?(comments|posts|messages)\b", I), None),
    ("location_access", re.compile(r"navigator\.geolocation|getCurrentPosition|ACCESS_FINE_LOCATION|requestForegroundPermissionsAsync", I), None),
    ("kids_audience", re.compile(r"\b(for kids|for children|children's|kid-friendly|ages? \d{1,2}\s*[-–to]+\s*1[0-2]|elementary school|primary school|tiểu học|thiếu nhi|trẻ em|coppa)\b", I), None),
    # money
    ("subscriptions", re.compile(r"\b(subscription|recurring|billing_?cycle|interval\s*:\s*[\"'](month|year)|mode\s*:\s*[\"']subscription|checkout\.sessions\.create)\b", I), None),
    ("fees", re.compile(r"\b(service fee|processing fee|convenience fee|booking fee|platform fee|handling fee)\b", I), None),
    # consumer protection
    ("prechecked_consent", re.compile(r"(defaultChecked|checked=\{?true\}?|checked\b(?!=\{?false))[^>]{0,120}(newsletter|marketing|consent|subscribe|terms|share)|(newsletter|marketing|consent|subscribe)[^>]{0,120}(defaultChecked|checked=\{?true)", I), UI_EXT),
    ("urgency", re.compile(r"\b(only \d+ left|\d+ people are (viewing|looking)|offer ends in|hurry|limited time only|countdown|selling fast)\b", I), None),
    ("confirmshaming", re.compile(r"no thanks,? i (don't|do not) (want|like|care)|i('d| would) rather (pay|lose|miss)|i (hate|don't like) (saving|money|deals)", I), None),
    ("testimonials", re.compile(r"\b(testimonials?|reviews?)\b\s*[=:]\s*\[|\brating\s*:\s*[45](\.\d)?\b|★★★★★|\b(5|five)[- ]star\b|\btrusted by\s+[\d,.]+k?\+?", I), None),
    ("claims", re.compile(r"\b(gdpr[- ]compliant|hipaa[- ]compliant|soc ?2[- ](certified|compliant)|iso ?27001 certified|100% (secure|safe|private|guaranteed)|bank[- ](level|grade) (security|encryption)|military[- ]grade|unhackable|#1 (rated|app|platform|tool)|number one|best in the world|clinically proven|guaranteed results)\b", I), None),
    # code-level privacy leaks
    ("exposed_secret", re.compile(r"\b(NEXT_PUBLIC|VITE|REACT_APP|EXPO_PUBLIC|PUBLIC|NUXT_PUBLIC)_[A-Z0-9_]*(SECRET|SERVICE_ROLE|PRIVATE|ADMIN)[A-Z0-9_]*\b|sk_live_[0-9a-zA-Z]{16,}|\bsk-(proj-)?[A-Za-z0-9_-]{32,}|sk-ant-[A-Za-z0-9_-]{20,}|-----BEGIN (RSA |EC )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}", 0), None),
    ("pii_logging", re.compile(r"(console\.(log|info|debug|error)|logger\.(info|debug|warn|error)|log\.(info|debug|warn|error)|print\(|System\.out\.println)\s*\([^)]*\b(email|password|passwd|token|phone|address|ssn|req\.body|request\.body|user\b|credit|card)", I), None),
    ("firebase_open_rules", re.compile(r"allow\s+read\s*,\s*write\s*:\s*if\s+true|allow\s+(read|write)\s*:\s*if\s+true|\"\.(read|write)\"\s*:\s*true", I), None),
    ("rls_enabled", re.compile(r"enable row level security", I), None),
    ("create_table", re.compile(r"create table\s+(if not exists\s+)?\"?(public\.)?\w+", I), {".sql"}),
    ("supabase_service_role_client", re.compile(r"SERVICE_ROLE", 0), None),
    ("replay_masking", re.compile(r"maskAllInputs|maskAllText|data-hj-suppress|data-private|blockAllMedia|mask_all_text|session_recording\s*:\s*\{", I), None),
    # existing compliance features
    ("deletion_flow", re.compile(r"(delete|remove|close|erase)[-_ ]?(my[-_ ]?)?(account|user|profile|data)\b|deleteUser\(|auth\.admin\.deleteUser|right to (erasure|be forgotten)", I), None),
    ("export_flow", re.compile(r"(export|download)[-_ ]?(my[-_ ]?)?(data|account)\b|data[-_ ]?portability", I), None),
    ("unsubscribe", re.compile(r"unsubscribe|List-Unsubscribe|opt[- ]?out|manage (email )?preferences", I), None),
    ("cancel_subscription", re.compile(r"cancel[-_ ]?(subscription|plan|membership)|billingPortal|billing_portal|customer[-_ ]?portal", I), None),
    ("retention_logic", re.compile(r"\b(retention|ttl|expire_?at|expiresAt|purge|cleanup|prune)\b.*\b(days?|months?|interval|cron|schedule)", I), None),
    ("age_gate", re.compile(r"(are you|must be|at least)\s+(1[3-8]|over 1[3-8])|age[-_ ]?(gate|verification|check)|parental consent", I), None),
    ("business_details", re.compile(r"\b(registered (office|address)|company (number|registration)|vat (id|number)|tax (id|code)|mã số thuế|legal entity|imprint|impressum)\b", I), None),
    # accessibility (UI files only)
    ("outline_removed", re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b|focus:outline-none(?![^\"']*focus-visible)", I), UI_EXT | STYLE_EXT),
    ("clickable_div", re.compile(r"<(div|span|li|img)\b[^>]*\bonClick=", I), UI_EXT),
    ("positive_tabindex", re.compile(r"tabIndex=\{?[\"']?[1-9]|tabindex=[\"'][1-9]", I), UI_EXT),
    ("html_lang_missing", re.compile(r"<html(?![^>]*\blang=)[^>]*>", I), UI_EXT),
    ("local_fonts", re.compile(r"@font-face|next/font/local|\.woff2?[\"')]|\.ttf[\"')]|\.otf[\"')]", I), None),
    ("google_fonts", re.compile(r"fonts\.googleapis\.com|next/font/google|@fontsource/", I), None),
    ("remote_images", re.compile(r"(unsplash|pexels|pixabay|shutterstock|istockphoto|gettyimages|freepik)\.(com|net)", I), None),
]

# image without alt, checked per tag (can span lines in JSX, so we scan whole file)
IMG_TAG = re.compile(r"<(img|Image)\b([^>]*?)/?>", re.S)
INPUT_TAG = re.compile(r"<(input|textarea|select)\b([^>]*?)/?>", re.S | re.I)

LEGAL_PAGE_PATTERNS = {
    "privacy": re.compile(r"privacy|chinh-sach-bao-mat|bao-mat", I),
    "terms": re.compile(r"terms|tos\b|conditions|dieu-khoan", I),
    "refund": re.compile(r"refund|return-policy|returns|hoan-tien", I),
    "cookie": re.compile(r"cookie", I),
    "accessibility": re.compile(r"accessibility|a11y-statement", I),
    "contact": re.compile(r"contact|imprint|impressum|lien-he|about", I),
    "subprocessors": re.compile(r"subprocessor|sub-processor|third-part(y|ies)", I),
}
PAGE_DIR_HINT = re.compile(r"(^|/)(pages|app|routes|views|templates|public|static|src/pages|src/app|src/routes|content|resources/templates|legal|docs)(/|$)", I)

# --------------------------------------------------------------------------
# Check catalog. Each check lists trigger signals (any) and an optional
# "present" signal that suggests it may already be handled.
# --------------------------------------------------------------------------
PERSONAL_DATA = ["auth", "user_accounts", "collects_email", "pii_fields", "payments",
                 "analytics", "session_replay", "ads", "email", "newsletter", "supabase", "firebase"]
UI = ["ui"]

CHECKS = [
    # id, category, title, triggers, base severity, present signal (or legal page key prefixed with "page:")
    ("PRV-01", "privacy", "Privacy policy", PERSONAL_DATA, "critical", "page:privacy"),
    ("PRV-02", "privacy", "Cookie policy", ["cookies", "analytics", "ads", "session_replay", "support_widget"], "high", "page:cookie"),
    ("PRV-03", "privacy", "Cookie consent banner that blocks non-essential scripts until opt-in", ["analytics", "ads", "session_replay"], "high", "consent_manager"),
    ("PRV-04", "privacy", "Consent and purpose text on forms", ["collects_email", "newsletter", "pii_fields", "forms"], "medium", None),
    ("PRV-05", "privacy", "Data minimization (no unnecessary fields)", ["pii_fields", "user_accounts"], "medium", None),
    ("PRV-06", "privacy", "Third-party SDK audit and sub-processor disclosure", ["third_party"], "high", "page:subprocessors"),
    ("PRV-07", "privacy", "Age gate / children's data consent", ["kids_audience", "collects_dob"], "high", "age_gate"),
    ("PRV-08", "privacy", "Account and data deletion request", ["auth", "user_accounts"], "high", "deletion_flow"),
    ("PRV-09", "privacy", "Data access and export", ["auth", "user_accounts"], "medium", "export_flow"),
    ("PRV-10", "privacy", "Data retention rules", ["database", "supabase", "firebase", "user_accounts"], "medium", "retention_logic"),
    ("PRV-11", "privacy", "No personal data in logs or error reports", ["pii_logging", "error_tracking"], "high", None),
    ("PRV-12", "privacy", "AI provider data-sharing disclosure", ["ai"], "high", None),
    ("PRV-13", "privacy", "Session replay masks inputs and sensitive text", ["session_replay"], "high", "replay_masking"),
    ("SEC-01", "security", "No secrets exposed in client code or committed files", ["exposed_secret", "env_committed"], "critical", None),
    ("SEC-02", "security", "Database access rules (Supabase RLS / Firebase rules)", ["supabase", "firebase"], "critical", None),
    ("SEC-03", "security", "API routes do not return other users' data (auth + ownership checks)", ["auth", "user_accounts"], "high", None),
    ("SEC-04", "security", "Uploaded files are not publicly listable", ["file_upload", "storage"], "medium", None),
    ("LEG-01", "legal", "Terms of service", ["auth", "user_accounts", "payments", "ugc"], "high", "page:terms"),
    ("LEG-02", "legal", "Refund policy", ["payments"], "high", "page:refund"),
    ("LEG-03", "legal", "Business details and contact", ["payments", "international", "auth"], "medium", "business_details"),
    ("LEG-04", "legal", "Easy subscription cancellation", ["subscriptions"], "high", "cancel_subscription"),
    ("LEG-05", "legal", "Licensed fonts, images and assets", ["local_fonts", "google_fonts", "remote_images", "ui"], "low", None),
    ("CON-01", "consumer", "No dark patterns", ["prechecked_consent", "urgency", "confirmshaming", "subscriptions"], "medium", None),
    ("CON-02", "consumer", "No hidden fees / drip pricing", ["payments", "fees"], "high", None),
    ("CON-03", "consumer", "No fake or unverifiable reviews/testimonials", ["testimonials"], "high", None),
    ("CON-04", "consumer", "No unsupported claims", ["claims"], "medium", None),
    ("CON-05", "consumer", "Unsubscribe link in marketing emails", ["email", "newsletter"], "high", "unsubscribe"),
    ("A11Y-01", "accessibility", "Alt text on images", ["img_missing_alt", "ui"], "medium", None),
    ("A11Y-02", "accessibility", "Color contrast (WCAG AA)", UI, "medium", None),
    ("A11Y-03", "accessibility", "Keyboard navigation, visible focus and page language", ["outline_removed", "clickable_div", "positive_tabindex", "html_lang_missing", "ui"], "medium", None),
    ("A11Y-04", "accessibility", "Form fields have labels", ["inputs_without_label", "forms"], "medium", None),
]

# Signals strong enough to upgrade severity one step, per check.
ESCALATE = {
    "PRV-03": ["ads", "session_replay"],
    "PRV-07": ["kids_audience"],
    "SEC-02": ["rls_missing", "firebase_open_rules"],
    "CON-01": ["prechecked_consent", "confirmshaming"],
    "CON-04": ["claims"],
    "A11Y-01": ["img_missing_alt"],
    "A11Y-03": ["outline_removed", "clickable_div"],
}
SEV_ORDER = ["low", "medium", "high", "critical"]

# Checks that the script cannot judge from code alone.
NEEDS_INPUT = {"PRV-07", "LEG-03", "LEG-05", "CON-03"}


# --------------------------------------------------------------------------
def rel(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def read_text(path):
    try:
        if os.path.getsize(path) > MAX_FILE_BYTES:
            return None
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return None


def parse_dependencies(root, files):
    """Return {dep_name_lower: manifest_rel_path}."""
    deps = {}

    def add(name, src):
        if name:
            deps.setdefault(name.strip().lower(), src)

    for path in files:
        name = os.path.basename(path)
        r = rel(path, root)
        if name == "package.json":
            text = read_text(path)
            try:
                data = json.loads(text or "{}")
            except json.JSONDecodeError:
                continue
            for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                for d in (data.get(key) or {}):
                    add(d, r)
        elif re.match(r"requirements.*\.txt$", name):
            for line in (read_text(path) or "").splitlines():
                m = re.match(r"\s*([A-Za-z0-9_.\-\[\]]+)", line)
                if m and not line.strip().startswith("#"):
                    add(re.sub(r"\[.*\]", "", m.group(1)), r)
        elif name == "pyproject.toml":
            for m in re.finditer(r"^\s*[\"']?([A-Za-z0-9_.\-]+)[\"']?\s*(=|>=|==|~=|\^|<)", read_text(path) or "", re.M):
                add(m.group(1), r)
            for m in re.finditer(r"[\"']([A-Za-z0-9_.\-]+)\s*(\[.*?\])?\s*(>=|==|~=|<|>|$|[\"'])", read_text(path) or ""):
                add(m.group(1), r)
        elif name == "pom.xml":
            text = read_text(path) or ""
            for m in re.finditer(r"<dependency>.*?<groupId>([^<]+)</groupId>.*?<artifactId>([^<]+)</artifactId>", text, re.S):
                add(f"{m.group(1)}:{m.group(2)}", r)
                add(m.group(2), r)
            if "<parent>" in text and "spring-boot" in text:
                add("org.springframework.boot:spring-boot", r)
        elif name in ("build.gradle", "build.gradle.kts"):
            for m in re.finditer(r"[\"']([A-Za-z0-9_.\-]+):([A-Za-z0-9_.\-]+)(:[^\"']*)?[\"']", read_text(path) or ""):
                add(f"{m.group(1)}:{m.group(2)}", r)
                add(m.group(2), r)
            if "org.springframework.boot" in (read_text(path) or ""):
                add("org.springframework.boot:spring-boot", r)
        elif name == "go.mod":
            for m in re.finditer(r"^\s*(?:require\s+)?([a-z0-9.\-/]+\.[a-z]+/[^\s]+)\s+v", read_text(path) or "", re.M):
                add(m.group(1), r)
                add(m.group(1).split("/")[-1], r)
        elif name == "composer.json":
            try:
                data = json.loads(read_text(path) or "{}")
            except json.JSONDecodeError:
                continue
            for key in ("require", "require-dev"):
                for d in (data.get(key) or {}):
                    add(d, r)
        elif name == "Gemfile":
            for m in re.finditer(r"^\s*gem\s+[\"']([^\"']+)", read_text(path) or "", re.M):
                add(m.group(1), r)
        elif name == "pubspec.yaml":
            in_deps = False
            for line in (read_text(path) or "").splitlines():
                if re.match(r"^(dev_)?dependencies:", line):
                    in_deps = True
                    continue
                if in_deps and re.match(r"^\S", line):
                    in_deps = False
                m = re.match(r"^\s{2}([a-z0-9_]+):", line)
                if in_deps and m:
                    add(m.group(1), r)
    return deps


def walk(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in (".github", ".claude-plugin", ".well-known")]
        for fn in filenames:
            out.append(os.path.join(dirpath, fn))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="Path to the repository to scan")
    ap.add_argument("--out", help="Write JSON here (default: stdout)")
    ap.add_argument("--md", action="store_true", help="Also print a short markdown summary to stderr")
    args = ap.parse_args()

    root = os.path.abspath(args.repo)
    if not os.path.isdir(root):
        sys.exit(f"Not a directory: {root}")

    all_files = walk(root)
    signals = defaultdict(list)          # name -> [evidence strings]
    third_parties = {}                   # vendor -> {kind, evidence}
    legal_pages = defaultdict(list)
    stack = []

    def ev(sig, where):
        if len(signals[sig]) < MAX_EVIDENCE and where not in signals[sig]:
            signals[sig].append(where)

    # ---- dependencies ----------------------------------------------------
    deps = parse_dependencies(root, all_files)
    for fw, pat in FRAMEWORKS:
        rx = re.compile(pat + r"$")
        hits = [d for d in deps if rx.match(d)]
        if hits:
            stack.append(fw)
    for vendor, kind, dep_pat, _ in VENDORS:
        if not dep_pat:
            continue
        rx = re.compile(dep_pat + r"$")
        for d, src in deps.items():
            if rx.match(d):
                third_parties.setdefault(vendor, {"kind": kind, "evidence": []})
                e = f"{src}: dependency `{d}`"
                if e not in third_parties[vendor]["evidence"]:
                    third_parties[vendor]["evidence"].append(e)
                ev(kind, e)

    # ---- env files -------------------------------------------------------
    gitignore = read_text(os.path.join(root, ".gitignore")) or ""
    env_ignored = bool(re.search(r"^\s*\.env(\*|\.\*|\.local)?\s*$|^\s*\*\.env\s*$|^\s*\.env\*?\s*$", gitignore, re.M))
    for path in all_files:
        b = os.path.basename(path)
        if re.match(r"^\.env(\..+)?$", b) and not re.search(r"example|sample|template|dist", b, I):
            if not env_ignored:
                ev("env_committed", f"{rel(path, root)} (not covered by .gitignore)")

    # ---- source scan -----------------------------------------------------
    vendor_code = [(v, k, re.compile(p, I)) for v, k, _, p in VENDORS if p]
    scanned = 0
    ui_files = 0
    img_missing = 0
    inputs_unlabeled = 0
    sql_tables = []
    sql_rls = 0
    for path in all_files:
        ext = os.path.splitext(path)[1].lower()
        base = os.path.basename(path)
        r = rel(path, root)
        is_env = base.startswith(".env")
        if ext not in TEXT_EXT and not is_env and base not in ("Dockerfile",):
            continue
        # legal pages by path
        if PAGE_DIR_HINT.search(r) or ext in (".md", ".mdx", ".html"):
            for key, rx in LEGAL_PAGE_PATTERNS.items():
                if rx.search(r) and not re.search(r"node_modules|test|spec|\.json$", r, I):
                    if len(legal_pages[key]) < MAX_EVIDENCE:
                        legal_pages[key].append(r)
        text = read_text(path)
        if text is None:
            continue
        scanned += 1
        if base in ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Cargo.lock"):
            continue
        is_ui = ext in UI_EXT
        if is_ui:
            ui_files += 1
            ev("ui", r)
        lines = text.splitlines()
        for ln, line in enumerate(lines, 1):
            if len(line) > 2000:
                line = line[:2000]
            for sig, rx, exts in CODE_SIGNALS:
                if exts is not None and ext not in exts:
                    continue
                if sig == "exposed_secret" and (is_env and env_ignored):
                    continue  # local env files that are gitignored are fine
                if rx.search(line):
                    ev(sig, f"{r}:{ln}")
            for vendor, kind, rx in vendor_code:
                if rx.search(line):
                    third_parties.setdefault(vendor, {"kind": kind, "evidence": []})
                    e = f"{r}:{ln}"
                    if len(third_parties[vendor]["evidence"]) < MAX_EVIDENCE and e not in third_parties[vendor]["evidence"]:
                        third_parties[vendor]["evidence"].append(e)
                    ev(kind, e)
        if is_ui:
            for m in IMG_TAG.finditer(text):
                attrs = m.group(2)
                if not re.search(r"\balt\s*=", attrs) and not re.search(r"\{\s*\.\.\.", attrs):
                    img_missing += 1
                    ln = text.count("\n", 0, m.start()) + 1
                    ev("img_missing_alt", f"{r}:{ln}")
            for m in INPUT_TAG.finditer(text):
                attrs = m.group(2)
                if re.search(r"type=[\"'](hidden|submit|button|checkbox|radio)[\"']", attrs, I):
                    continue
                if re.search(r"aria-label|aria-labelledby|\bid\s*=|title=", attrs, I):
                    continue
                inputs_unlabeled += 1
                ln = text.count("\n", 0, m.start()) + 1
                ev("inputs_without_label", f"{r}:{ln}")
        if ext == ".sql":
            for m in re.finditer(r"create table\s+(?:if not exists\s+)?\"?(?:public\.)?(\w+)", text, I):
                sql_tables.append((m.group(1), r))
            sql_rls += len(re.findall(r"enable row level security", text, I))

    # ---- derived signals -------------------------------------------------
    if third_parties:
        for v, info in sorted(third_parties.items()):
            if info["kind"] not in ("consent_manager", "international", "database"):
                ev("third_party", f"{v} ({info['kind']})")
    if "supabase" in signals and sql_tables:
        rls_tables = set()
        for path in all_files:
            if path.endswith(".sql"):
                for m in re.finditer(r"alter table\s+(?:if exists\s+)?\"?(?:public\.)?(\w+)\"?\s+enable row level security", read_text(path) or "", I):
                    rls_tables.add(m.group(1).lower())
        for t, r in sql_tables:
            if t.lower() not in rls_tables:
                ev("rls_missing", f"{r}: table `{t}` has no `enable row level security`")
    if "auth" not in signals and ("supabase" in signals or "firebase" in signals) and "user_accounts" in signals:
        ev("auth", "inferred from Supabase/Firebase + user tables")

    # ---- evaluate checks -------------------------------------------------
    results = []
    for cid, cat, title, triggers, sev, present in CHECKS:
        fired = [t for t in triggers if t in signals]
        # Accessibility checks only apply when the repo ships a user interface.
        if cid.startswith("A11Y") and "ui" not in signals:
            fired = []
        if not fired:
            results.append({"id": cid, "category": cat, "title": title, "status": "not-applicable",
                            "severity": None, "reasons": [], "evidence": []})
            continue
        severity = sev
        esc = [s for s in ESCALATE.get(cid, []) if s in signals]
        if esc and SEV_ORDER.index(severity) < len(SEV_ORDER) - 1:
            severity = SEV_ORDER[SEV_ORDER.index(severity) + 1]
        status = "likely-missing"
        present_evidence = []
        if present:
            if present.startswith("page:"):
                present_evidence = legal_pages.get(present[5:], [])
            else:
                present_evidence = signals.get(present, [])
            if present_evidence:
                status = "present-verify"
        if cid == "SEC-01":
            status = "likely-issue"
        if cid == "SEC-02":
            status = "likely-issue" if esc else "verify"
        if cid in ("PRV-11", "SEC-03", "SEC-04", "PRV-04", "PRV-05", "PRV-12", "A11Y-02", "CON-02") and status == "likely-missing":
            status = "verify"
        if cid in NEEDS_INPUT and status != "present-verify":
            status = "needs-input"
        if cid in ("A11Y-01", "A11Y-03", "A11Y-04", "CON-01", "CON-03", "CON-04", "PRV-11") and any(
                s in signals for s in ("img_missing_alt", "outline_removed", "clickable_div", "inputs_without_label",
                                       "prechecked_consent", "confirmshaming", "urgency", "claims", "pii_logging", "testimonials")
                if s in triggers):
            status = "likely-issue"
        if fired == ["ui"] and cid.startswith("A11Y") and cid != "A11Y-02":
            status = "verify"
            severity = "low"
        evidence = []
        for t in fired:
            if t == "ui":
                continue
            for e in signals[t][:3]:
                evidence.append(f"[{t}] {e}")
        results.append({
            "id": cid, "category": cat, "title": title, "status": status, "severity": severity,
            "reasons": fired, "evidence": evidence[:10], "present_evidence": present_evidence[:5],
        })

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, None: 9}
    results.sort(key=lambda c: (order[c["severity"]], c["id"]))

    report = {
        "tool": "launch-compliance/detect_signals.py",
        "version": "0.1.0",
        "repo": root,
        "files_scanned": scanned,
        "ui_files": ui_files,
        "stack": stack,
        "third_parties": {k: v for k, v in sorted(third_parties.items())},
        "legal_pages_found": {k: v for k, v in legal_pages.items()},
        "signals": {k: v for k, v in sorted(signals.items()) if k != "ui"},
        "counts": {"images_missing_alt": img_missing, "inputs_without_label": inputs_unlabeled,
                   "sql_tables": len(sql_tables), "rls_statements": sql_rls},
        "checks": results,
        "note": "Candidates only. Verify every finding by reading the code before reporting it.",
    }

    data = json.dumps(report, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(data)
    else:
        print(data)

    if args.md:
        applicable = [c for c in results if c["status"] != "not-applicable"]
        lines = [f"Stack: {', '.join(stack) or 'unknown'} | files scanned: {scanned}",
                 f"Third parties: {', '.join(third_parties) or 'none detected'}",
                 f"Applicable checks: {len(applicable)} / {len(results)}", ""]
        for c in applicable:
            lines.append(f"- [{(c['severity'] or '-').upper():8}] {c['id']:8} {c['status']:15} {c['title']}")
        print("\n".join(lines), file=sys.stderr)


if __name__ == "__main__":
    main()
