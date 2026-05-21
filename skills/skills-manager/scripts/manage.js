#!/usr/bin/env bun
/**
 * manage.js
 * Programmatic interface and CLI wrapper for the skills.sh registry inside this workspace.
 * 
 * Usage:
 *   bun ./skills/skills-manager/scripts/manage.js [options]
 * 
 * Options:
 *   --list              List all installed project skills
 *   --find <query>      Search the skills.sh registry for a skill
 *   --add <package>     Download and install a skill package (e.g. shadcn/ui)
 *   --update            Update all installed skills to the latest versions
 *   --remove <name>     Remove a specific installed skill
 */

import { execSync } from "child_process";

// Color constants for CLI output
const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";

const args = process.argv.slice(2);
let command = null;
let param = null;

if (args.length === 0) {
  printHelp();
  process.exit(0);
}

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case "--list":
      command = "list";
      break;
    case "--find":
      command = "find";
      param = args[++i];
      break;
    case "--add":
      command = "add";
      param = args[++i];
      break;
    case "--update":
      command = "update";
      break;
    case "--remove":
      command = "remove";
      param = args[++i];
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

switch (command) {
  case "list":
    console.log(`${CYAN}Listing all installed project skills...${RESET}\n`);
    runSkillsCommand("list");
    break;

  case "find":
    if (!param) {
      console.error(`${RED}Error: Please specify a search query (e.g. --find shadcn)${RESET}`);
      process.exit(1);
    }
    console.log(`${CYAN}Searching the skills.sh registry for "${BOLD}${param}${RESET}${CYAN}"...${RESET}\n`);
    runSkillsCommand(`find "${param}"`);
    break;

  case "add":
    if (!param) {
      console.error(`${RED}Error: Please specify a skill package name to add (e.g. --add shadcn/ui)${RESET}`);
      process.exit(1);
    }
    console.log(`${CYAN}Downloading and installing skill "${BOLD}${param}${RESET}${CYAN}"...${RESET}\n`);
    runSkillsCommand(`add ${param} --all`);
    break;

  case "update":
    console.log(`${CYAN}Updating all installed skills to their latest versions...${RESET}\n`);
    runSkillsCommand("update -y");
    break;

  case "remove":
    if (!param) {
      console.error(`${RED}Error: Please specify the name of the skill to remove (e.g. --remove shadcn)${RESET}`);
      process.exit(1);
    }
    console.log(`${CYAN}Removing skill "${BOLD}${param}${RESET}${CYAN}"...${RESET}\n`);
    runSkillsCommand(`remove ${param} --all -y`);
    break;
}

function runSkillsCommand(subCommand) {
  try {
    execSync(`bunx skills ${subCommand}`, { stdio: "inherit", cwd: process.cwd() });
  } catch (err) {
    console.error(`\n${RED}Execution failed. Please check build or CLI logs above.${RESET}`);
    process.exit(1);
  }
}

function printHelp() {
  console.log(`${BOLD}Skills Manager CLI Utility${RESET}`);
  console.log("Usage:");
  console.log("  bun ./skills/skills-manager/scripts/manage.js [options]\n");
  console.log("Options:");
  console.log("  --list              List all installed project skills");
  console.log("  --find <query>      Search the skills.sh registry for a skill");
  console.log("  --add <package>     Download and install a skill package (e.g. shadcn/ui)");
  console.log("  --update            Update all installed skills to the latest versions");
  console.log("  --remove <name>     Remove a specific installed skill");
  console.log("  --help, -h           Show this help dialogue");
}
