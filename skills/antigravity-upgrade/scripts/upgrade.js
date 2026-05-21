#!/usr/bin/env bun
/**
 * upgrade.js
 * Automates the upgrade pipeline for the Google Antigravity Suite packages in flake.nix.
 * 
 * Usage:
 *   bun ./skills/antigravity-upgrade/scripts/upgrade.js [options]
 * 
 * Options:
 *   --cli <version>      New CLI version
 *   --manager <version>  New Manager version
 *   --ide <version>      New IDE version
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

// Parse CLI arguments
const args = process.argv.slice(2);
let newCliVersion = null;
let newManagerVersion = null;
let newIdeVersion = null;
let autoRebuild = false;
let dryRun = false;

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

if (!newCliVersion && !newManagerVersion && !newIdeVersion) {
  console.log(`${YELLOW}No component versions specified. Please provide at least one of --cli, --manager, or --ide.${RESET}\n`);
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
const getCliUrl = (version) => `https://storage.googleapis.com/antigravity-public/antigravity-cli/${version}/linux-x64/cli_linux_x64.tar.gz`;
const getManagerUrl = (version) => `https://storage.googleapis.com/antigravity-public/antigravity-hub/${version}/linux-x64/Antigravity.tar.gz`;
const getIdeUrl = (version) => `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/${version}/linux-x64/Antigravity%20IDE.tar.gz`;

// Map of components to their blocks and update details
const updates = {};

if (newCliVersion) {
  updates["antigravity-cli"] = {
    newVersion: newCliVersion,
    url: getCliUrl(newCliVersion),
    blockRegex: /(antigravity-cli\s*=\s*mkAntigravityCli\s*\{)([\s\S]*?)(\};)/
  };
}

if (newManagerVersion) {
  updates["antigravity-manager"] = {
    newVersion: newManagerVersion,
    url: getManagerUrl(newManagerVersion),
    blockRegex: /(antigravity-manager\s*=\s*mkAntigravityApp\s*\{)([\s\S]*?)(comment\s*=\s*"Google Antigravity manager";\s*\};)/
  };
}

if (newIdeVersion) {
  updates["antigravity-ide"] = {
    newVersion: newIdeVersion,
    url: getIdeUrl(newIdeVersion),
    blockRegex: /(antigravity-ide\s*=\s*mkAntigravityApp\s*\{)([\s\S]*?)(categories\s*=\s*\[\s*"Development"\s*"IDE"\s*\];\s*\};)/
  };
}

// Prefetch URLs and calculate hashes
for (const [name, update] of Object.entries(updates)) {
  console.log(`${CYAN}Prefetching and verifying ${BOLD}${name}${RESET}${CYAN} (Version: ${update.newVersion})...${RESET}`);
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
  console.log(`${YELLOW}Dry run active. No files written. Setup would update ${changeCount} components.${RESET}`);
} else {
  // Write to flake.nix
  fs.writeFileSync(flakePath, updatedFlakeContent, "utf8");
  console.log(`${GREEN}✓ successfully wrote updates to ${BOLD}flake.nix${RESET}\n`);

  if (autoRebuild) {
    console.log(`${CYAN}Rebuilding NixOS system configuration... (running sudo nixos-rebuild switch)${RESET}`);
    try {
      execSync(`sudo nixos-rebuild switch --flake .#quiver-wsl`, { stdio: "inherit", cwd: repoRoot });
      console.log(`\n${GREEN}✓ NixOS System configuration rebuilt successfully!${RESET}`);
    } catch (err) {
      console.error(`\n${RED}Error: Rebuild failed. Please check build logs above.${RESET}`);
      process.exit(1);
    }
  } else {
    console.log(`${YELLOW}To apply these changes, execute the system switch manually:${RESET}`);
    console.log(`${BOLD}sudo nixos-rebuild switch --flake .#quiver-wsl${RESET}`);
  }
}

function printHelp() {
  console.log(`${BOLD}Google Antigravity Upgrade Utility${RESET}`);
  console.log("Usage:");
  console.log("  bun ./skills/antigravity-upgrade/scripts/upgrade.js [options]\n");
  console.log("Options:");
  console.log("  --cli <version>      Upgrade the Antigravity CLI package (e.g. 1.0.0-5288553236791296)");
  console.log("  --manager <version>  Upgrade the Antigravity Manager package (e.g. 2.0.1-6566078776737792)");
  console.log("  --ide <version>      Upgrade the Antigravity IDE package (e.g. 2.0.1-4861014005645312)");
  console.log("  --rebuild            Automatically run sudo nixos-rebuild switch --flake .#quiver-wsl");
  console.log("  --dry-run            Calculate hashes and show changes without writing to flake.nix or rebuilding");
  console.log("  --help, -h           Show this help dialogue");
}
