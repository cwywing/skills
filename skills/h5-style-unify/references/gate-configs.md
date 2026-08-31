# Gate Configs — machine enforcement, verbatim

Provenance: production H5 stylelint gate (pre-commit) and the sibling iOS ripgrep design lint (CI).
Both ran in production. Templates live in `assets/`. Paths below use `<app-root>` — substitute the
directory confirmed in P0; do not assume a `h5/` prefix.

## The stylelint gate (CSS side)

`<app-root>/.stylelintrc.json` — one rule, error level, Chinese remediation message (copy from
`assets/stylelintrc.json.tmpl`):

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

**The customSyntax trap:** `customSyntax: postcss-html` must live ONLY inside `overrides` scoped to
`**/*.vue`. Declaring it top-level makes stylelint parse plain `.css` with the HTML syntax, where
`color-no-hex` silently stops matching — the gate reports green while enforcing nothing on `.css`.
Symptom: `.vue` violations caught, `.css` violations pass.

`<app-root>/.stylelintignore` — whitelist the SoT and build output only:

```
# theme.css 是设计 token 唯一真相源，允许在此定义 hex 色值
src/theme/theme.css
dist/
node_modules/
```

Scripts in `<app-root>/package.json`:

```json
{
  "scripts": {
    "lint:css": "stylelint \"src/**/*.{css,vue,scss}\"",
    "lint:css:fix": "stylelint \"src/**/*.{css,vue,scss}\" --fix"
  },
  "devDependencies": {
    "postcss-html": "^1.8.0",
    "stylelint": "^16.0.0"
  }
}
```

Pin versions to whatever the repo already uses. stylelint 16+ is the floor; 17 is ESM-only and needs
Node ≥ 20.19. Do not copy a major version from this file if the app is already on another.

## Pre-commit wiring (repo or app package.json)

Staged-files-only keeps the hook fast. Substitute `<app-root>` (`.` if the app *is* the repo root):

```json
{
  "scripts": {
    "prepare": "simple-git-hooks"
  },
  "simple-git-hooks": {
    "pre-commit": "npx lint-staged"
  },
  "lint-staged": {
    "<app-root>/src/**/*.{css,vue}": "npx stylelint --config <app-root>/.stylelintrc.json --ignore-path <app-root>/.stylelintignore"
  }
}
```

Hooks are local-only — anyone can `--no-verify`. CI is the durable second layer.

## CI layer

Minimum viable job (fail-closed). Copy `audit-styles.mjs` into the repo (or invoke it from the
skill path in agent runs):

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
  with: { node-version: 20 }
- run: npm ci
  working-directory: <app-root>
- run: npm run lint:css
  working-directory: <app-root>
- run: node scripts/audit-styles.mjs .
  working-directory: <app-root>
```

Any step that would be skipped on failure must instead go red. The sibling iOS job that pulls the
H5 SoT and diffs generated colorsets is owned by `swiftui-style-unify`.

## Known gate blind spots (audit script covers these; stylelint does not)

1. **`rgba()` / `hsl()` literals** — `color-no-hex` only matches hex.
2. **Inline `style="…#fff…"` in templates** — stylelint sees `<style>` blocks, not attributes.
3. **Tailwind / Uno arbitrary values** — `bg-[#1677ff]` bypasses stylelint; `audit-styles.mjs` flags them.
4. **Vue SFC `<script>` color literals** — treated as errors even in multiline objects (`primary: '#fff'` with no color-ish key on the same line). `querySelector('#id')` / `getElementById('id')` arguments are exempt; leftover hex-like strings go in the audit leftovers, do not delete the rule.
5. **Standalone `.js/.ts` color literals** — report-only (`warn`) until `--strict`.

## Gate self-test (do this, observe it, record it)

```bash
echo '.probe { color: #abcdef; }' >> src/styles/base.css
npx stylelint "src/**/*.{css,vue}" ; echo "exit=$?"   # MUST be non-zero
git checkout -- src/styles/base.css
npx stylelint "src/**/*.{css,vue}" ; echo "exit=$?"   # MUST be zero
```

Run from `<app-root>`. A gate whose failure has never been observed is unverified. If the self-test
stays green, stop and diagnose (customSyntax trap, wrong ignore path, rule typo) — see SKILL.md
Mutation safety, no-weakening rule.
