# Gate Configs — machine enforcement, verbatim

Provenance: star-training's stylelint gate (pre-commit) and EvairSIM's ripgrep design lint (CI).
Both configs below ran in production. The template copies live in `assets/`.

## The stylelint gate (CSS side)

`h5/.stylelintrc.json` — one rule, error level, Chinese remediation message:

```json
{
  "rules": {
    "color-no-hex": [
      true,
      {
        "severity": "error",
        "message": "禁止裸写 hex 颜色，请使用 theme.css 中的 CSS 变量（var(--color-*)）。如需新增色值，先在 theme.css 登记。"
      }
    ]
  },
  "overrides": [
    {
      "files": ["**/*.vue"],
      "customSyntax": "postcss-html"
    }
  ]
}
```

**The customSyntax trap (paid-for, 2026-08-11):** `customSyntax: postcss-html` must live ONLY inside
`overrides` scoped to `**/*.vue`. Declaring it top-level makes stylelint parse plain `.css` files
with the HTML syntax, where `color-no-hex` silently stops matching — the gate reports green while
enforcing nothing on `.css`. Symptom to watch for: `.vue` violations caught, `.css` violations pass.

`h5/.stylelintignore` — whitelist the SoT and build output only:

```
# theme.css 是设计 token 唯一真相源，允许在此定义 hex 色值
src/theme/theme.css
dist/
node_modules/
```

Scripts in the app's `package.json`:

```json
{
  "scripts": {
    "lint:css": "stylelint \"src/**/*.{css,vue}\"",
    "lint:css:fix": "stylelint \"src/**/*.{css,vue}\" --fix"
  },
  "devDependencies": {
    "postcss-html": "^2.0.0",
    "stylelint": "^17.14.1"
  }
}
```

## Pre-commit wiring (repo root `package.json`)

```json
{
  "scripts": {
    "prepare": "simple-git-hooks",
    "lint:css": "npm --prefix h5 run lint:css"
  },
  "simple-git-hooks": {
    "pre-commit": "npx lint-staged"
  },
  "lint-staged": {
    "h5/src/**/*.{css,vue}": "npm --prefix h5 exec -- stylelint --config h5/.stylelintrc.json --ignore-path h5/.stylelintignore"
  },
  "devDependencies": {
    "lint-staged": "^15.5.2",
    "simple-git-hooks": "^2.13.1"
  }
}
```

Staged-files-only keeps the hook fast (no full-repo scan); `npm install` at the root once installs
the hooks (`prepare`). Hooks are local-only enforcement — anyone can `--no-verify`; that is why CI
is the durable second layer, not a nicety.

## CI layer

Minimum viable job (fail-closed):

```yaml
# .github/workflows/ci.yml (excerpt)
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
  with: { node-version: 20 }
- run: npm ci --prefix h5
- run: npm --prefix h5 run lint:css
- run: node scripts/audit-styles.mjs h5   # covers the rgba blind spot below
```

EvairSIM additionally makes the CI **pull the H5 SoT and re-run the token sync; a diff in the
generated colorsets fails the build**, and a failed H5 fetch fails the job rather than skipping the
check — the opposite of "best effort". Copy that posture: any step that would be skipped on failure
must instead go red.

## The ripgrep lint pattern (non-CSS platforms / extra rules)

For layers stylelint can't see (Swift, or extra MUSTs), EvairSIM's `scripts/lint-design-system.sh`
implements `assert_no_match` — the pattern to steal:

```bash
set -euo pipefail
command -v rg >/dev/null 2>&1 || { echo "❌ ripgrep required" >&2; exit 1; }  # fail fast, never fake-green

assert_no_match() {  # pattern, path, message
  hits="$(rg -n --no-heading "$1" "$2" 2>/dev/null || true)"
  [ -z "$hits" ] && echo "✓ $3" || { echo "$hits" >&2; echo "❌ $3" >&2; exit 1; }
}

assert_no_match 'Color\('              "$FEATURES" 'No Color(...) in Features — use DesignTokens.Colors.*'
assert_no_match '\.font\(\.system\('   "$FEATURES" 'No .font(.system(...)) — use .evairTextStyle(...)'
```

Enforced MUSTs there: no `Color(...)`, no `.font(.system(size:))`, no raw `padding(N)`/`spacing: N`,
no bare `ProgressView`, icon sizes only via `.evairSymbolSize()` (never typography tokens). Each
message says the fix, not just the crime.

## Known gate blind spots (enforce out-of-band)

1. **`rgba()`/`hsl()` literals** — `color-no-hex` only matches hex. One production leak survived a
   green lint: `drop-shadow(0 4px 12px rgba(0,0,0,0.12))`. Countermeasure: `audit-styles.mjs` flags
   literal-number rgba/hsl outside the SoT; run it in CI alongside stylelint.
2. **Inline `style="…#fff…"` in templates** — stylelint sees `<style>` blocks, not attributes.
   (`:style` bindings that set custom properties like `--i` are legitimate; only color literals
   violate.)
3. **JS-side colors** (share cards, canvas, echarts defaults) — invisible to CSS lints. Audit
   script scans `.js/.ts` for hex assigned to color-ish keys; treat as report-only until volume
   justifies a token import path.

## Gate self-test (do this, observe it, record it)

```bash
echo '.probe { color: #abcdef; }' >> src/styles/base.css
npm --prefix h5 run lint:css; echo "exit=$?"   # MUST be non-zero
git checkout -- src/styles/base.css
npm --prefix h5 run lint:css; echo "exit=$?"   # MUST be zero
```

A gate whose failure has never been observed is unverified. If the self-test stays green, stop and
diagnose (customSyntax trap, wrong ignore path, rule typo) before proceeding — see the
no-weakening rule in SKILL.md Mutation safety.
