#!/usr/bin/env node
/**
 * audit-styles.mjs — style-consistency audit for H5 / mobile-web frontends.
 *
 * Zero dependencies, Node >= 18. Covers the blind spots a stylelint `color-no-hex`
 * gate cannot see: literal rgba()/hsl(), inline style="" colors in templates, and
 * JS-side color literals; also reports structural facts (SoT presence, gate presence,
 * stack detection) so a run doubles as a Phase-0/1 report.
 *
 * Usage:
 *   node audit-styles.mjs <app-root> [--sot <path>] [--json] [--strict]
 *
 * Fail-closed contract (mirrors the gate-configs doctrine):
 *   exit 0 — no errors (warnings allowed unless --strict)
 *   exit 1 — violations found, or no SoT detected
 *   exit 2 — operational failure (bad path, unreadable dir, zero files scanned).
 * Never weaken a rule to make this script pass; fix the code or record the debt.
 */

import fs from "node:fs";
import path from "node:path";

// ---------- args ----------
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

// ---------- ignore handling (stylelintignore + built-ins) ----------
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
  // minimal matcher: supports **, *, and trailing-dir semantics; enough for ignore files
  let s = g.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*\*/g, "\u0000").replace(/\*/g, "[^/]*").replace(/\u0000/g, ".*");
  if (!s.includes("/")) s = `(^|/)${s}`;          // bare name matches at any depth
  return new RegExp(s.endsWith("/") ? `${s}.*` : `${s}(/|$)`);
}
const ignoredRes = ignoredGlobs.map(globToRe);
const isIgnored = (rel) => ignoredRes.some((re) => re.test(rel)) || SKIP_DIRS.has(path.basename(rel));

// ---------- collect files ----------
// Ignored files (SKIP_DIRS / .stylelintignore) stay in the list with ignored=true:
// the SoT is normally stylelint-whitelisted, so detection must still see it —
// only violation scanning skips ignored files.
const files = [];
(function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
  catch (e) { fail2(`cannot read directory ${dir}: ${e.message}`); }
  for (const e of entries) {
    const rel = path.relative(APP_ROOT, path.join(dir, e.name));
    if (e.isDirectory()) {
      if (!SKIP_DIRS.has(e.name) && !isIgnored(rel)) walk(path.join(dir, e.name));
    } else if (/\.(css|scss|vue|js|ts|jsx|tsx)$/.test(e.name)) {
      files.push({ abs: path.join(dir, e.name), rel, ignored: isIgnored(rel) });
    }
  }
})(APP_ROOT);
if (files.length === 0) fail2(`zero scannable files under ${APP_ROOT} — wrong app root?`);

// ---------- SoT detection ----------
function countCustomProps(text) { return (text.match(/^\s*--[A-Za-z0-9-]+\s*:/gm) || []).length; }
let sot = null;
if (opts.sot) {
  const p = path.resolve(APP_ROOT, opts.sot);
  if (!fs.existsSync(p)) fail2(`--sot file not found: ${p}`);
  sot = { rel: path.relative(APP_ROOT, p), abs: p };
} else {
  let best = null;
  for (const f of files) {
    if (!/\.(css|scss)$/.test(f.rel)) continue;
    const text = fs.readFileSync(f.abs, "utf8");
    if (/:root|page\s*\{|uni-page/.test(text)) {
      const n = countCustomProps(text);
      if (n >= 10 && (!best || n > best.n)) best = { ...f, n };
    }
  }
  if (best) sot = { rel: best.rel, abs: best.abs };
}

// ---------- stack & gate detection ----------
function readPkg(dir) {
  const p = path.join(dir, "package.json");
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null;
}
const pkg = readPkg(APP_ROOT);
const deps = { ...(pkg?.dependencies || {}), ...(pkg?.devDependencies || {}) };
let stack = "unknown";
if (deps["@dcloudio/uni-app"] || deps["@dcloudio/vite-plugin-uni"]) stack = "uniapp";
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

// ---------- scanning ----------
// valid color lengths: 3,4,6,8 hex digits; preceded by a value-ish char so bare
// words in comments/identifiers don't match
const hexRe = /(?<=[:,\s(='"])#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/g;
const rgbLiteralRe = /\brgba?\(\s*\d/g;
const hslLiteralRe = /\bhsla?\(\s*\d/g;

function stripCommentsKeepLen(text) {
  return text.replace(/\/\*[\s\S]*?\*\//g, (m) => " ".repeat(m.length));
}
function lineOf(text, idx) { return text.slice(0, idx).split("\n").length; }
function looksLikeSelector(text, matchEnd) {
  // "#fade {" / "#fade:hover" are id selectors, not colors: only selector-ish
  // chars may sit between the hex and a following "{" or pseudo-class
  const rest = text.slice(matchEnd, matchEnd + 60);
  return /^\s*[.:#>~+*\w\s[\]="'-]*\{/.test(rest) || /^\s*:{1,2}[\w-]+/.test(rest);
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
  // template attribute style="...#fff..." and :style bindings containing color literals
  for (const re of [/(?<!:)style="[^"]*"/g, /:style="[^"]*"/g]) {
    let m;
    while ((m = re.exec(text))) {
      const attr = m[0];
      if (/#[0-9a-fA-F]{3,8}\b/.test(attr) || /rgba?\(\s*\d|hsla?\(\s*\d/.test(attr)) {
        addFinding("error", "inline-style-color", rel, lineOf(text, m.index), attr,
          "模板内联样式携带颜色字面量 — 移入 class，经 var(--*) 消费");
      }
    }
  }
}
function scanJsColorish(text, rel) {
  const clean = stripCommentsKeepLen(text);
  let m;
  hexRe.lastIndex = 0;
  while ((m = hexRe.exec(clean))) {
    const line = clean.split("\n")[lineOf(clean, m.index) - 1] || "";
    if (/colou?r|background|bg|theme|border/i.test(line)) {
      addFinding("warn", "js-color", rel, lineOf(clean, m.index), line,
        "JS 侧颜色字面量 — 评估改为从 SoT 导出/注入，暂仅报告");
    }
  }
}

for (const f of files) {
  if (f.ignored) continue; // whitelisted (stylelintignore) — exempt from violation scanning
  if (sot && path.resolve(f.abs) === path.resolve(sot.abs)) continue; // SoT is whitelisted
  const text = fs.readFileSync(f.abs, "utf8");
  if (f.rel.endsWith(".vue")) {
    scanInlineStyles(text, f.rel);
    for (const sm of text.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)) {
      scanCssLike(sm[1], f.rel, lineOf(text, sm.index));
    }
  } else if (/\.(css|scss)$/.test(f.rel)) {
    scanCssLike(text, f.rel, 1);
  } else {
    scanJsColorish(text, f.rel);
  }
}

// ---------- structural findings ----------
if (!sot) {
  addFinding("error", "no-sot", "(project)", 0, "",
    "未检测到设计 token 真相源（含 :root 自定义属性的 css/scss）— 先建立 theme SoT（见 assets/theme.css.tmpl），或用 --sot 指定");
}

// ---------- output ----------
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
    for (const f of list.slice(0, 50)) console.log(`  ${f.severity === "error" ? "✖" : "⚠"} ${f.file}:${f.line}  ${f.snippet}\n     → ${f.message}`);
    if (list.length > 50) console.log(`  … ${list.length - 50} more`);
  }
}

const failWanted = errors.length > 0 || !sot || (opts.strict && warns.length > 0);
if (!opts.json) {
  console.log(failWanted ? `\nFAIL — see above (fail-closed)` : `\nPASS — no style violations`);
}
process.exit(failWanted ? 1 : 0);
