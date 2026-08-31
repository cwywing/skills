#!/usr/bin/env node
/**
 * audit-styles.mjs — style-consistency audit for H5 / mobile-web frontends.
 *
 * Zero dependencies, Node >= 18. Covers the blind spots a stylelint `color-no-hex`
 * gate cannot see: literal rgba()/hsl(), inline style="" colors, Tailwind/Uno
 * arbitrary hex (`bg-[#fff]`), JS-side color literals (including Vue SFC
 * <script>), and uniapp .wxss/.nvue/.uvue. Also reports structural facts
 * (SoT presence — css/scss *and* Vue/uni global style — gate, stack).
 *
 * Usage:
 *   node audit-styles.mjs <app-root> [--sot <path>] [--json] [--strict]
 *
 * Fail-closed contract:
 *   exit 0 — no errors (warnings allowed unless --strict)
 *   exit 1 — violations found, or no SoT detected
 *   exit 2 — operational failure (bad path, unreadable dir, zero files scanned).
 * Never weaken a rule to make this script pass; fix the code or record the debt.
 */

import fs from "node:fs";
import path from "node:path";

const argv = process.argv.slice(2);
const positional = [];
const opts = { sot: null, json: false, strict: false };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--sot") opts.sot = argv[++i];
  else if (a === "--json") opts.json = true;
  else if (a === "--strict") opts.strict = true;
  else if (a === "--help" || a === "-h") { usage(); process.exit(0); }
  else if (a.startsWith("--")) { fail2(`unknown option: ${a}`); }
  else positional.push(a);
}
if (positional.length !== 1) usage(), process.exit(2);
const APP_ROOT = path.resolve(positional[0]);

function usage() {
  console.error("usage: node audit-styles.mjs <app-root> [--sot <path>] [--json] [--strict]");
}
function fail2(msg) { console.error(`✖ ${msg}`); process.exit(2); }

if (!fs.existsSync(APP_ROOT) || !fs.statSync(APP_ROOT).isDirectory()) {
  fail2(`app root not found or not a directory: ${APP_ROOT}`);
}
if (parseInt(process.versions.node.split(".")[0], 10) < 18) {
  fail2(`Node >= 18 required (running ${process.versions.node})`);
}

const SCAN_EXT = /\.(css|scss|wxss|vue|nvue|uvue|js|ts|jsx|tsx)$/;
const SFC_EXT = /\.(vue|nvue|uvue)$/;
const CSS_EXT = /\.(css|scss|wxss)$/;
const SOT_CANDIDATE = /\.(css|scss|wxss|vue|nvue|uvue)$/;

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".next", ".nuxt", ".output", "unpackage", "coverage"]);
const ignoredGlobs = [];
const stylelintignore = path.join(APP_ROOT, ".stylelintignore");
if (fs.existsSync(stylelintignore)) {
  for (const raw of fs.readFileSync(stylelintignore, "utf8").split(/\r?\n/)) {
    const line = raw.trim();
    if (line && !line.startsWith("#")) ignoredGlobs.push(line);
  }
}
function globToRe(g) {
  let s = g.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*\*/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\u0000/g, ".*");
  if (!s.includes("/")) s = `(^|/)${s}`;
  return new RegExp(s.endsWith("/") ? `${s}.*` : `${s}(/|$)`);
}
const ignoredRes = ignoredGlobs.map(globToRe);
const isIgnored = (rel) => ignoredRes.some((re) => re.test(rel)) || SKIP_DIRS.has(path.basename(rel));

const files = [];
(function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
  catch (e) { fail2(`cannot read directory ${dir}: ${e.message}`); }
  for (const e of entries) {
    const rel = path.relative(APP_ROOT, path.join(dir, e.name));
    if (e.isDirectory()) {
      if (!SKIP_DIRS.has(e.name) && !isIgnored(rel)) walk(path.join(dir, e.name));
    } else if (SCAN_EXT.test(e.name)) {
      files.push({ abs: path.join(dir, e.name), rel, ignored: isIgnored(rel) });
    }
  }
})(APP_ROOT);
if (files.length === 0) fail2(`zero scannable files under ${APP_ROOT} — wrong app root?`);

function styleBlocks(text) {
  return [...text.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)];
}
function scriptBlocks(text) {
  return [...text.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)];
}
function cssTextOf(f, text) {
  if (SFC_EXT.test(f.rel)) return styleBlocks(text).map((m) => m[1]).join("\n");
  if (CSS_EXT.test(f.rel)) return text;
  return "";
}
function countCustomProps(text) { return (text.match(/^\s*--[A-Za-z0-9-]+\s*:/gm) || []).length; }
function looksLikeSotHost(text) { return /:root|page\s*\{|uni-page/.test(text); }

let sot = null;
if (opts.sot) {
  const p = path.resolve(APP_ROOT, opts.sot);
  if (!fs.existsSync(p)) fail2(`--sot file not found: ${p}`);
  sot = { rel: path.relative(APP_ROOT, p), abs: p };
} else {
  let best = null;
  for (const f of files) {
    if (!SOT_CANDIDATE.test(f.rel)) continue;
    const text = fs.readFileSync(f.abs, "utf8");
    const css = cssTextOf(f, text) || text;
    if (!looksLikeSotHost(css)) continue;
    const n = countCustomProps(css);
    if (n >= 10 && (!best || n > best.n)) best = { ...f, n };
  }
  if (best) sot = { rel: best.rel, abs: best.abs };
}

function readPkg(dir) {
  const p = path.join(dir, "package.json");
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null;
}
const pkg = readPkg(APP_ROOT);
const deps = { ...(pkg?.dependencies || {}), ...(pkg?.devDependencies || {}) };
let stack = "unknown";
if (deps["@dcloudio/uni-app"] || deps["@dcloudio/vite-plugin-uni"] || fs.existsSync(path.join(APP_ROOT, "manifest.json"))) stack = "uniapp";
else if (deps.vant) stack = "vue3 + vant";
else if (deps["ant-design-mobile"] || deps["antd-mobile"]) stack = "react + antd-mobile";
else if (deps.varlet) stack = "vue3 + varlet";
else if (deps.vue) stack = "vue (no ui lib)";
else if (deps.react) stack = "react (no ui lib)";

const gate = { stylelint: false, colorNoHex: false, hooks: false, ci: false };
for (const parent of [APP_ROOT, path.dirname(APP_ROOT), path.dirname(path.dirname(APP_ROOT))]) {
  if (gate.stylelint && gate.hooks) break;
  if (!gate.stylelint) {
    for (const c of [".stylelintrc.json", ".stylelintrc", ".stylelintrc.js", ".stylelintrc.cjs", "stylelint.config.js"]) {
      const p = path.join(parent, c);
      if (fs.existsSync(p)) {
        gate.stylelint = true;
        const t = fs.readFileSync(p, "utf8");
        if (/color-no-hex/.test(t)) gate.colorNoHex = true;
        break;
      }
    }
  }
  const pp = readPkg(parent);
  if (pp && (pp["lint-staged"] || pp["simple-git-hooks"] || pp.husky)) gate.hooks = true;
  const wf = path.join(parent, ".github", "workflows");
  if (fs.existsSync(wf) && fs.readdirSync(wf).some((f) => /lint|ci|style/i.test(f))) gate.ci = true;
}

// lookbehind includes `[` so Tailwind/Uno arbitrary values (`bg-[#1677ff]`) match
const hexRe = /(?<=[:,\s(='"[])#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/g;
const rgbLiteralRe = /\brgba?\(\s*\d/g;
const hslLiteralRe = /\bhsla?\(\s*\d/g;

function stripCommentsKeepLen(text) {
  let s = text.replace(/\/\*[\s\S]*?\*\//g, (m) => " ".repeat(m.length));
  // `http://` is safe: the char before `//` is `:`, excluded by [^:]
  return s.replace(/([^:]|^)\/\/.*$/gm, (m, p1) => (p1 || "") + " ".repeat(m.length - (p1 ? p1.length : 0)));
}
function lineOf(text, idx) { return text.slice(0, idx).split("\n").length; }
function looksLikeSelector(text, matchEnd) {
  const rest = text.slice(matchEnd, matchEnd + 60);
  return /^\s*[.:#>~+*\w\s[\]="'-]*\{/.test(rest) || /^\s*:{1,2}[\w-]+/.test(rest);
}
function looksLikeDomIdSelector(text, hashIndex) {
  // querySelector('#fade') / getElementById('fade') — id, not a color.
  // Only the argument immediately after those APIs is exempt; a palette
  // next to it still flags.
  const before = text.slice(Math.max(0, hashIndex - 96), hashIndex);
  return /(?:querySelector(?:All)?|getElementById)\s*\(\s*['"]$/.test(before);
}

const findings = [];
function addFinding(sev, kind, file, line, snippet, msg) {
  findings.push({ severity: sev, kind, file, line, snippet: snippet.trim().slice(0, 120), message: msg });
}

function scanCssLike(text, rel, startLine) {
  const clean = stripCommentsKeepLen(text);
  let m;
  hexRe.lastIndex = 0;
  while ((m = hexRe.exec(clean))) {
    if (looksLikeSelector(clean, m.index + m[0].length)) continue;
    addFinding("error", "raw-hex", rel, startLine + lineOf(clean, m.index) - 1, clean.split("\n")[lineOf(clean, m.index) - 1],
      "裸写 hex 颜色 — 先在 theme SoT 登记语义 token，再以 var(--*) 消费");
  }
  for (const [re, kind] of [[rgbLiteralRe, "raw-rgb"], [hslLiteralRe, "raw-hsl"]]) {
    re.lastIndex = 0;
    while ((m = re.exec(clean))) {
      addFinding("error", kind, rel, startLine + lineOf(clean, m.index) - 1, clean.split("\n")[lineOf(clean, m.index) - 1],
        "字面量 rgba()/hsl()（stylelint 盲区）— 改用 rgba(var(--*-rgb), α)，三元组在 SoT 登记");
    }
  }
}
function scanInlineStyles(text, rel) {
  for (const re of [/(?<!:)style="[^"]*"/g, /:style="[^"]*"/g]) {
    let m;
    while ((m = re.exec(text))) {
      const attr = m[0];
      if (/#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/.test(attr) || /rgba?\(\s*\d|hsla?\(\s*\d/.test(attr)) {
        addFinding("error", "inline-style-color", rel, lineOf(text, m.index), attr,
          "模板内联样式携带颜色字面量 — 移入 class，经 var(--*) 消费");
      }
    }
  }
}
function scanJsColorish(text, rel, startLine = 1, asError = false) {
  const clean = stripCommentsKeepLen(text);
  let m;
  hexRe.lastIndex = 0;
  while ((m = hexRe.exec(clean))) {
    const line = clean.split("\n")[lineOf(clean, m.index) - 1] || "";
    if (looksLikeDomIdSelector(clean, m.index)) continue;
    const prev = clean[m.index - 1] || "";
    const quoted = prev === "'" || prev === '"';
    // SFC <script>: any hex literal is the same leak as CSS hex — do not require
    // a same-line keyword (multiline `primary: '#1677ff'` would otherwise PASS).
    // Standalone JS: quoted hex always counts; unquoted needs a color-ish key.
    const keyed = /colou?r|background|\bbg\b|theme|border|fill|stroke|palette|primary|secondary|success|warning|danger|accent/i.test(line);
    if (!asError && !quoted && !keyed) continue;
    addFinding(
      asError ? "error" : "warn",
      "js-color",
      rel,
      startLine + lineOf(clean, m.index) - 1,
      line,
      asError
        ? "SFC/脚本里的颜色字面量 — 先在 SoT 登记，再注入/导出 token（与 CSS 裸 hex 同级）"
        : "JS 侧颜色字面量 — 评估改为从 SoT 导出/注入；--strict 时升级为 error",
    );
  }
}

for (const f of files) {
  if (f.ignored) continue;
  if (sot && path.resolve(f.abs) === path.resolve(sot.abs)) continue;
  const text = fs.readFileSync(f.abs, "utf8");
  if (SFC_EXT.test(f.rel)) {
    scanInlineStyles(text, f.rel);
    for (const sm of styleBlocks(text)) {
      scanCssLike(sm[1], f.rel, lineOf(text, sm.index));
    }
    for (const sc of scriptBlocks(text)) {
      // SFC script color literals are the same leak as CSS hex — error, not warn
      scanJsColorish(sc[1], f.rel, lineOf(text, sc.index), true);
    }
  } else if (CSS_EXT.test(f.rel)) {
    scanCssLike(text, f.rel, 1);
  } else {
    scanJsColorish(text, f.rel, 1, false);
  }
}

if (!sot) {
  addFinding("error", "no-sot", "(project)", 0, "",
    "未检测到设计 token 真相源（含 :root / page 自定义属性的 css、scss、wxss 或 Vue/uni SFC）— 先建立 theme SoT（见 assets/theme.css.tmpl），或用 --sot 指定");
}

const errors = findings.filter((f) => f.severity === "error");
const warns = findings.filter((f) => f.severity === "warn");

if (opts.json) {
  console.log(JSON.stringify({ appRoot: APP_ROOT, stack, sot: sot?.rel || null, gate, summary: { errors: errors.length, warnings: warns.length, filesScanned: files.length }, findings }, null, 2));
} else {
  console.log(`style audit — ${APP_ROOT}`);
  console.log(`  stack: ${stack}`);
  console.log(`  SoT:   ${sot ? sot.rel : "✖ 未检出"}`);
  console.log(`  gate:  stylelint=${gate.stylelint ? `yes${gate.colorNoHex ? " (color-no-hex)" : " (无 color-no-hex!)"}` : "no"}  hooks=${gate.hooks ? "yes" : "no"}  ci=${gate.ci ? "yes" : "no"}`);
  console.log(`  scanned ${files.length} files → ${errors.length} errors, ${warns.length} warnings\n`);
  const byKind = {};
  for (const f of findings) (byKind[f.kind] ||= []).push(f);
  for (const [kind, list] of Object.entries(byKind)) {
    console.log(`[${kind}] ×${list.length}`);
    for (const item of list.slice(0, 50)) console.log(`  ${item.severity === "error" ? "✖" : "⚠"} ${item.file}:${item.line}  ${item.snippet}\n     → ${item.message}`);
    if (list.length > 50) console.log(`  … ${list.length - 50} more`);
  }
}

const failWanted = errors.length > 0 || !sot || (opts.strict && warns.length > 0);
if (!opts.json) {
  console.log(failWanted ? `\nFAIL — see above (fail-closed)` : `\nPASS — no style violations`);
}
process.exit(failWanted ? 1 : 0);
