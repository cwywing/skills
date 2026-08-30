#!/usr/bin/env bash
# audit-swift-styles.sh — SwiftUI design-system gate.
#
# Generalized from a production lint (EvairSIM scripts/lint-design-system.sh). Polices
# the Features layer with ripgrep MUST-NOTs and checks that Color("...") appears only in
# the tokens file. Fail-closed: missing rg FAILS (never fake-green — the original bug
# this gate exists to prevent); violations exit 1; usage errors exit 2.
#
# Usage:
#   ./audit-swift-styles.sh <repo-root> [--features <dir>] [--tokens <ColorTokens.swift>]
#                           [--style-mod <name>] [--report]
#
#   --features   Features dir (default: deepest dir named "Features" under repo-root)
#   --tokens     color tokens file (default: file defining Color(" first found under a
#                Theme/Tokens dir; repo-wide Color(" rule excludes it)
#   --style-mod  text-style modifier name (default: evairTextStyle) — multiline
#                Image-sizing anti-pattern uses it
#   --report     also print structural facts (adoption counts) without failing on them

set -euo pipefail

fail() { echo "❌ Design System lint failed: $1" >&2; exit 1; }
usage_exit() { echo "usage: $0 <repo-root> [--features <dir>] [--tokens <file>] [--style-mod <name>] [--report]" >&2; exit 2; }

ROOT="" FEATURES="" TOKENS="" STYLE_MOD="evairTextStyle" REPORT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --features)  FEATURES="$2"; shift 2 ;;
    --tokens)    TOKENS="$2"; shift 2 ;;
    --style-mod) STYLE_MOD="$2"; shift 2 ;;
    --report)    REPORT=1; shift ;;
    -h|--help)   usage_exit ;;
    *) if [[ -z "$ROOT" ]]; then ROOT="$1"; shift; else usage_exit; fi ;;
  esac
done
[[ -n "$ROOT" ]] || usage_exit
ROOT="$(cd "$ROOT" 2>/dev/null && pwd)" || usage_exit

# --- fail fast on the dependency (the false-green lesson) ---
command -v rg >/dev/null 2>&1 || fail "ripgrep (rg) is required — install: brew install ripgrep (macOS) / sudo apt-get install -y ripgrep (CI)"

# --- auto-detect ---
if [[ -z "$FEATURES" ]]; then
  FEATURES="$(find "$ROOT" -type d -name Features -not -path '*/.git/*' -not -path '*/Pods/*' -not -path '*/.build/*' 2>/dev/null | head -1 || true)"
fi
[[ -n "$FEATURES" ]] || fail "no Features directory found under $ROOT — pass --features <dir>"
if [[ -z "$TOKENS" ]]; then
  TOKENS="$(find "$ROOT" -type f -name '*.swift' -path '*Tokens*' -not -path '*/.build/*' 2>/dev/null | xargs -r grep -l 'Color("' 2>/dev/null | head -1 || true)"
fi

echo "SwiftUI style audit — $ROOT"
echo "  features: $FEATURES"
echo "  tokens:   ${TOKENS:-<none found — Color(\"...\") rule will apply repo-wide>}"
echo "  rg:       $(command -v rg)"
echo

matches() { rg -n --no-heading "$@" 2>/dev/null || true; }
assert_no_match() { # pattern path message [extra rg args...]
  local pattern="$1" path="$2" message="$3"; shift 3
  local hits; hits="$(matches "$pattern" "$path" "$@")"
  if [[ -n "$hits" ]]; then echo "$hits" >&2; fail "$message"; fi
  echo "✓ $message"
}

echo "— Feature styling guardrails —"
assert_no_match 'Color\(' "$FEATURES" 'No Color(...) in Features — use DesignTokens.Colors.*'
assert_no_match '\.font\(\.system\(' "$FEATURES" "No .font(.system(...)) in Features — use .${STYLE_MOD}(DesignTokens.Typography.*)"
assert_no_match 'cornerRadius\(\s*[0-9]' "$FEATURES" 'No numeric cornerRadius(...) in Features — use DesignTokens.Radius.*'
assert_no_match 'padding\(\s*[0-9]' "$FEATURES" 'No padding(literal) in Features — use DesignTokens.Spacing.*'
assert_no_match 'padding\(\.[a-zA-Z]+,\s*[0-9]' "$FEATURES" 'No padding(.edge, literal) in Features — use DesignTokens.Spacing.*'
assert_no_match 'spacing:\s*[0-9]' "$FEATURES" 'No spacing: N in Features — use DesignTokens.Spacing.*'
assert_no_match '\.shadow\(' "$FEATURES" 'No raw .shadow(...) in Features — use Theme components / token shadow modifiers'
assert_no_match 'frame\((width|height):\s*[0-9]' "$FEATURES" 'No frame(width|height: N) in Features — use DesignTokens.Metrics.* or components'
assert_no_match 'lineWidth:\s*[0-9]' "$FEATURES" 'No lineWidth: N in Features — use DesignTokens.Metrics.*'
assert_no_match 'MetricsTokens' "$FEATURES" 'Features must use DesignTokens.Metrics.* — not MetricsTokens directly'

echo
echo "— Component adoption (Features must use Theme wrappers) —"
assert_no_match 'ProgressView\(' "$FEATURES" 'No ProgressView in Features — use the Theme progress component'
assert_no_match 'ContentUnavailableView' "$FEATURES" 'No ContentUnavailableView in Features — use the Theme empty-state component'
assert_no_match '\bToggle\(' "$FEATURES" 'No raw Toggle in Features — use the Theme toggle component'

echo
echo "— Repo-wide policy —"
if [[ -n "$TOKENS" ]]; then
  # rg globs: LATER globs take precedence — whitelist first, exclusion last, or the
  # exclusion is silently overridden and the tokens file itself gets flagged.
  # (And expand the basename BEFORE quoting — a $( ) inside single quotes stays literal.)
  TOKENS_BASE="$(basename "$TOKENS")"
  assert_no_match 'Color\("' "$ROOT" "Color(\"...\") only allowed in $TOKENS" -g '*.swift' -g "!**/${TOKENS_BASE}"
else
  assert_no_match 'Color\("' "$ROOT" 'Color("...") found but no tokens file detected — pass --tokens <file>' -g '*.swift'
fi

# Multiline: sizing an Image with a text-style modifier (smuggles lineHeight/tracking into an image)
if hits="$(rg -n -U --no-heading "Image\(systemName:[^\n]*\)\n\s*\.${STYLE_MOD}" "$FEATURES" --glob '*.swift' 2>/dev/null || true)" && [[ -n "$hits" ]]; then
  echo "$hits" >&2
  fail "No .${STYLE_MOD} on Image — use a symbol-size token (DesignTokens.Metrics.*)"
fi
echo "✓ No .${STYLE_MOD} on Image — use a symbol-size token (DesignTokens.Metrics.*)"

if [[ "$REPORT" -eq 1 ]]; then
  echo
  echo "— Structural report (informational) —"
  for t in DesignTokens EvairTextStyle; do
    f="$(find "$ROOT" -type f -name "$t.swift" -not -path '*/.build/*' 2>/dev/null | head -1 || true)"
    echo "  $t.swift: ${f:-NOT FOUND}"
  done
  echo "  DesignTokens. uses in Features: $(matches --count-matches 'DesignTokens\.' "$FEATURES" --glob '*.swift' | awk -F: '{s+=$NF} END {print s+0}')"
  echo "  ${STYLE_MOD} uses in Features:  $(matches --count-matches "\.${STYLE_MOD}\(" "$FEATURES" --glob '*.swift' | awk -F: '{s+=$NF} END {print s+0}')"
fi

echo
echo "PASS — SwiftUI style gate clean (fail-closed)"
