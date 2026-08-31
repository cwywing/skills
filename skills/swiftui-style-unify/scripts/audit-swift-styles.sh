#!/usr/bin/env bash
# audit-swift-styles.sh — SwiftUI design-system gate.
#
# Polices the business-view layer with ripgrep MUST-NOTs and checks that
# Color("...") appears only in the tokens file. Fail-closed: missing rg FAILS
# (never fake-green). Collects ALL rule hits, then exits 1 if any error-level
# violation exists — Phase 1 baseline counts need a full report, not fail-fast.
#
# Usage:
#   ./audit-swift-styles.sh <repo-root> [--features <dir>] [--tokens <ColorTokens.swift>]
#                           [--style-mod <name>] [--components] [--report]
#
#   --features    Business-view dir. Auto-detect: a directory named Features, else
#                 App, else repo-root (Theme/ and *Tokens.swift excluded from scan).
#   --tokens      Color tokens file (default: first *.swift under a *Tokens* path
#                 that contains Color(" ). Repo-wide Color(" rule excludes it.
#   --style-mod   Text-style modifier name (default: textStyle).
#   --components  Promote ProgressView / Toggle / ContentUnavailableView to errors.
#                 Off by default so the gate can be installed before wrappers exist.
#   --report      Print adoption counts (also printed on every run; flag kept for
#                 callers that already pass it).
#
# Exit: 0 clean; 1 violations; 2 usage / missing repo.

set -euo pipefail

fail_dep() { echo "ERROR: $1" >&2; exit 1; }
usage_exit() { echo "usage: $0 <repo-root> [--features <dir>] [--tokens <file>] [--style-mod <name>] [--components] [--report]" >&2; exit 2; }

ROOT="" FEATURES="" TOKENS="" STYLE_MOD="textStyle" COMPONENTS=0 REPORT=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --features)   FEATURES="$2"; shift 2 ;;
    --tokens)     TOKENS="$2"; shift 2 ;;
    --style-mod)  STYLE_MOD="$2"; shift 2 ;;
    --components) COMPONENTS=1; shift ;;
    --report)     REPORT=1; shift ;;
    -h|--help)    usage_exit ;;
    *) if [[ -z "$ROOT" ]]; then ROOT="$1"; shift; else usage_exit; fi ;;
  esac
done
[[ -n "$ROOT" ]] || usage_exit
ROOT="$(cd "$ROOT" 2>/dev/null && pwd)" || usage_exit

command -v rg >/dev/null 2>&1 || fail_dep "ripgrep (rg) is required — install: brew install ripgrep (macOS) / sudo apt-get install -y ripgrep (CI)"

# Portable: first matching directory, no GNU find -quit, no xargs -r.
first_dir_named() {
  local name="$1" found=""
  while IFS= read -r d; do
    found="$d"
    break
  done < <(find "$ROOT" -type d -name "$name" \
            -not -path '*/.git/*' -not -path '*/Pods/*' -not -path '*/.build/*' \
            -not -path '*/DerivedData/*' 2>/dev/null)
  printf '%s' "$found"
}

first_tokens_file() {
  local found=""
  while IFS= read -r f; do
    if rg -l --fixed-strings 'Color("' "$f" >/dev/null 2>&1; then
      found="$f"
      break
    fi
  done < <(find "$ROOT" -type f -name '*.swift' -path '*Tokens*' \
            -not -path '*/.build/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' 2>/dev/null)
  printf '%s' "$found"
}

if [[ -z "$FEATURES" ]]; then
  FEATURES="$(first_dir_named Features)"
  if [[ -z "$FEATURES" ]]; then
    FEATURES="$(first_dir_named App)"
  fi
  if [[ -z "$FEATURES" ]]; then
    FEATURES="$ROOT"
  fi
fi
if [[ -z "$TOKENS" ]]; then
  TOKENS="$(first_tokens_file)"
fi

echo "SwiftUI style audit — $ROOT"
echo "  views:    $FEATURES"
echo "  tokens:   ${TOKENS:-<none found — Color(\"...\") rule will apply repo-wide>}"
echo "  style-mod .${STYLE_MOD}  components=$([[ "$COMPONENTS" -eq 1 ]] && echo on || echo warn-only)"
echo "  rg:       $(command -v rg)"
echo

ERROR_COUNT=0
WARN_COUNT=0
RULE_ERRORS=0

# Business-layer globs: skip the token/theme implementation and package noise.
# Later globs win in rg — keep the exclusion AFTER the include.
VIEW_GLOBS=( --glob '*.swift' --glob '!**/Theme/**' --glob '!**/*Tokens.swift' --glob '!**/.build/**' --glob '!**/Pods/**' --glob '!**/DerivedData/**' )

matches() { rg -n --no-heading "$@" 2>/dev/null || true; }

count_lines() {
  local s="$1"
  if [[ -z "$s" ]]; then echo 0; else printf '%s\n' "$s" | wc -l | tr -d ' '; fi
}

check() {
  # check <error|warn> <pattern> <path> <message> [extra rg args]
  local level="$1" pattern="$2" path="$3" message="$4"
  shift 4
  local hits n
  hits="$(matches "$pattern" "$path" "$@")"
  n="$(count_lines "$hits")"
  if [[ -n "$hits" ]]; then
    if [[ "$level" == "error" ]]; then
      echo "✖ ×${n}  $message"
      printf '%s\n' "$hits"
      ERROR_COUNT=$((ERROR_COUNT + n))
      RULE_ERRORS=$((RULE_ERRORS + 1))
    else
      echo "⚠ ×${n}  $message"
      printf '%s\n' "$hits"
      WARN_COUNT=$((WARN_COUNT + n))
    fi
    echo
  else
    echo "✓ $message"
  fi
}

echo "— View-layer value rules —"
check error 'Color\(' "$FEATURES" 'No Color(...) in views — use DesignTokens.Colors.*' "${VIEW_GLOBS[@]}"
# size: only — .font(.system(.body)) is Apple Dynamic Type and is allowed
check error '\.font\(\.system\(size:' "$FEATURES" "No .font(.system(size:)) in views — use .${STYLE_MOD}(DesignTokens.Typography.*)" "${VIEW_GLOBS[@]}"
check error 'cornerRadius\(\s*[0-9]' "$FEATURES" 'No numeric cornerRadius(...) in views — use DesignTokens.Radius.*' "${VIEW_GLOBS[@]}"
check error 'padding\(\s*[0-9]' "$FEATURES" 'No padding(literal) in views — use DesignTokens.Spacing.*' "${VIEW_GLOBS[@]}"
check error 'padding\(\.[a-zA-Z]+,\s*[0-9]' "$FEATURES" 'No padding(.edge, literal) in views — use DesignTokens.Spacing.*' "${VIEW_GLOBS[@]}"
check error 'spacing:\s*[0-9]' "$FEATURES" 'No spacing: N in views — use DesignTokens.Spacing.*' "${VIEW_GLOBS[@]}"
check error '\.shadow\(' "$FEATURES" 'No raw .shadow(...) in views — use Theme components / token shadow modifiers' "${VIEW_GLOBS[@]}"
check error 'frame\((width|height):\s*[0-9]' "$FEATURES" 'No frame(width|height: N) in views — use DesignTokens.Metrics.* or components' "${VIEW_GLOBS[@]}"
check error 'lineWidth:\s*[0-9]' "$FEATURES" 'No lineWidth: N in views — use DesignTokens.Metrics.*' "${VIEW_GLOBS[@]}"
check error 'MetricsTokens' "$FEATURES" 'Views must use DesignTokens.Metrics.* — not MetricsTokens directly' "${VIEW_GLOBS[@]}"

echo
echo "— Component wrappers (warn until --components) —"
COMP_LEVEL="warn"
[[ "$COMPONENTS" -eq 1 ]] && COMP_LEVEL="error"
check "$COMP_LEVEL" 'ProgressView\(' "$FEATURES" 'No ProgressView in views — use the Theme progress component' "${VIEW_GLOBS[@]}"
check "$COMP_LEVEL" 'ContentUnavailableView' "$FEATURES" 'No ContentUnavailableView in views — use the Theme empty-state component' "${VIEW_GLOBS[@]}"
check "$COMP_LEVEL" '\bToggle\(' "$FEATURES" 'No raw Toggle in views — use the Theme toggle component' "${VIEW_GLOBS[@]}"

echo
echo "— Repo-wide policy —"
if [[ -n "$TOKENS" ]]; then
  TOKENS_BASE="$(basename "$TOKENS")"
  # include first, exclusion last — later globs take precedence
  check error 'Color\("' "$ROOT" "Color(\"...\") only allowed in $TOKENS" --glob '*.swift' --glob "!**/${TOKENS_BASE}"
else
  check error 'Color\("' "$ROOT" 'Color("...") found but no tokens file detected — pass --tokens <file>' --glob '*.swift'
fi

hits="$(rg -n -U --no-heading "Image\(systemName:[^\n]*\)\n\s*\.${STYLE_MOD}" "$FEATURES" "${VIEW_GLOBS[@]}" 2>/dev/null || true)"
n="$(count_lines "$hits")"
if [[ -n "$hits" ]]; then
  echo "✖ ×${n}  No .${STYLE_MOD} on Image — use DesignTokens.Metrics.* for symbol size"
  printf '%s\n' "$hits"
  ERROR_COUNT=$((ERROR_COUNT + n))
  RULE_ERRORS=$((RULE_ERRORS + 1))
else
  echo "✓ No .${STYLE_MOD} on Image — use DesignTokens.Metrics.* for symbol size"
fi

echo
echo "— Structural report —"
for t in DesignTokens TextStyle; do
  f=""
  while IFS= read -r p; do f="$p"; break; done < <(find "$ROOT" -type f -name "$t.swift" -not -path '*/.build/*' 2>/dev/null)
  echo "  $t.swift: ${f:-NOT FOUND}"
done
echo "  DesignTokens. uses in views: $(matches --count-matches 'DesignTokens\.' "$FEATURES" "${VIEW_GLOBS[@]}" | awk -F: '{s+=$NF} END {print s+0}')"
echo "  .${STYLE_MOD}( uses in views: $(matches --count-matches "\.${STYLE_MOD}\(" "$FEATURES" "${VIEW_GLOBS[@]}" | awk -F: '{s+=$NF} END {print s+0}')"
echo "  errors: ${ERROR_COUNT}   warnings: ${WARN_COUNT}   failed-rules: ${RULE_ERRORS}"

if [[ "$ERROR_COUNT" -gt 0 ]]; then
  echo
  echo "FAIL — ${ERROR_COUNT} error(s) across ${RULE_ERRORS} rule(s) (fail-closed)"
  exit 1
fi
echo
echo "PASS — SwiftUI style gate clean (fail-closed)"
exit 0
