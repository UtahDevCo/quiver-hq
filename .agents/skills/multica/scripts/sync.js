#!/usr/bin/env bun
/**
 * sync.js
 * Synchronize local workspace skills and agents with your Multica workspace.
 *
 * Usage:
 *   bun ./skills/multica/scripts/sync.js [options]
 *   Or (from root if symlinked/installed):
 *   bun ./.agents/skills/multica/scripts/sync.js [options]
 *
 * Options:
 *   --dry-run          Print actions without making changes on Multica.
 *   --create-agents    Detect runtimes and provision missing agents.
 *   --assign-all       Set all synchronized skills for all workspace agents.
 *   --help, -h          Show this help dialogue.
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";

const args = process.argv.slice(2);
let dryRun = false;
let createAgents = false;
let assignAll = false;

if (args.includes('--help') || args.includes('-h')) {
  printHelp();
  process.exit(0);
}

dryRun = args.includes('--dry-run');
createAgents = args.includes('--create-agents');
assignAll = args.includes('--assign-all');

const WORKSPACE_DIR = process.cwd();
const SCRATCH_DIR = path.join(WORKSPACE_DIR, 'scratch');
if (!fs.existsSync(SCRATCH_DIR)) {
  fs.mkdirSync(SCRATCH_DIR, { recursive: true });
}
const TEMP_CONTENT_FILE = path.join(SCRATCH_DIR, 'temp_sync_content.md');

// Helper to run multica CLI commands and parse output
function runMultica(commandArgs) {
  try {
    const output = execSync(`multica ${commandArgs}`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
    return output.trim();
  } catch (error) {
    console.error(`${RED}Error executing: multica ${commandArgs}${RESET}`);
    console.error(error.stderr || error.message);
    throw error;
  }
}

function printHelp() {
  console.log(`${BOLD}Multica Sync Utility${RESET}`);
  console.log("Synchronizes local workspace skills and agents to Multica.");
  console.log("\nUsage:");
  console.log("  bun ./.agents/skills/multica/scripts/sync.js [options]\n");
  console.log("Options:");
  console.log("  --dry-run          Show what would be changed without applying it");
  console.log("  --create-agents    Automatically create agents for detected runtimes");
  console.log("  --assign-all       Assign all synchronized skills to all agents");
  console.log("  --help, -h          Show this help menu");
}

function parseFrontmatter(fileContent) {
  const match = fileContent.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) {
    return { metadata: {}, body: fileContent };
  }
  const yamlStr = match[1];
  const body = match[2];
  const metadata = {};
  yamlStr.split(/\r?\n/).forEach(line => {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.substring(0, colonIdx).trim();
      let val = line.substring(colonIdx + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.substring(1, val.length - 1);
      }
      metadata[key] = val;
    }
  });
  return { metadata, body };
}

function getFilesRecursive(dir, baseDir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      // Ignore version control, node packages, local artifacts, and config folders
      if (file !== 'node_modules' && file !== '.git' && file !== 'evals' && file !== 'tests' && file !== 'temp' && file !== 'scratch') {
        results = results.concat(getFilesRecursive(fullPath, baseDir));
      }
    } else {
      if (file !== 'SKILL.md' && file !== '.DS_Store' && file !== 'sync.js') {
        const ext = path.extname(file).toLowerCase();
        const binaryExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.pdf', '.zip', '.tar', '.gz', '.mp3', '.mp4'];
        if (!binaryExtensions.includes(ext)) {
          const relativePath = path.relative(baseDir, fullPath);
          results.push({ absolutePath: fullPath, relativePath });
        }
      }
    }
  });
  return results;
}

async function main() {
  console.log(`${CYAN}${BOLD}=== Starting Multica Synchronizer ===${RESET}\n`);

  // 1. Gather all local skills
  const skillsDirs = [
    path.join(WORKSPACE_DIR, 'skills'),
    path.join(WORKSPACE_DIR, '.agents', 'skills'),
    path.join(WORKSPACE_DIR, 'projects', 'k1', '.agents', 'skills'),
    path.join(WORKSPACE_DIR, 'projects', 'wiley', 'skills'),
    path.join(WORKSPACE_DIR, 'projects', 'quiver-photos-v2', '.github', 'skills'),
    '/home/chris/.gemini/config/plugins/firebase/skills',
    '/home/chris/.gemini/config/skills',
    '/home/chris/.gemini/skills',
    '/home/chris/.gemini/config/plugins/chrome-devtools-plugin/skills',
    '/home/chris/.gemini/config/plugins/modern-web-guidance-plugin/skills'
  ];

  const localSkills = new Map();

  for (const dir of skillsDirs) {
    if (!fs.existsSync(dir)) continue;
    const items = fs.readdirSync(dir);
    for (const item of items) {
      const skillPath = path.join(dir, item);
      const stat = fs.statSync(skillPath);
      // Resolve symlink to get real path
      const realSkillPath = fs.realpathSync(skillPath);
      const realStat = fs.statSync(realSkillPath);
      if (realStat.isDirectory()) {
        const skillMdPath = path.join(realSkillPath, 'SKILL.md');
        if (fs.existsSync(skillMdPath)) {
          const content = fs.readFileSync(skillMdPath, 'utf-8');
          const { metadata, body } = parseFrontmatter(content);
          const name = metadata.name || item;
          const description = metadata.description || "";

          // Gather companion files
          const companionFiles = getFilesRecursive(realSkillPath, realSkillPath);

          localSkills.set(name, {
            name,
            description,
            body,
            companionFiles,
            dir: realSkillPath
          });
        }
      }
    }
  }

  console.log(`${GREEN}Found ${localSkills.size} unique local skills:${RESET}`);
  for (const [name, skill] of localSkills) {
    console.log(` - ${BOLD}${name}${RESET} (${skill.companionFiles.length} companion files)`);
  }
  console.log();

  // 2. Fetch existing skills from Multica
  console.log(`${CYAN}Fetching existing skills from Multica workspace...${RESET}`);
  let remoteSkills = [];
  try {
    const rawList = runMultica('skill list --output json');
    remoteSkills = JSON.parse(rawList);
    console.log(`${GREEN}Loaded ${remoteSkills.length} skills from Multica workspace.${RESET}\n`);
  } catch (err) {
    console.error(`${RED}Failed to fetch skills from Multica CLI. Please verify your login status with "multica login".${RESET}`);
    process.exit(1);
  }

  const remoteSkillsMap = new Map(remoteSkills.map(s => [s.name, s]));
  const syncedSkillIds = [];

  // 3. Sync skills
  for (const [name, skill] of localSkills) {
    console.log(`${CYAN}Syncing skill: ${BOLD}${name}${RESET}...`);
    const existing = remoteSkillsMap.get(name);
    let skillId = existing ? existing.id : null;

    if (dryRun) {
      if (existing) {
        console.log(`[DRY-RUN] Would update existing skill: ${name} (ID: ${skillId})`);
      } else {
        console.log(`[DRY-RUN] Would create new skill: ${name}`);
      }
      syncedSkillIds.push(skillId || "dry-run-id");
    } else {
      // Write body to temporary content file to avoid CLI escaping issues
      fs.writeFileSync(TEMP_CONTENT_FILE, skill.body, 'utf-8');

      try {
        if (existing) {
          const resultRaw = runMultica(`skill update ${skillId} --name "${name}" --description "${skill.description.replace(/"/g, '\\"')}" --content-file "${TEMP_CONTENT_FILE}" --output json`);
          const result = JSON.parse(resultRaw);
          console.log(`Updated skill: ${name} (ID: ${skillId})`);
        } else {
          const resultRaw = runMultica(`skill create --name "${name}" --description "${skill.description.replace(/"/g, '\\"')}" --content-file "${TEMP_CONTENT_FILE}" --output json`);
          const result = JSON.parse(resultRaw);
          skillId = result.id;
          console.log(`Created new skill: ${name} (ID: ${skillId})`);
        }
        syncedSkillIds.push(skillId);
      } catch (err) {
        console.error(`${RED}Failed to sync skill ${name}${RESET}`);
        continue;
      } finally {
        if (fs.existsSync(TEMP_CONTENT_FILE)) {
          fs.unlinkSync(TEMP_CONTENT_FILE);
        }
      }
    }

    // Sync files
    if (skillId) {
      let remoteFiles = [];
      if (!dryRun) {
        try {
          const rawFiles = runMultica(`skill files list ${skillId} --output json`);
          remoteFiles = JSON.parse(rawFiles);
        } catch (err) {
          console.error(`${RED}Failed to list files for skill ${name}${RESET}`);
        }
      }

      const remoteFilesMap = new Map(remoteFiles.map(f => [f.path, f]));
      const localFilePaths = new Set(skill.companionFiles.map(f => f.relativePath));

      // Upload local files
      for (const file of skill.companionFiles) {
        if (dryRun) {
          console.log(`[DRY-RUN] Would upsert file: ${file.relativePath} for skill ${name}`);
        } else {
          try {
            runMultica(`skill files upsert ${skillId} --path "${file.relativePath}" --content-file "${file.absolutePath}" --output json`);
            console.log(`  Upserted file: ${file.relativePath}`);
          } catch (err) {
            console.error(`  ${RED}Failed to upsert file: ${file.relativePath}${RESET}`);
          }
        }
      }

      // Delete remote files that are not local
      for (const [remotePath, remoteFile] of remoteFilesMap) {
        if (!localFilePaths.has(remotePath)) {
          if (dryRun) {
            console.log(`[DRY-RUN] Would delete remote file: ${remotePath} (ID: ${remoteFile.id})`);
          } else {
            try {
              runMultica(`skill files delete ${skillId} ${remoteFile.id}`);
              console.log(`  Deleted obsolete remote file: ${remotePath}`);
            } catch (err) {
              console.error(`  ${RED}Failed to delete obsolete remote file: ${remotePath}${RESET}`);
            }
          }
        }
      }
    }
  }

  // 4. Handle Create Agents if requested
  if (createAgents) {
    console.log(`\n${CYAN}Checking runtimes and provisioning agents...${RESET}`);
    let runtimes = [];
    let agents = [];
    try {
      runtimes = JSON.parse(runMultica('runtime list --output json'));
      agents = JSON.parse(runMultica('agent list --output json'));
    } catch (err) {
      console.error(`${RED}Failed to fetch runtimes/agents list.${RESET}`);
    }

    const onlineRuntimes = runtimes.filter(r => r.STATUS === 'online' || r.status === 'online');
    console.log(`Found ${onlineRuntimes.length} online runtimes:`);

    for (const runtime of onlineRuntimes) {
      const provider = runtime.PROVIDER || runtime.provider;
      const id = runtime.ID || runtime.id;
      const name = runtime.NAME || runtime.name;

      const hasAgent = agents.some(a => a.runtime_id === id && !a.archived_at);
      if (hasAgent) {
        console.log(` - Runtime ${name} already has an active agent.`);
      } else {
        const agentName = `${provider.charAt(0).toUpperCase() + provider.slice(1)} Agent`;
        if (dryRun) {
          console.log(`[DRY-RUN] Would create agent: "${agentName}" for runtime ${name} (ID: ${id})`);
        } else {
          try {
            const resultRaw = runMultica(`agent create --name "${agentName}" --runtime-id "${id}" --output json`);
            const result = JSON.parse(resultRaw);
            console.log(`Created agent: "${agentName}" (ID: ${result.id}) for runtime ${name}`);
            agents.push(result); // Add to local array so we can assign skills to it
          } catch (err) {
            console.error(`${RED}Failed to create agent "${agentName}" for runtime ${id}${RESET}`);
          }
        }
      }
    }
  }

  // 5. Handle Assign All if requested
  if (assignAll && syncedSkillIds.length > 0) {
    console.log(`\n${CYAN}Assigning skills to all agents...${RESET}`);
    let agents = [];
    try {
      agents = JSON.parse(runMultica('agent list --output json'));
    } catch (err) {
      console.error(`${RED}Failed to fetch agents for skill assignment.${RESET}`);
    }

    const activeAgents = agents.filter(a => !a.archived_at);
    // Filter out dry-run placeholders
    const validSkillIds = syncedSkillIds.filter(id => id !== "dry-run-id");
    
    if (validSkillIds.length > 0) {
      const skillIdsStr = validSkillIds.join(',');

      for (const agent of activeAgents) {
        if (dryRun) {
          console.log(`[DRY-RUN] Would assign ${validSkillIds.length} skills to agent "${agent.name}" (ID: ${agent.id})`);
        } else {
          try {
            runMultica(`agent skills set ${agent.id} --skill-ids "${skillIdsStr}"`);
            console.log(`Assigned skills to agent "${agent.name}"`);
          } catch (err) {
            console.error(`${RED}Failed to assign skills to agent "${agent.name}"${RESET}`);
          }
        }
      }
    }
  }

  console.log(`\n${GREEN}${BOLD}=== Multica Sync Completed! ===${RESET}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
