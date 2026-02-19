#!/usr/bin/env node
/**
 * check-setup.mjs
 *
 * Quick validator for integrating Superwall in an Expo project.
 *
 * Run from the project root:
 *   node {baseDir}/scripts/check-setup.mjs
 *
 * Options:
 *   --path <dir>   Project directory (default: .)
 *   --json         Output machine-readable JSON
 */
import fs from "node:fs";
import path from "node:path";

function parseArgs(argv) {
  const out = { projectDir: ".", json: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--json") out.json = true;
    else if (a === "--path" && argv[i + 1]) {
      out.projectDir = argv[i + 1];
      i++;
    } else if (!a.startsWith("-") && out.projectDir === ".") {
      out.projectDir = a;
    }
  }
  return out;
}

function readJson(filePath) {
  const raw = fs.readFileSync(filePath, "utf8");
  return JSON.parse(raw);
}

function parseMajorVersion(version) {
  // Handles "~53.0.0", "^53.0.0", "53.0.0", ">=53", etc.
  const m = String(version).match(/(\d+)(?:\.\d+)?(?:\.\d+)?/);
  return m ? Number(m[1]) : null;
}

function findExpoConfig(projectDir) {
  const candidates = ["app.json", "app.config.json"];
  for (const f of candidates) {
    const p = path.join(projectDir, f);
    if (fs.existsSync(p)) return { type: "json", file: p };
  }
  // app.config.js is common but requires execution; don't eval in a validator.
  const jsCfg = path.join(projectDir, "app.config.js");
  if (fs.existsSync(jsCfg)) return { type: "js", file: jsCfg };
  return null;
}

function extractBuildProperties(expoConfig) {
  const plugins = expoConfig?.expo?.plugins;
  if (!Array.isArray(plugins)) return null;

  for (const entry of plugins) {
    // "expo-build-properties"
    if (typeof entry === "string" && entry === "expo-build-properties") {
      return { hasPlugin: true, config: null };
    }
    // ["expo-build-properties", { ios: {...}, android: {...}}]
    if (Array.isArray(entry) && entry[0] === "expo-build-properties") {
      return { hasPlugin: true, config: entry[1] ?? null };
    }
  }
  return { hasPlugin: false, config: null };
}

function compareVersions(a, b) {
  // a, b are strings like "15.1". Compare numerically by dot parts.
  const pa = String(a).split(".").map((x) => Number(x));
  const pb = String(b).split(".").map((x) => Number(x));
  const n = Math.max(pa.length, pb.length);
  for (let i = 0; i < n; i++) {
    const da = pa[i] ?? 0;
    const db = pb[i] ?? 0;
    if (da > db) return 1;
    if (da < db) return -1;
  }
  return 0;
}

function main() {
  const args = parseArgs(process.argv);
  const projectDir = path.resolve(process.cwd(), args.projectDir);

  const report = {
    projectDir,
    ok: true,
    checks: [],
    hints: [],
  };

  const add = (name, status, details) => {
    if (status !== "pass") report.ok = false;
    report.checks.push({ name, status, details });
  };

  // package.json
  const pkgPath = path.join(projectDir, "package.json");
  if (!fs.existsSync(pkgPath)) {
    add("package.json present", "fail", `Not found at ${pkgPath}`);
  } else {
    add("package.json present", "pass", pkgPath);
    const pkg = readJson(pkgPath);
    const deps = { ...(pkg.dependencies || {}), ...(pkg.devDependencies || {}) };

    const expoVer = deps.expo;
    const expoMajor = expoVer ? parseMajorVersion(expoVer) : null;

    if (expoMajor == null) {
      add("Expo SDK version (expo dep)", "warn", `Could not parse expo version from "${expoVer}"`);
      report.hints.push("Superwall Expo SDK requires Expo SDK 53+.");
    } else if (expoMajor >= 53) {
      add("Expo SDK version (>=53)", "pass", `expo@${expoVer} (major ${expoMajor})`);
    } else {
      add("Expo SDK version (>=53)", "fail", `expo@${expoVer} (major ${expoMajor})`);
    }

    const hasSuperwall = Boolean(deps["expo-superwall"]);
    add("Dependency: expo-superwall", hasSuperwall ? "pass" : "fail", hasSuperwall ? deps["expo-superwall"] : "Not installed");

    const hasBuildProps = Boolean(deps["expo-build-properties"]);
    add("Dependency: expo-build-properties", hasBuildProps ? "pass" : "warn", hasBuildProps ? deps["expo-build-properties"] : "Recommended to set iOS 15.1+ and Android minSdk 21+");
  }

  // app.json / app.config.*
  const cfg = findExpoConfig(projectDir);
  if (!cfg) {
    add("Expo config (app.json/app.config.*)", "warn", "No app.json/app.config.json/app.config.js found");
  } else if (cfg.type === "js") {
    add("Expo config file", "warn", `Found ${path.basename(cfg.file)} (JS). Validator does not execute it.`);
    report.hints.push("Ensure expo-build-properties is configured for iOS deploymentTarget 15.1+ and Android minSdkVersion 21+.");
  } else {
    add("Expo config file", "pass", path.basename(cfg.file));
    try {
      const expoConfig = readJson(cfg.file);

      const scheme = expoConfig?.expo?.scheme;
      if (scheme) {
        add("Deep link scheme set", "pass", `scheme: ${scheme}`);
      } else {
        add("Deep link scheme set", "warn", "No expo.scheme found (optional unless using previews/deep links)");
      }

      const bp = extractBuildProperties(expoConfig);
      if (!bp) {
        add("expo.plugins present", "warn", "No plugins array found under expo.plugins");
      } else if (!bp.hasPlugin) {
        add("Plugin: expo-build-properties configured", "warn", "Not found in expo.plugins");
      } else {
        add("Plugin: expo-build-properties configured", "pass", bp.config ? "Configured with options" : "Present (no inline options)");

        const iosTarget = bp.config?.ios?.deploymentTarget;
        if (iosTarget) {
          const ok = compareVersions(iosTarget, "15.1") >= 0;
          add("iOS deploymentTarget >= 15.1", ok ? "pass" : "fail", `deploymentTarget: ${iosTarget}`);
        } else {
          add("iOS deploymentTarget >= 15.1", "warn", "Not set in expo-build-properties config");
        }

        const minSdk = bp.config?.android?.minSdkVersion;
        if (typeof minSdk === "number") {
          add("Android minSdkVersion >= 21", minSdk >= 21 ? "pass" : "fail", `minSdkVersion: ${minSdk}`);
        } else {
          add("Android minSdkVersion >= 21", "warn", "Not set in expo-build-properties config");
        }
      }
    } catch (e) {
      add("Parse Expo config", "fail", String(e));
    }
  }

  // Dev build reminder
  report.hints.push("Remember: Superwall does not run in Expo Go. Use a Development Build (expo run:* or EAS dev client).");
  report.hints.push("If dashboard changes don't appear during development, fully restart the app (no hot reload refetch).");

  if (args.json) {
    process.stdout.write(JSON.stringify(report, null, 2) + "\n");
  } else {
    const pad = (s, n) => (s + " ".repeat(n)).slice(0, n);
    console.log(`\nSuperwall Expo setup check — ${report.ok ? "OK ✅" : "Needs attention ⚠️"}`);
    console.log(`Project: ${report.projectDir}\n`);
    for (const c of report.checks) {
      const icon = c.status === "pass" ? "✅" : c.status === "warn" ? "⚠️" : "❌";
      console.log(`${icon} ${pad(c.name, 35)} ${c.details}`);
    }
    if (report.hints.length) {
      console.log("\nHints:");
      for (const h of report.hints) console.log(`- ${h}`);
    }
    console.log("");
  }

  process.exit(report.ok ? 0 : 1);
}

main();
