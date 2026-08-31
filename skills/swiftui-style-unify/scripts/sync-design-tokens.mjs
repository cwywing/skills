#!/usr/bin/env node
/**
 * sync-design-tokens.mjs — web CSS SoT → iOS Asset Catalog colorsets.
 *
 * The web file is the only hand-maintained color SoT. This script generates
 * committed .colorset folders (Any + Dark). CI re-runs it and fails on diff.
 *
 * Usage:
 *   node sync-design-tokens.mjs --css <styles.css> --assets <Assets.xcassets>
 *                               [--map <map.json>] [--dry-run]
 *
 * MAP (JSON): { "AppWarning": ["--color-warning", "--color-warning"] }
 *             asset name → [lightVar, darkVar]
 * Default map: assets/color-map.json.tmpl next to this skill, or --map.
 *
 * Supported value syntax in the SoT: #hex (3/4/6/8 digits only; 8-digit keeps
 * alpha), oklch(L C h), rgb()/rgba() numbers, and var(--other). Illegal hex
 * lengths and unresolvable values fail the run (fail-closed).
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const argv = process.argv.slice(2);
const opts = { css: null, assets: null, map: null, dryRun: false };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--css") opts.css = argv[++i];
  else if (a === "--assets") opts.assets = argv[++i];
  else if (a === "--map") opts.map = argv[++i];
  else if (a === "--dry-run") opts.dryRun = true;
  else if (a === "--help" || a === "-h") { usage(); process.exit(0); }
  else { console.error(`unknown option: ${a}`); usage(); process.exit(2); }
}
if (!opts.css || !opts.assets) { usage(); process.exit(2); }

function usage() {
  console.error("usage: node sync-design-tokens.mjs --css <styles.css> --assets <Assets.xcassets> [--map map.json] [--dry-run]");
}

const cssPath = path.resolve(opts.css);
const assetsPath = path.resolve(opts.assets);
if (!fs.existsSync(cssPath)) { console.error(`css not found: ${cssPath}`); process.exit(2); }

const skillDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const defaultMap = path.join(skillDir, "assets", "color-map.json.tmpl");
const mapPath = opts.map ? path.resolve(opts.map) : defaultMap;
if (!fs.existsSync(mapPath)) { console.error(`map not found: ${mapPath} — pass --map`); process.exit(2); }

const MAP = JSON.parse(fs.readFileSync(mapPath, "utf8"));
if (!MAP || typeof MAP !== "object" || Array.isArray(MAP)) {
  console.error("map must be a JSON object of { AssetName: [lightVar, darkVar] }");
  process.exit(2);
}

const css = fs.readFileSync(cssPath, "utf8");

function extractBlock(src, needle) {
  const idx = src.search(needle);
  if (idx < 0) return "";
  const brace = src.indexOf("{", idx);
  if (brace < 0) return "";
  let depth = 0;
  for (let i = brace; i < src.length; i++) {
    if (src[i] === "{") depth++;
    else if (src[i] === "}") {
      depth--;
      if (depth === 0) return src.slice(brace + 1, i);
    }
  }
  return "";
}

function parseVars(block) {
  const vars = {};
  if (!block) return vars;
  for (const m of block.matchAll(/--([A-Za-z0-9-]+)\s*:\s*([^;]+);/g)) {
    vars[`--${m[1]}`] = m[2].trim();
  }
  return vars;
}

const lightVars = parseVars(extractBlock(css, /:root\b/));
const darkVars = {
  ...lightVars,
  ...parseVars(extractBlock(css, /\.dark\s*[,{]/)),
  ...parseVars(extractBlock(css, /\[data-theme=["']dark["']\]/)),
};

function resolveVar(value, vars, depth = 0) {
  if (depth > 8) throw new Error(`var() cycle: ${value}`);
  const m = value.match(/^var\(\s*([^,)]+)\s*(?:,\s*(.+))?\)\s*$/);
  if (!m) return value;
  const name = m[1].trim();
  if (vars[name] != null) return resolveVar(vars[name], vars, depth + 1);
  if (m[2] != null) return resolveVar(m[2].trim(), vars, depth + 1);
  throw new Error(`unresolved ${name}`);
}

function hexToRgb(hex) {
  const h = hex.replace("#", "");
  if (!/^(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(h)) {
    throw new Error(`invalid hex: ${hex}`);
  }
  let rgb = h;
  let a = 1;
  if (h.length === 3) rgb = h.split("").map((c) => c + c).join("");
  else if (h.length === 4) {
    rgb = h.slice(0, 3).split("").map((c) => c + c).join("");
    a = parseInt(h[3] + h[3], 16) / 255;
  } else if (h.length === 8) {
    rgb = h.slice(0, 6);
    a = parseInt(h.slice(6, 8), 16) / 255;
  }
  const n = parseInt(rgb, 16);
  return { r: ((n >> 16) & 255) / 255, g: ((n >> 8) & 255) / 255, b: (n & 255) / 255, a };
}

function oklchToSrgb(L, C, hDeg) {
  const h = (hDeg * Math.PI) / 180;
  const a = C * Math.cos(h);
  const b = C * Math.sin(h);
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.2914855480 * b;
  const l = l_ ** 3, m = m_ ** 3, s = s_ ** 3;
  let r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
  let g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
  let bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;
  const toGamma = (c) => {
    c = Math.min(1, Math.max(0, c));
    return c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055;
  };
  return { r: toGamma(r), g: toGamma(g), b: toGamma(bl), a: 1 };
}

function parseColor(raw, vars) {
  const value = resolveVar(raw.trim(), vars);
  const hex = value.match(/^#([0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/);
  if (hex) return hexToRgb(hex[0]);
  const oklch = value.match(/^oklch\(\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*(?:\/\s*([0-9.]+%?))?\s*\)$/i);
  if (oklch) {
    const rgb = oklchToSrgb(+oklch[1], +oklch[2], +oklch[3]);
    if (oklch[4]) rgb.a = oklch[4].endsWith("%") ? parseFloat(oklch[4]) / 100 : +oklch[4];
    return rgb;
  }
  const rgb = value.match(/^rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*,\s*([0-9.]+))?\s*\)$/i);
  if (rgb) {
    const n = (x) => (x > 1 ? x / 255 : +x);
    return { r: n(+rgb[1]), g: n(+rgb[2]), b: n(+rgb[3]), a: rgb[4] != null ? +rgb[4] : 1 };
  }
  throw new Error(`unsupported color syntax: ${value}`);
}

function fmt(n) { return n.toFixed(3); }

function colorsetJSON(light, dark) {
  const entry = (rgb, darkAppearance) => {
    const color = {
      color: {
        "color-space": "srgb",
        components: {
          red: fmt(rgb.r),
          green: fmt(rgb.g),
          blue: fmt(rgb.b),
          alpha: fmt(rgb.a ?? 1),
        },
      },
      idiom: "universal",
    };
    if (darkAppearance) {
      color.appearances = [{ appearance: "luminosity", value: "dark" }];
    }
    return color;
  };
  return {
    colors: [entry(light, false), entry(dark, true)],
    info: { author: "xcode", version: 1 },
  };
}

const written = [];
for (const [asset, pair] of Object.entries(MAP)) {
  const [lightVar, darkVar] = pair;
  if (typeof lightVar !== "string") {
    console.error(`MAP.${asset} must be [lightVar, darkVar]`);
    process.exit(1);
  }
  const darkName = darkVar || lightVar;
  if (lightVars[lightVar] == null) {
    console.error(`light var ${lightVar} (asset ${asset}) not in :root`);
    process.exit(1);
  }
  let light, dark;
  try {
    light = parseColor(lightVars[lightVar], lightVars);
    dark = parseColor(darkVars[darkName] ?? lightVars[lightVar], darkVars);
  } catch (e) {
    console.error(`${asset}: ${e.message}`);
    process.exit(1);
  }
  const dir = path.join(assetsPath, `${asset}.colorset`);
  const json = JSON.stringify(colorsetJSON(light, dark), null, 2) + "\n";
  written.push(asset);
  if (opts.dryRun) {
    console.log(`dry-run ${asset}  L=${fmt(light.r)},${fmt(light.g)},${fmt(light.b)},a=${fmt(light.a ?? 1)}  D=${fmt(dark.r)},${fmt(dark.g)},${fmt(dark.b)},a=${fmt(dark.a ?? 1)}`);
    continue;
  }
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(path.join(dir, "Contents.json"), json);
}

console.log(`${opts.dryRun ? "dry-run" : "wrote"} ${written.length} colorset(s) → ${assetsPath}`);
