#!/usr/bin/env bash
# Fixture tests for scripts/audit-swift-styles.sh
# Run: bash tests/run.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/scripts/audit-swift-styles.sh"
chmod +x "$SCRIPT"

FAILED=0
ok() { echo "  ok  $1"; }
fail() { echo "  FAIL $1 — $2"; FAILED=$((FAILED + 1)); }

tmpdir() { mktemp -d "${TMPDIR:-/tmp}/swift-audit.XXXXXX"; }

echo "swiftui audit-swift-styles.sh"

if grep -v '^[[:space:]]*#' "$SCRIPT" | grep -q 'xargs -r'; then
  fail "no GNU xargs -r" "script still contains xargs -r"
else
  ok "no GNU xargs -r"
fi

{
  d="$(tmpdir)"
  mkdir -p "$d/App/Features/Order" "$d/App/Theme/Tokens"
  cat > "$d/App/Theme/Tokens/ColorTokens.swift" << 'EOF'
enum ColorTokens { static let warning = Color("AppWarning") }
EOF
  cat > "$d/App/Features/Order/OrderView.swift" << 'EOF'
import SwiftUI
struct OrderView: View {
    var body: some View {
        VStack(spacing: 12) {
            Text("hi")
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(Color(red: 0.95, green: 0.3, blue: 0.2))
            RoundedRectangle(cornerRadius: 12).padding(14)
        }
    }
}
EOF
  set +e
  out="$("$SCRIPT" "$d" 2>&1)"
  st=$?
  set -e
  if [[ "$st" -ne 1 ]]; then fail "violations exit 1" "status=$st"; else ok "violations exit 1"; fi
  echo "$out" | grep -q 'Color(' && echo "$out" | grep -q 'font(.system(size:' && echo "$out" | grep -q 'padding(literal)' \
    && ok "aggregates Color + font size + padding" \
    || fail "aggregates all rules" "$(echo "$out" | tail -20)"
  echo "$out" | grep -q 'failed-rules:' && ok "prints failed-rules summary" || fail "summary" "no failed-rules"
  rm -rf "$d"
}

{
  d="$(tmpdir)"
  mkdir -p "$d/App/Features" "$d/App/Theme/Tokens"
  echo 'enum ColorTokens { static let warning = Color("AppWarning") }' > "$d/App/Theme/Tokens/ColorTokens.swift"
  cat > "$d/App/Features/FP.swift" << 'EOF'
import SwiftUI
struct FP: View {
    var body: some View {
        Text("a").font(.system(.body))
        Text("b").foregroundStyle(Color.primary)
    }
}
EOF
  set +e
  out="$("$SCRIPT" "$d" 2>&1)"
  st=$?
  set -e
  if [[ "$st" -eq 0 ]]; then ok ".font(.system(.body)) allowed"; else fail ".font(.system(.body)) allowed" "$out"; fi
  rm -rf "$d"
}

{
  d="$(tmpdir)"
  mkdir -p "$d/App/Features" "$d/App/Theme/Tokens"
  echo 'enum ColorTokens { static let warning = Color("AppWarning") }' > "$d/App/Theme/Tokens/ColorTokens.swift"
  echo 'struct TextStyle {}' > "$d/App/Theme/Tokens/TextStyle.swift"
  cat > "$d/App/Features/CleanView.swift" << 'EOF'
import SwiftUI
struct CleanView: View {
    var body: some View {
        Text("ok")
            .textStyle(DesignTokens.Typography.labelMedium)
            .foregroundStyle(DesignTokens.Colors.warning)
            .padding(DesignTokens.Spacing.md)
    }
}
EOF
  set +e
  out="$("$SCRIPT" "$d" --report 2>&1)"
  st=$?
  set -e
  if [[ "$st" -eq 0 ]]; then ok "generic .textStyle clean PASS"; else fail "generic .textStyle clean PASS" "$out"; fi
  echo "$out" | grep -q 'TextStyle.swift:' && echo "$out" | grep -vq 'EvairTextStyle' \
    && ok "report looks for TextStyle.swift" \
    || fail "report TextStyle" "$out"
  rm -rf "$d"
}

{
  d="$(tmpdir)"
  mkdir -p "$d/App"
  echo 'enum X {}' > "$d/App/Foo.swift"
  set +e
  out="$("$SCRIPT" "$d" 2>&1)"
  st=$?
  set -e
  if echo "$out" | grep -q 'no Features directory found'; then
    fail "missing Features is not hard-fail" "$out"
  else
    ok "missing Features does not hard-fail"
  fi
  rm -rf "$d"
}

{
  d="$(tmpdir)"
  mkdir -p "$d/App/Features" "$d/App/Theme/Tokens"
  echo 'enum ColorTokens { static let warning = Color("AppWarning") }' > "$d/App/Theme/Tokens/ColorTokens.swift"
  echo 'struct V: View { var body: some View { Toggle("x", isOn: .constant(true)) } }' > "$d/App/Features/T.swift"
  set +e
  out="$("$SCRIPT" "$d" 2>&1)"
  st=$?
  set -e
  if [[ "$st" -eq 0 ]] && echo "$out" | grep -q 'Toggle'; then
    ok "Toggle is warn without --components (exit 0)"
  else
    fail "Toggle warn-only" "status=$st $out"
  fi
  set +e
  out2="$("$SCRIPT" "$d" --components 2>&1)"
  st2=$?
  set -e
  if [[ "$st2" -eq 1 ]]; then ok "Toggle is error with --components"; else fail "--components Toggle" "status=$st2 $out2"; fi
  rm -rf "$d"
}

echo
echo "sync-design-tokens.mjs"
SYNC="$ROOT/scripts/sync-design-tokens.mjs"
H5_THEME="$ROOT/../h5-style-unify/assets/theme.css.tmpl"
MAP="$ROOT/assets/color-map.json.tmpl"
assets="$(tmpdir)"
set +e
sout="$(node "$SYNC" --css "$H5_THEME" --assets "$assets" --map "$MAP" --dry-run 2>&1)"
sst=$?
set -e
if [[ "$sst" -eq 0 ]] && echo "$sout" | grep -q 'dry-run'; then
  ok "sync dry-run against H5 theme template"
else
  fail "sync dry-run" "status=$sst $sout"
fi
rm -rf "$assets"

sync_probe() {
  local css_body="$1" expect="$2" name="$3" extra="${4:-}"
  local td mapf cssf
  td="$(tmpdir)"
  mapf="$td/map.json"
  cssf="$td/t.css"
  echo '{"Accent":["--accent","--accent"]}' > "$mapf"
  printf '%s\n' "$css_body" > "$cssf"
  set +e
  out="$(node "$SYNC" --css "$cssf" --assets "$td/out" --map "$mapf" --dry-run 2>&1)"
  st=$?
  set -e
  if [[ "$expect" == "fail" ]]; then
    if [[ "$st" -ne 0 ]]; then ok "$name"; else fail "$name" "expected fail, got: $out"; fi
  else
    if [[ "$st" -eq 0 ]] && echo "$out" | grep -q "$extra"; then ok "$name"; else fail "$name" "status=$st $out"; fi
  fi
  rm -rf "$td"
}

sync_probe ':root { --accent: #ff9500cc; }' pass "8-digit hex keeps alpha" 'a=0.800'
sync_probe ':root { --accent: #12345; }' fail "illegal 5-digit hex fails closed"
sync_probe $':root { --accent: #ff0000; }\n.dark-mode { --accent: #00ff00; }\n.dark { --accent: #0000ff; }' pass "dark class not confused with .dark-mode" 'D=0.000,0.000,1.000'

if [[ "$FAILED" -gt 0 ]]; then
  echo "$FAILED failed"
  exit 1
fi
echo "all passed"
