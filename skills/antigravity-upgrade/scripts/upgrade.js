#!/usr/bin/env bun
/**
 * upgrade.js
 * Automates the upgrade pipeline for the Google Antigravity Suite packages in flake.nix.
 *
 * Usage:
 *   bun ./skills/antigravity-upgrade/scripts/upgrade.js [options]
 *
 * Options:
 *   --auto               Auto-discover and upgrade all components to their latest GCS versions
 *   --cli <version>      New CLI version (e.g. 1.0.1-6660132856266752)
 *   --manager <version>  New Manager version (e.g. 2.0.6-5413878570549248)
 *   --ide <version>      New IDE version (e.g. 2.0.1-4861014005645312)
 *   --rebuild            Automatically run nixos-rebuild switch after writing changes
 *   --dry-run            Simulate changes without modifying files or rebuilding
 */

import { execSync } from "child_process";
import fs from "fs";
import path from "path";

// Color constants for CLI output
const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const BLUE = "\x1b[34m";
const CYAN = "\x1b[36m";
const MAGENTA = "\x1b[35m";

// Parse CLI arguments
const args = process.argv.slice(2);
let newCliVersion = null;
let newManagerVersion = null;
let newIdeVersion = null;
let autoRebuild = false;
let dryRun = false;
let autoDiscover = false;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--cli":
      newCliVersion = args[++i];
      break;
    case "--manager":
      newManagerVersion = args[++i];
      break;
    case "--ide":
      newIdeVersion = args[++i];
      break;
    case "--rebuild":
      autoRebuild = true;
      break;
    case "--dry-run":
      dryRun = true;
      break;
    case "--auto":
      autoDiscover = true;
      break;
    case "--help":
    case "-h":
      printHelp();
      process.exit(0);
    default:
      console.error(`${RED}Unknown argument: ${args[i]}${RESET}`);
      printHelp();
      process.exit(1);
  }
}

// --- Auto-discovery from GCS ---

/**
 * Lists prefixes (version directories) from a GCS bucket path.
 * Returns a sorted array of version strings, newest last.
 */
async function listGCSVersions(bucket, prefix) {
  const url = `https://storage.googleapis.com/storage/v1/b/${bucket}/o?prefix=${encodeURIComponent(prefix)}&delimiter=/`;
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`GCS list failed for ${url}: ${resp.status}`);
  const data = await resp.json();
  const prefixes = (data.prefixes || []).map((p) => p.replace(prefix, "").replace(/\/$/, ""));
  return prefixes;
}

/**
 * Parses a version string like "1.0.1-6660132856266752" or "2.0.6-5413878570549248"
 * into [major, minor, patch, buildId] for comparison.
 */
function parseVersion(v) {
  const m = v.match(/^(\d+)\.(\d+)\.(\d+)(?:-(\d+))?$/);
  if (!m) return null;
  return [parseInt(m[1]), parseInt(m[2]), parseInt(m[3]), parseInt(m[4] || "0")];
}

function compareVersions(a, b) {
  const pa = parseVersion(a);
  const pb = parseVersion(b);
  if (!pa || !pb) return 0;
  for (let i = 0; i < 4; i++) {
    if (pa[i] !== pb[i]) return pa[i] - pb[i];
  }
  return 0;
}

/**
 * Picks the highest semver+buildId version from a list.
 * Ignores non-semver entries like "test", "tools", "dogfood", "v0.x.x", etc.
 */
function pickLatest(versions) {
  const semver = versions.filter((v) => /^\d+\.\d+\.\d+-\d+$/.test(v));
  if (semver.length === 0) return null;
  return semver.sort(compareVersions).at(-1);
}

/**
 * Verifies that a specific download URL returns HTTP 200.
 */
async function verifyUrl(url) {
  const resp = await fetch(url, { method: "HEAD" });
  return resp.ok;
}

async function autoDiscoverVersions() {
  console.log(`${MAGENTA}${BOLD}🔍 Auto-discovering latest Antigravity versions from GCS...${RESET}\n`);

  // --- CLI ---
  const cliVersions = await listGCSVersions("antigravity-public", "antigravity-cli/");
  const latestCli = pickLatest(cliVersions);
  if (!latestCli) throw new Error("Could not determine latest CLI version from GCS.");
  console.log(`${CYAN}CLI latest:     ${BOLD}${latestCli}${RESET}`);

  // --- Manager ---
  const managerVersions = await listGCSVersions("antigravity-public", "antigravity-hub/");
  const latestManager = pickLatest(managerVersions.filter((v) => !/dogfood/.test(v)));
  if (!latestManager) throw new Error("Could not determine latest Manager version from GCS.");
  console.log(`${CYAN}Manager latest: ${BOLD}${latestManager}${RESET}`);

  // IDE: Try matching the Manager's build ID against the IDE CDN, then fall back to known versions.
  // The IDE CDN is not publicly listable, so we probe known version/build combinations.
  let latestIde = null;
  const ideProbeVersions = ["2.0.6", "2.0.5", "2.0.3", "2.0.2", "2.0.1"];
  const ideProbeBuildIds = managerVersions
    .filter((v) => /^\d+\.\d+\.\d+-\d+$/.test(v))
    .map((v) => v.split("-")[1])
    .filter(Boolean);

  // Also add build IDs from CLI versions
  const cliBuildIds = cliVersions
    .filter((v) => /^\d+\.\d+\.\d+-\d+$/.test(v))
    .map((v) => v.split("-")[1])
    .filter(Boolean);

  const allBuildIds = [...new Set([...ideProbeBuildIds, ...cliBuildIds])];

  console.log(`${CYAN}Probing IDE CDN for latest version...${RESET}`);
  outer: for (const minor of ideProbeVersions) {
    for (const buildId of allBuildIds) {
      const candidate = `${minor}-${buildId}`;
      const url = `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/${candidate}/linux-x64/Antigravity%20IDE.tar.gz`;
      if (await verifyUrl(url)) {
        latestIde = candidate;
        break outer;
      }
    }
  }

  if (latestIde) {
    console.log(`${CYAN}IDE latest:     ${BOLD}${latestIde}${RESET}`);
  } else {
    console.log(`${YELLOW}IDE: Could not find a newer version via CDN probing. Skipping IDE upgrade.${RESET}`);
  }

  console.log();
  return { cli: latestCli, manager: latestManager, ide: latestIde };
}

// --- Main ---

async function main() {
  // Handle auto-discovery
  if (autoDiscover) {
    const discovered = await autoDiscoverVersions();
    if (!newCliVersion) newCliVersion = discovered.cli;
    if (!newManagerVersion) newManagerVersion = discovered.manager;
    if (!newIdeVersion && discovered.ide) newIdeVersion = discovered.ide;
  }

  if (!newCliVersion && !newManagerVersion && !newIdeVersion) {
    console.log(
      `${YELLOW}No component versions specified. Use --auto to discover latest, or provide --cli, --manager, --ide.${RESET}\n`
    );
    printHelp();
    process.exit(0);
  }

  // Find flake.nix in current directory or upwards
  let repoRoot = process.cwd();
  while (repoRoot !== "/" && !fs.existsSync(path.join(repoRoot, "flake.nix"))) {
    repoRoot = path.dirname(repoRoot);
  }
  const flakePath = path.join(repoRoot, "flake.nix");

  if (!fs.existsSync(flakePath)) {
    console.error(`${RED}Error: Could not find flake.nix in ${process.cwd()} or parent directories.${RESET}`);
    process.exit(1);
  }

  console.log(`${CYAN}Using flake.nix at: ${BOLD}${flakePath}${RESET}\n`);

  // Load current flake content
  let flakeContent = fs.readFileSync(flakePath, "utf8");

  // Template builders for download URLs
  const getCliUrl = (version) =>
    `https://storage.googleapis.com/antigravity-public/antigravity-cli/${version}/linux-x64/cli_linux_x64.tar.gz`;
  const getManagerUrl = (version) =>
    `https://storage.googleapis.com/antigravity-public/antigravity-hub/${version}/linux-x64/Antigravity.tar.gz`;
  const getIdeUrl = (version) =>
    `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/${version}/linux-x64/Antigravity%20IDE.tar.gz`;

  // Map of components to their blocks and update details
  const updates = {};

  if (newCliVersion) {
    updates["antigravity-cli"] = {
      newVersion: newCliVersion,
      url: getCliUrl(newCliVersion),
      blockRegex: /(antigravity-cli\s*=\s*mkAntigravityCli\s*\{)([\s\S]*?)(\};)/,
    };
  }

  if (newManagerVersion) {
    updates["antigravity-manager"] = {
      newVersion: newManagerVersion,
      url: getManagerUrl(newManagerVersion),
      blockRegex:
        /(antigravity-manager\s*=\s*mkAntigravityApp\s*\{)([\s\S]*?)(comment\s*=\s*"Google Antigravity manager";\s*\};)/,
    };
  }

  if (newIdeVersion) {
    updates["antigravity-ide"] = {
      newVersion: newIdeVersion,
      url: getIdeUrl(newIdeVersion),
      blockRegex:
        /(antigravity-ide\s*=\s*mkAntigravityApp\s*\{)([\s\S]*?)(categories\s*=\s*\[\s*"Development"\s*"IDE"\s*\];\s*\};)/,
    };
  }

  // Check if any component is already at the requested version
  for (const [name, update] of Object.entries(updates)) {
    const match = flakeContent.match(update.blockRegex);
    if (match) {
      const currentVersionMatch = match[2].match(/version\s*=\s*"([^"]*)";/);
      const currentVersion = currentVersionMatch ? currentVersionMatch[1] : null;
      if (currentVersion === update.newVersion) {
        console.log(`${GREEN}✓ ${BOLD}${name}${RESET}${GREEN} is already at version ${BOLD}${update.newVersion}${RESET}. Skipping.`);
        delete updates[name];
      }
    }
  }

  if (Object.keys(updates).length === 0) {
    console.log(`\n${GREEN}${BOLD}All components are already up to date!${RESET}`);
    process.exit(0);
  }

  // Prefetch URLs and calculate hashes
  for (const [name, update] of Object.entries(updates)) {
    console.log(
      `${CYAN}Prefetching and verifying ${BOLD}${name}${RESET}${CYAN} (Version: ${update.newVersion})...${RESET}`
    );
    console.log(`URL: ${update.url}`);

    try {
      const prefetchOutput = execSync(`nix store prefetch-file --json "${update.url}"`, { encoding: "utf8" });
      const prefetchInfo = JSON.parse(prefetchOutput);
      update.newHash = prefetchInfo.hash;
      console.log(`${GREEN}✓ Successfully retrieved SRI Hash: ${BOLD}${update.newHash}${RESET}\n`);
    } catch (err) {
      console.error(`${RED}Error prefetching URL: ${err.message}${RESET}`);
      process.exit(1);
    }
  }

  // Perform replacements
  let updatedFlakeContent = flakeContent;
  let changeCount = 0;

  for (const [name, update] of Object.entries(updates)) {
    const match = updatedFlakeContent.match(update.blockRegex);
    if (!match) {
      console.error(`${RED}Error: Could not find code block for ${BOLD}${name}${RESET}${RED} in flake.nix.${RESET}`);
      console.error(`Please check the flake.nix formatting.`);
      process.exit(1);
    }

    const prefix = match[1];
    const blockContent = match[2];
    const suffix = match[3];

    // Read old details
    const oldVersionMatch = blockContent.match(/version\s*=\s*"([^"]*)";/);
    const oldUrlMatch = blockContent.match(/url\s*=\s*"([^"]*)";/);
    const oldHashMatch = blockContent.match(/hash\s*=\s*"([^"]*)";/);

    const oldVersion = oldVersionMatch ? oldVersionMatch[1] : "unknown";
    const oldUrl = oldUrlMatch ? oldUrlMatch[1] : "unknown";
    const oldHash = oldHashMatch ? oldHashMatch[1] : "unknown";

    // Create new block contents
    let newBlockContent = blockContent;
    newBlockContent = newBlockContent.replace(/version\s*=\s*"([^"]*)";/, `version = "${update.newVersion}";`);
    newBlockContent = newBlockContent.replace(/url\s*=\s*"([^"]*)";/, `url = "${update.url}";`);
    newBlockContent = newBlockContent.replace(/hash\s*=\s*"([^"]*)";/, `hash = "${update.newHash}";`);

    // Assemble full replacement
    const replacement = prefix + newBlockContent + suffix;
    updatedFlakeContent = updatedFlakeContent.replace(match[0], replacement);

    console.log(`${BOLD}${CYAN}--- ${name} Change Summary ---${RESET}`);
    console.log(`${BLUE}Version:${RESET} ${RED}${oldVersion}${RESET} -> ${GREEN}${update.newVersion}${RESET}`);
    console.log(`${BLUE}URL:    ${RESET} ${RED}${oldUrl}${RESET} -> ${GREEN}${update.url}${RESET}`);
    console.log(`${BLUE}Hash:   ${RESET} ${RED}${oldHash}${RESET} -> ${GREEN}${update.newHash}${RESET}`);
    console.log();
    changeCount++;
  }

  if (dryRun) {
    console.log(
      `${YELLOW}Dry run active. No files written. Setup would update ${changeCount} components.${RESET}`
    );
  } else {
    // Write to flake.nix
    fs.writeFileSync(flakePath, updatedFlakeContent, "utf8");
    console.log(`${GREEN}✓ Successfully wrote updates to ${BOLD}flake.nix${RESET}\n`);

    if (autoRebuild) {
      const flakeName = execSync("hostname", { encoding: "utf8" }).trim();
      console.log(
        `${CYAN}Rebuilding NixOS system configuration... (sudo nixos-rebuild switch --flake .#${flakeName})${RESET}`
      );
      try {
        execSync(`sudo nixos-rebuild switch --flake .#${flakeName}`, { stdio: "inherit", cwd: repoRoot });
        console.log(`\n${GREEN}✓ NixOS system configuration rebuilt successfully!${RESET}`);
      } catch (err) {
        console.error(`\n${RED}Error: Rebuild failed. Please check build logs above.${RESET}`);
        process.exit(1);
      }
    } else {
      const flakeName = execSync("hostname", { encoding: "utf8" }).trim();
      console.log(`${YELLOW}To apply these changes, execute the system switch manually:${RESET}`);
      console.log(`${BOLD}sudo nixos-rebuild switch --flake .#${flakeName}${RESET}`);
    }
  }
}

function printHelp() {
  console.log(`${BOLD}Google Antigravity Upgrade Utility${RESET}`);
  console.log("Usage:");
  console.log("  bun ./skills/antigravity-upgrade/scripts/upgrade.js [options]\n");
  console.log("Options:");
  console.log("  --auto               Auto-discover and upgrade all components to the latest available GCS versions");
  console.log("  --cli <version>      Upgrade the Antigravity CLI package (e.g. 1.0.1-6660132856266752)");
  console.log("  --manager <version>  Upgrade the Antigravity Manager package (e.g. 2.0.6-5413878570549248)");
  console.log("  --ide <version>      Upgrade the Antigravity IDE package (e.g. 2.0.1-4861014005645312)");
  console.log("  --rebuild            Automatically run sudo nixos-rebuild switch --flake .#$(hostname)");
  console.log("  --dry-run            Calculate hashes and show changes without writing to flake.nix or rebuilding");
  console.log("  --help, -h           Show this help dialogue");
  console.log();
  console.log("Examples:");
  console.log("  # Fully automatic: discover latest versions, update flake.nix, and rebuild:");
  console.log("  bun upgrade.js --auto --rebuild");
  console.log();
  console.log("  # Dry-run auto-discovery to preview what would change:");
  console.log("  bun upgrade.js --auto --dry-run");
  console.log();
  console.log("  # Manually upgrade specific components:");
  console.log("  bun upgrade.js --cli 1.0.1-6660132856266752 --manager 2.0.6-5413878570549248 --rebuild");
}

main().catch((err) => {
  console.error(`${RED}Fatal: ${err.message}${RESET}`);
  process.exit(1);
});
