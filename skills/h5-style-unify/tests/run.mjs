#!/usr/bin/env node
/**
 * Fixture tests for scripts/audit-styles.mjs.
 * Run: node tests/run.mjs
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const script = path.join(root, "scripts", "audit-styles.mjs");
const themeTmpl = fs.readFileSync(path.join(root, "assets", "theme.css.tmpl"), "utf8");

let failed = 0;
function tmp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "h5-audit-"));
}
function run(dir, extra = []) {
  return spawnSync(process.execPath, [script, dir, "--json", ...extra], { encoding: "utf8" });
}
function assert(name, cond, detail) {
  if (cond) console.log(`  ok  ${name}`);
  else { console.error(`  FAIL ${name}${detail ? " — " + detail : ""}`); failed++; }
}

function write(dir, rel, body) {
  const p = path.join(dir, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, body);
}

console.log("h5 audit-styles.mjs");

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme/theme.css", themeTmpl);
  write(d, "src/styles/base.css", ".x{color:var(--color-text);background:rgba(var(--color-overlay-rgb),0.5)}");
  const r = run(d);
  const j = JSON.parse(r.stdout);
  assert("clean exits 0", r.status === 0, `status=${r.status} stderr=${r.stderr}`);
  assert("clean detects SoT", j.sot === "src/theme/theme.css", j.sot);
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme/theme.css", themeTmpl);
  write(d, "src/views/Order.vue", `<template><div style="color:#ff0000">x</div></template>
<style>
.badge { background: #fff7e6; }
.overlay { background: rgba(15, 23, 42, 0.5); }
#fade { opacity: 1; }
</style>`);
  const r = run(d);
  const j = JSON.parse(r.stdout);
  const kinds = new Set(j.findings.map((f) => f.kind));
  assert("vue leaks exit 1", r.status === 1);
  assert("flags raw-hex", kinds.has("raw-hex"));
  assert("flags raw-rgb", kinds.has("raw-rgb"));
  assert("flags inline-style", kinds.has("inline-style-color"));
  assert("id selector #fade not flagged as extra hex", j.findings.filter((f) => f.kind === "raw-hex").length === 1);
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme.css", themeTmpl);
  write(d, "src/a.css", ".btn { @apply bg-[#1677ff] text-[#fff]; }\n.ok { color: var(--color-primary); }\n");
  const r = run(d);
  const j = JSON.parse(r.stdout);
  assert("tailwind arbitrary hex is error", r.status === 1 && j.findings.some((f) => f.kind === "raw-hex"));
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme.css", themeTmpl);
  write(d, "src/Foo.vue", `<template><div>ok</div></template>
<script>
const palette = {
  primary: '#1677ff',
  secondary: '#576b95',
  danger: '#ff3b30',
}
</script>
<style>.ok { color: var(--color-primary); }</style>`);
  const r = run(d);
  const j = JSON.parse(r.stdout);
  const js = j.findings.filter((f) => f.kind === "js-color");
  assert("SFC multiline object hex is error (no same-line keyword)", r.status === 1 && js.length === 3 && js.every((f) => f.severity === "error"), `status=${r.status} n=${js.length} ${JSON.stringify(js)}`);
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme.css", themeTmpl);
  write(d, "src/Foo.vue", `<template><div>ok</div></template>
<script>
document.querySelector('#fade')
document.querySelectorAll('#cafe')
document.getElementById('#babe')
const palette = { primary: '#1677ff' }
</script>
<style>.ok { color: var(--color-primary); }</style>`);
  const r = run(d);
  const j = JSON.parse(r.stdout);
  const js = j.findings.filter((f) => f.kind === "js-color");
  const snips = js.map((f) => f.snippet).join("\n");
  assert("querySelector('#fade') is not a color leak", !/querySelector/.test(snips) && !/getElementById/.test(snips), snips);
  assert("palette hex still errors next to DOM id selectors", r.status === 1 && js.length === 1 && /primary/.test(snips), `n=${js.length} ${snips}`);
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"@dcloudio/uni-app":"^3"}}');
  const vars = Array.from({ length: 12 }, (_, i) => `  --c${i}: #${(i + 1).toString().repeat(6).slice(0, 6)};`).join("\n");
  write(d, "App.vue", `<style>\npage {\n${vars}\n}\n</style>\n<template><view>ok</view></template>\n`);
  const r = run(d);
  const j = JSON.parse(r.stdout);
  assert("uniapp App.vue SoT detected", j.stack === "uniapp" && j.sot === "App.vue", JSON.stringify({ stack: j.stack, sot: j.sot, status: r.status, findings: j.findings }));
  assert("uniapp App.vue SoT not scanned as leak", r.status === 0, `status=${r.status} ${JSON.stringify(j.findings)}`);
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme.css", themeTmpl);
  write(d, "pages/index/index.wxss", ".x { color: #ff0000; }\n");
  const r = run(d);
  const j = JSON.parse(r.stdout);
  assert("wxss hex is error", r.status === 1 && j.findings.some((f) => f.file.includes(".wxss") && f.kind === "raw-hex"));
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme.css", themeTmpl);
  write(d, "src/share.js", "export const cardBg = '#ffffff'\n");
  const r = run(d);
  const j = JSON.parse(r.stdout);
  assert("standalone JS color is warn, exit 0", r.status === 0 && j.findings.some((f) => f.kind === "js-color" && f.severity === "warn"));
  const r2 = run(d, ["--strict"]);
  assert("--strict promotes JS warn to fail", r2.status === 1);
  fs.rmSync(d, { recursive: true });
}

{
  const d = tmp();
  write(d, "package.json", '{"dependencies":{"vue":"^3"}}');
  write(d, "src/theme.css", themeTmpl);
  write(d, "src/palette.js", "export const palette = {\n  primary: '#1677ff',\n  secondary: '#576b95',\n}\n");
  const r = run(d);
  const j = JSON.parse(r.stdout);
  const js = j.findings.filter((f) => f.kind === "js-color");
  assert("standalone JS quoted hex without color-key is still warn", r.status === 0 && js.length === 2, `status=${r.status} n=${js.length}`);
  fs.rmSync(d, { recursive: true });
}

if (failed) {
  console.error(`\n${failed} failed`);
  process.exit(1);
}
console.log("all passed");
