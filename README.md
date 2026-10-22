# LaunchCompliance

**Repo-aware launch compliance for apps built fast.** LaunchCompliance is a set of portable agent skills, packaged as a Claude Code plugin, that reads your codebase, works out what personal data the app collects and which third parties it sends it to, and tells you which privacy, legal, consumer-protection and accessibility pieces you are missing, with `file:line` evidence and fixes.

Vibe-coded apps ship in a weekend and skip this layer entirely: no privacy policy, Google Analytics firing before consent, a Supabase service-role key in the browser, tables without Row Level Security, fake testimonials from the template. LaunchCompliance catches these before your users (or a regulator) do.

> ⚠️ LaunchCompliance is a developer checklist, not legal advice.

## What it checks

31 checks in five groups. Each one only runs when the code gives a reason for it (payments → refund policy, Resend → unsubscribe links, Supabase → RLS, and so on).

| ID | Check | Triggered by |
|---|---|---|
| **Privacy & data** | | |
| PRV-01 | Privacy policy | any personal data |
| PRV-02 | Cookie policy | cookies, analytics, ads, widgets |
| PRV-03 | Consent banner that actually blocks trackers before opt-in | analytics, ads, session replay |
| PRV-04 | Consent and purpose text on forms | email/PII forms, newsletters |
| PRV-05 | Data minimization | DOB, phone, address, ID fields |
| PRV-06 | Third-party SDK audit & sub-processor list | any third-party SDK |
| PRV-07 | Age gate / children's data | kids audience, DOB fields |
| PRV-08 | Account & data deletion | user accounts |
| PRV-09 | Data access & export | user accounts |
| PRV-10 | Data retention | databases |
| PRV-11 | No personal data in logs / error reports | PII in logs, Sentry etc. |
| PRV-12 | AI provider data-sharing disclosure | OpenAI, Anthropic, Gemini, ... |
| PRV-13 | Session replay masking | Hotjar, Clarity, LogRocket, ... |
| **Code-level leaks** | | |
| SEC-01 | Secrets exposed to client or committed | `NEXT_PUBLIC_*SECRET*`, `sk_live_`, `.env` |
| SEC-02 | Supabase RLS / Firebase rules | Supabase, Firebase |
| SEC-03 | API routes don't return other users' data | auth + API routes |
| SEC-04 | Uploaded files not publicly listable | uploads, storage |
| **Legal & commercial** | | |
| LEG-01 | Terms of service | accounts, payments, UGC |
| LEG-02 | Refund policy | payments |
| LEG-03 | Business details & contact | payments, international |
| LEG-04 | Easy subscription cancellation | subscriptions |
| LEG-05 | Licensed fonts, images, assets | UI, local fonts, stock images |
| **Consumer protection** | | |
| CON-01 | No dark patterns | pre-ticked boxes, fake urgency, confirmshaming |
| CON-02 | No hidden fees / drip pricing | payments, added fees |
| CON-03 | No fake or unverifiable reviews | hardcoded testimonials |
| CON-04 | No unsupported claims | "GDPR compliant", "100% secure", "#1" |
| CON-05 | Unsubscribe link in marketing emails | email providers |
| **Accessibility (WCAG 2.2 AA)** | | |
| A11Y-01 | Alt text | images |
| A11Y-02 | Color contrast | UI |
| A11Y-03 | Keyboard navigation, focus, page language | UI |
| A11Y-04 | Form labels | forms |

Detected stacks include Next.js, React, Vue/Nuxt, Svelte/SvelteKit, Astro, Remix, Express, NestJS, React Native/Expo, Flutter, Django, Flask, FastAPI, Spring Boot (Maven/Gradle), Laravel and Rails.

## Install

### Claude Code

```bash
# inside Claude Code
/plugin marketplace add yuk1na2312/launch-compliance
/plugin install launch-compliance@launch-compliance
```

or from your shell:

```bash
claude plugin marketplace add yuk1na2312/launch-compliance
claude plugin install launch-compliance@launch-compliance
```

### Claude apps (claude.ai / desktop)

Zip a skill folder (`plugins/launch-compliance/skills/audit` and/or `.../policy-docs`) and upload it as a custom skill. You can then ask Claude to audit a repo you've connected or uploaded.

### Other coding agents

The two skills follow the open [Agent Skills](https://agentskills.io) layout: YAML `name` + `description` frontmatter in `SKILL.md`, with `references/` and `scripts/` resolved relative to the skill folder. They work as-is in OpenCode, Codex CLI, Cursor, GitHub Copilot, Gemini CLI and other agents that read `SKILL.md`; installing means putting the whole `audit` and `policy-docs` folders in that agent's skills directory.

| Agent | Project-level | User-level | Docs |
|---|---|---|---|
| OpenCode | `.opencode/skills/` | `~/.config/opencode/skills/` | [skills](https://opencode.ai/v2/docs/skills) |
| Codex CLI | `.agents/skills/` | `~/.agents/skills/` | [skills](https://developers.openai.com/codex/skills) |
| Cursor | `.agents/skills/` or `.cursor/skills/` | `~/.agents/skills/` or `~/.cursor/skills/` | [skills](https://cursor.com/docs/context/skills) |
| GitHub Copilot | `.github/skills/` or `.agents/skills/` | `~/.copilot/skills/` or `~/.agents/skills/` | [skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` | [skills](https://geminicli.com/docs/cli/skills/) |

`.agents/skills/` is read by every agent in the table except OpenCode, so it is the simplest single target if you use more than one. Run the command from the root of the app you want to audit, set `SRC` to the `skills` folder of this repository, and set `SKILLS` to a directory from the table. Symlinks keep the installed skills in sync with the checkout; copy instead if your agent does not follow symlinks.

```bash
SRC=/path/to/launch-compliance/plugins/launch-compliance/skills
SKILLS=.agents/skills                      # or any directory from the table, e.g. .opencode/skills
mkdir -p "$SKILLS"
for s in audit policy-docs; do ln -s "$SRC/$s" "$SKILLS/$s"; done
```

Anywhere symlinks are not an option, replace `ln -s` with `cp -R` in the loop. On Windows, symlinks need Developer Mode or an elevated shell, so copy the folders instead; set `$src` and `$dest` to the same source and project or user directory:

```powershell
$src  = "C:\path\to\launch-compliance\plugins\launch-compliance\skills"
$dest = ".opencode\skills"                          # project-level
# $dest = "$HOME\.config\opencode\skills"           # user-level instead

New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item -Recurse "$src\audit", "$src\policy-docs" $dest
```

Restart the agent, or start a new session, after installing. Codex CLI, Cursor, Copilot and Gemini CLI also read the shared `~/.agents/skills` user directory.

#### Agents without skill support

If an agent has no skills directory, add one line to the project's `AGENTS.md` that points at the `SKILL.md` path:

```markdown
Before launch, privacy, payments, auth or legal-page work, read and follow `/path/to/launch-compliance/plugins/launch-compliance/skills/audit/SKILL.md`.
```

Use the absolute path, or a path relative to your app. The skill runs the scanner from its own folder, so no other install step is needed.

### The scanner on its own

The scanner is a single Python file with no dependencies:

```bash
python3 plugins/launch-compliance/skills/audit/scripts/detect_signals.py path/to/your-app --md
```

It prints a prioritized candidate list and can write JSON (`--out signals.json`). The candidates are unverified; the skill does the verification.

## Use

In Claude Code, from your project:

```
/launch-compliance:audit
```

or just ask: *"Is this app ready to launch? Check privacy and compliance."*

In other agents, ask the same question in plain language, or invoke the skill by name: `$audit` in Codex CLI, `/audit` in Cursor, `@audit` in OpenCode, and automatic activation elsewhere when the task matches the description.

The agent will:

1. **Scan** - run the signal detector over dependencies and source
2. **Verify** - read the evidence for every candidate and drop false positives
3. **Report** - write `.launch-compliance/REPORT.md` with launch blockers, a data inventory, a third-party table, and findings by severity
4. **Fix** - on your go-ahead (`fix SEC-01 PRV-03` or `fix all critical`), make small, reviewable changes in your stack's conventions

To draft legal pages from what the code actually does:

```
/launch-compliance:policy-docs
```

In other agents, invoke `policy-docs` the same way as `audit`.

It builds a facts sheet from the code (data fields, vendors, cookies, payments, AI usage), asks you only for business facts it can't know, then writes the privacy policy, terms, refund and cookie pages into your project and links them in the footer.

## Example

`examples/vibe-app` is a deliberately broken Next.js + Supabase + Stripe + Resend + OpenAI app. Scanner output:

```
Stack: Next.js, React | files scanned: 10
Third parties: Stripe, Supabase, Resend, PostHog, Sentry, OpenAI, Google Analytics / GTM, Meta Pixel, Supabase Auth
Applicable checks: 29 / 31

- [CRITICAL] PRV-01   likely-missing  Privacy policy
- [CRITICAL] PRV-03   likely-missing  Cookie consent banner that blocks non-essential scripts until opt-in
- [CRITICAL] SEC-01   likely-issue    No secrets exposed in client code or committed files
- [CRITICAL] SEC-02   likely-issue    Database access rules (Supabase RLS / Firebase rules)
- [HIGH    ] CON-01   likely-issue    No dark patterns
- [HIGH    ] CON-03   likely-issue    No fake or unverifiable reviews/testimonials
...
```

## Repository layout

```
launch-compliance/
├── .claude-plugin/marketplace.json     → makes the repo installable as a plugin source
├── plugins/launch-compliance/
│   ├── .claude-plugin/plugin.json      → plugin name, version, author
│   └── skills/
│       ├── audit/                      → main skill (/launch-compliance:audit)
│       │   ├── SKILL.md                → instructions: scan → verify → report → fix
│       │   ├── scripts/detect_signals.py → scanner, plain Python, no dependencies
│       │   └── references/
│       │       ├── checks-privacy.md      PRV-01..13
│       │       ├── checks-security.md     SEC-01..04
│       │       ├── checks-legal.md        LEG-01..05
│       │       ├── checks-consumer.md     CON-01..05
│       │       ├── checks-accessibility.md A11Y-01..04
│       │       ├── jurisdictions.md       what changes per country
│       │       ├── signals.md             manual fallback if Python isn't available
│       │       └── report-template.md     format of REPORT.md
│       └── policy-docs/                → second skill (/launch-compliance:policy-docs)
│           ├── SKILL.md                → drafts privacy/terms/refund/cookie pages
│           └── references/             → facts sheet + document outlines
├── examples/vibe-app/                  → broken demo app for testing
└── README, CONTRIBUTING, LICENSE
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New checks need: an ID, a trigger in `detect_signals.py`, and a Why / Verify / Pass when / Fix entry in the matching reference file. Please include a fixture in `examples/` that triggers it.

## License

[MIT](LICENSE)
