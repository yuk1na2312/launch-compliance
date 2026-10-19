# Accessibility checks (A11Y)

Target: WCAG 2.2 level AA. Accessibility is legally required in many contexts (the European Accessibility Act for many consumer digital services in the EU since June 2025, ADA litigation in the US, public-sector rules elsewhere), and it is a frequent source of demand letters for small sites.

Static scanning catches a subset. When the app can run locally, recommend (or run, if tools are available) an automated pass with axe-core or Lighthouse, and say what still needs manual testing.

---

## A11Y-01 Alt text on images — Medium (High when missing)

**Verify.** Every `<img>`, `<Image>`, `<svg>` used as content, and CSS background image that conveys meaning. The scanner counts tags without `alt`. Also check for useless alt text (`alt="image"`, filenames) and decorative images that should have `alt=""`.

**Pass when** meaningful images have descriptive alt text, decorative ones have `alt=""` (or `aria-hidden` for inline SVG), and icon-only buttons have an `aria-label`.

**Fix.** Write alt text from context (surrounding copy, component name, filename); mark decorative images with empty alt. Ask the user only when the image's meaning can't be inferred.

---

## A11Y-02 Color contrast — Medium

**Verify.** Collect the color tokens (Tailwind config, CSS variables, theme files) and the foreground/background pairs actually used for text and controls, including placeholder text, disabled-looking-but-enabled states, text on images, and dark mode. Compute contrast ratios.

**Pass when** normal text is at least 4.5:1, large text (≥24px, or ≥18.66px bold) at least 3:1, and UI component boundaries and focus indicators at least 3:1 against adjacent colors.

**Fix.** Adjust the token values, not individual usages, so the fix propagates. Show before/after ratios in the report. Keep the brand hue; change lightness.

---

## A11Y-03 Keyboard navigation, visible focus, page language — Medium (High when found)

**Verify.**
- `outline: none` / `focus:outline-none` without a replacement `focus-visible` style
- Clickable `div`/`span` (`onClick` without `role="button"`, `tabIndex={0}`, and Enter/Space handling); use a `<button>` instead
- Positive `tabIndex` values that break tab order
- Modals and menus: focus moves in, is trapped while open, Escape closes, focus returns to the trigger
- Skip-to-content link on pages with long navigation
- `<html>` without `lang`

**Pass when** every interactive element is reachable and operable by keyboard in a logical order, with a clearly visible focus indicator, and the page language is set.

**Fix.** Replace clickable divs with `<button>`/`<a>`; add a global `:focus-visible` style; remove positive tabindex; use the UI library's accessible dialog/menu primitives (Radix, Headless UI, shadcn/ui, etc.) instead of hand-rolled ones; add `lang` to `<html>`.

---

## A11Y-04 Form fields have labels — Medium

**Verify.** Each input/select/textarea has a programmatic label (`<label for>`, wrapping `<label>`, `aria-label`, or `aria-labelledby`). Placeholder text alone is not a label. Errors are announced (`aria-describedby`, `aria-invalid`) and not conveyed by color alone. Required fields are indicated in text.

**Pass when** every field has a visible label (or an accessible name for icon-only search fields) and errors are text-based and associated with their field.

**Fix.** Add `<label>` elements tied to inputs; associate error messages with `aria-describedby`; add `autocomplete` attributes for personal data fields (`email`, `name`, `tel`), which WCAG 2.2 also asks for.
