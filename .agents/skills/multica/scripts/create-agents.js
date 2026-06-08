#!/usr/bin/env bun
/**
 * create-agents.js
 * Automatically provision role-specific agents, managers, and squads in Multica.
 *
 * Usage:
 *   bun ./.agents/skills/multica/scripts/create-agents.js
 */

import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';

const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";

const WORKSPACE_DIR = process.cwd();

// Helper to run multica CLI commands and parse JSON output
function runMulticaJson(argsArray) {
  try {
    const output = execFileSync('multica', [...argsArray, '--output', 'json'], { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] });
    return JSON.parse(output.trim());
  } catch (error) {
    console.error(`${RED}Error executing: multica ${argsArray.join(' ')}${RESET}`);
    console.error(error.stderr || error.message);
    throw error;
  }
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

function readInstructions(filePath) {
  if (!fs.existsSync(filePath)) {
    console.warn(`${YELLOW}Warning: Instruction file not found: ${filePath}${RESET}`);
    return "";
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  const { body } = parseFrontmatter(content);
  return body.trim();
}

const agentDefs = [
  // ==========================================
  // A. Foundation Project Squad (Claude)
  // ==========================================
  {
    name: "Foundation Manager Agent",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructions: "You are the Foundation Manager Agent and Squad Leader for the Foundation projects. Your job is to oversee the team, review incoming requests, break them down into tickets, assign them to the specialized agents in your squad, monitor execution, verify the final output, and record leader evaluations.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Foundation Triage Agent",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructionFiles: [
      "projects/foundation-web/.github/agents/linear-triage.agent.md",
      "projects/foundation-web/.github/agents/sentry-triage.agent.md",
      "projects/foundation-web/.github/agents/pr-comment-triage.agent.md"
    ],
    skills: ["linear-triage", "sentry-triage", "pr-comment-triage", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Foundation Execution Agent",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructionFiles: [
      "projects/foundation-web/.github/agents/linear-ticket-executor.agent.md",
      "projects/foundation-web/.github/agents/sentry-issue-closer.agent.md",
      "projects/foundation-web/.github/agents/pr-comment-resolver.agent.md"
    ],
    skills: ["linear-ticket-executor", "sentry-issue-closer", "pr-comment-resolver", "github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "Foundation Code Review Agent",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructionFiles: [
      "projects/foundation-web/.github/agents/pr-deep-dive-reviewer.agent.md"
    ],
    skills: ["pr-deep-dive-reviewer", "pr-comment-triage", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Foundation PR/Linear Manager",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructionFiles: [
      "projects/foundation-web/.github/agents/linear-pr-closer.agent.md"
    ],
    skills: ["linear-pr-closer", "github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // B. Wiley Project Squad (Antigravity)
  // ==========================================
  {
    name: "Wiley Manager Agent",
    provider: "antigravity",
    instructions: "You are the Wiley Manager Agent and Squad Leader for the Wiley project. Your job is to oversee the team, coordinate tasks, deconstruct features into cards in Fizzy, assign cards to specialized agents, monitor execution, and record leader evaluations using the fizzy CLI.",
    skills: ["fizzy", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Wiley Release & Deploy Agent",
    provider: "antigravity",
    instructionFiles: [
      "projects/wiley/.github/agents/release-manager.agent.md",
      "projects/wiley/.github/agents/deploy-monitor.agent.md"
    ],
    skills: ["deployment-monitor", "fizzy", "github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "Wiley Email Triage Agent",
    provider: "antigravity",
    instructionFiles: ["projects/wiley/.github/agents/email-triage.agent.md"],
    skills: ["fizzy", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Wiley Production Debug Agent",
    provider: "antigravity",
    instructionFiles: ["projects/wiley/.github/agents/production-debug.agent.md"],
    skills: ["fizzy", "github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "Wiley Triage Agent",
    provider: "antigravity",
    instructionFiles: ["projects/wiley/.github/agents/wiley-triage.agent.md"],
    skills: ["fizzy", "github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // C. K1 Project Squad (Codex)
  // ==========================================
  {
    name: "K1 Manager Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the K1 Manager Agent and Squad Leader for the K1 project. Your responsibility is to oversee the team, review incoming requests, break them down into tickets, assign them to the K1 specialized agents, monitor execution, and verify the final output.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "K1 Triage Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the K1 Triage Agent. Your job is to intake bug reports, troubleshoot local Firebase environment configurations, and prioritize tickets.",
    skills: ["firebase-local-env-setup", "firebase-basics", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "K1 Codex Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are a software developer building out the K1 project (acting as the K1 Execution Agent). You write clean code and use Drizzle schema, Firebase Data Connect, Genkit, and Firestore skills. (Includes Chrome DevTools MCP).",
    skills: [
      "deployment-monitor",
      "developing-genkit-dart",
      "developing-genkit-js",
      "firebase-ai-logic",
      "firebase-app-hosting-basics",
      "firebase-auth-basics",
      "firebase-basics",
      "firebase-data-connect",
      "firebase-firestore-enterprise-native-mode",
      "firebase-firestore-standard",
      "firebase-hosting-basics",
      "firebase-local-env-setup",
      "shadcn",
      "github-helper",
      "multica"
    ],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "K1 Code Review Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the K1 Code Review Agent. Your job is to perform deep dive reviews on pull requests for the K1 project.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // D. Therapy Animal Hub Squad (Codex)
  // ==========================================
  {
    name: "Therapy Animal Hub Manager Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the Therapy Animal Hub Manager Agent and Squad Leader for the Therapy Animal Hub project. Your responsibility is to oversee the team, coordinate Next.js task allocation, monitor builds, and verify successful deployments.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Therapy Animal Hub Triage Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the Therapy Animal Hub Triage Agent. Your job is to evaluate incoming bug reports and diagnose app routing or deployment-related issues.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Therapy Animal Hub Release Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructionFiles: ["projects/therapyanimalhub.com/.github/agents/release.agent.md"],
    skills: ["deploy-therapyanimalhub", "github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "Therapy Animal Hub Code Review Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the Therapy Animal Hub Code Review Agent. Your job is to perform reviews on Next.js App Router PRs for Therapy Animal Hub.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // E. Trikin Project Squad (Codex exclusively)
  // ==========================================
  {
    name: "Trikin Manager Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the Trikin Manager Agent and Squad Leader for the Trikin project. Your responsibility is to coordinate tasks, deconstruct features into tickets, assign them to the specialized Trikin agents, and monitor execution.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Trikin Triage Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructionFiles: ["projects/trikin/.github/agents/production-debugger.agent.md"],
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Trikin Execution Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the Trikin Execution Agent. Your job is to implement code changes under web/src/, edit Drizzle schemas, run local tests, and manage Cloudflare D1 database operations. (Includes Chrome DevTools MCP).",
    skills: ["github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "Trikin Code Review Agent",
    provider: "codex",
    model: "gpt-5.5-medium",
    instructions: "You are the Trikin Code Review Agent. Your job is to review pull requests and verify conformance to the React component guidelines in AGENTS.md.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // F. Quiver Photos Project Squad (Gemini / Opencode)
  // ==========================================
  {
    name: "Quiver Photos Manager Agent",
    provider: "gemini",
    instructions: "You are the Quiver Photos Manager Agent and Squad Leader for Quiver Photos. Your responsibility is to oversee the team, coordinate bug report resolutions, track execution progress, and record leader evaluations.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Quiver Photos Triage Agent",
    provider: "gemini",
    instructionFiles: [
      "projects/quiver-photos-v2/.github/agents/bug-reports.agent.md",
      "projects/quiver-photos-v2/.github/agents/telemetry.agent.md"
    ],
    skills: ["bug-report-inbox", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Quiver Photos Executor Agent",
    provider: "opencode",
    instructionFiles: [
      "projects/quiver-photos-v2/.github/agents/devops.agent.md",
      "projects/quiver-photos-v2/.github/agents/download-all.agent.md",
      "projects/quiver-photos-v2/.github/agents/go-coverage.agent.md",
      "projects/quiver-photos-v2/.github/agents/testing.agent.md"
    ],
    skills: ["github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },

  // ==========================================
  // G. Tools Project Squad (Antigravity)
  // ==========================================
  {
    name: "Tools Manager Agent",
    provider: "antigravity",
    instructions: "You are the Tools Manager Agent and Squad Leader for the internal developer tools. Your job is to oversee the team, review developer tools feature requests, deconstruct them into tasks, assign them to specialized tools agents, monitor execution, and verify the final output.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Tools Execution Agent",
    provider: "antigravity",
    instructions: "You are a developer for internal tools. You implement code changes under tools/apps/, write clean code, and debug Next.js apps, Chrome extensions, and CLI scripts. (Includes Chrome DevTools MCP).",
    skills: ["chrome-extensions", "investing-screener", "opentui", "github-helper", "multica"],
    mcpConfig: {
      mcpServers: {
        "chrome-devtools": {
          command: "npx",
          args: ["-y", "@modelcontextprotocol/server-chrome-devtools"]
        }
      }
    }
  },
  {
    name: "Tools Code Review Agent",
    provider: "antigravity",
    instructions: "You are the Tools Code Review Agent. Your job is to review pull requests for the internal developer tools under projects/tools/.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Tools PR/Linear Manager",
    provider: "antigravity",
    instructions: "You are the Tools PR/Linear Manager. Your job is to handle branching, committing, pushing, and closing tickets/PRs for the tools project.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // H. Multica Management Project Squad (Antigravity)
  // ==========================================
  {
    name: "Multica Management Agent",
    provider: "antigravity",
    instructions: "You are the Multica Management Agent. Your job is to manage the Multica configuration, sync workspace skills, provision agents/squads, and audit runtime configurations using the multica CLI and sync scripts.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },

  // ==========================================
  // I. Monorepo-wide Agents
  // ==========================================
  {
    name: "Monorepo Documenter Agent",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructions: "You are a Monorepo Documenter. Your job is to keep all sub-project READMEs, Mermaid diagrams, API references, and system documentation up to date, consistent, and highly readable. You verify that diagrams accurately represent codebase dependencies and structure.",
    skills: ["github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Dependency Upgrader Agent",
    provider: "antigravity",
    instructions: "You are a Dependency and Package Upgrader. Your job is to monitor and execute updates for npm packages, go modules, and Nix system configurations/flakes. You run verification testing after upgrades to ensure no breaking changes are introduced.",
    skills: ["antigravity-upgrade", "skills-manager", "github-helper", "multica"],
    mcpConfig: null
  },
  {
    name: "Security Auditor Agent",
    provider: "claude",
    model: "claude-sonnet-4.6-medium",
    instructions: "You are a Security Auditor Agent. Your job is to audit codebase changes, database migrations, configuration files, and database rules (such as Firestore security rules) to identify potential vulnerabilities, leaks of secret keys, or access control issues. You provide detailed audit reports.",
    skills: ["firebase-security-rules-auditor", "github-helper", "multica"],
    mcpConfig: null
  }
];

const squadDefs = [
  {
    name: "Foundation Squad",
    leader: "Foundation Manager Agent",
    description: "Squad coordinating Foundation projects (foundation-web and foundation-integrations)",
    members: [
      "Foundation Triage Agent",
      "Foundation Execution Agent",
      "Foundation Code Review Agent",
      "Foundation PR/Linear Manager"
    ]
  },
  {
    name: "Wiley Squad",
    leader: "Wiley Manager Agent",
    description: "Squad coordinating Wiley project with Fizzy boards",
    members: [
      "Wiley Release & Deploy Agent",
      "Wiley Email Triage Agent",
      "Wiley Production Debug Agent",
      "Wiley Triage Agent"
    ]
  },
  {
    name: "K1 Squad",
    leader: "K1 Manager Agent",
    description: "Squad building K1 project (Firebase/Genkit)",
    members: [
      "K1 Triage Agent",
      "K1 Codex Agent",
      "K1 Code Review Agent"
    ]
  },
  {
    name: "Therapy Animal Hub Squad",
    leader: "Therapy Animal Hub Manager Agent",
    description: "Squad deploying and releasing Therapy Animal Hub Next.js app",
    members: [
      "Therapy Animal Hub Triage Agent",
      "Therapy Animal Hub Release Agent",
      "Therapy Animal Hub Code Review Agent"
    ]
  },
  {
    name: "Trikin Squad",
    leader: "Trikin Manager Agent",
    description: "Squad developing Trikin web and workers",
    members: [
      "Trikin Triage Agent",
      "Trikin Execution Agent",
      "Trikin Code Review Agent"
    ]
  },
  {
    name: "Quiver Photos Squad",
    leader: "Quiver Photos Manager Agent",
    description: "Squad managing Quiver Photos bug intake and executions",
    members: [
      "Quiver Photos Triage Agent",
      "Quiver Photos Executor Agent"
    ]
  },
  {
    name: "Tools Squad",
    leader: "Tools Manager Agent",
    description: "Squad managing internal developer tools",
    members: [
      "Tools Execution Agent",
      "Tools Code Review Agent",
      "Tools PR/Linear Manager"
    ]
  },
  {
    name: "Multica Management Squad",
    leader: "Multica Management Agent",
    description: "Squad managing the Multica platform and workspace configuration",
    members: []
  }
];

async function main() {
  console.log(`${CYAN}${BOLD}=== Provisioning Custom Multica Agents & Squads ===${RESET}\n`);

  // 1. Fetch Runtimes from Multica
  console.log(`${CYAN}Fetching online runtimes...${RESET}`);
  const runtimes = runMulticaJson(['runtime', 'list']);
  const onlineRuntimes = runtimes.filter(r => r.STATUS === 'online' || r.status === 'online');

  const providerMap = new Map();
  const activeRuntimeIds = new Set();
  for (const runtime of onlineRuntimes) {
    const provider = runtime.PROVIDER || runtime.provider;
    const id = runtime.ID || runtime.id;
    providerMap.set(provider.toLowerCase(), id);
    activeRuntimeIds.add(id);
  }

  console.log(`${GREEN}Online runtimes mapped successfully:${RESET}`);
  for (const [provider, id] of providerMap) {
    console.log(` - ${provider}: ${id}`);
  }
  console.log();

  // 2. Fetch Existing Skills to Map IDs
  console.log(`${CYAN}Fetching workspace skills...${RESET}`);
  const skills = runMulticaJson(['skill', 'list']);
  const skillNameToId = new Map(skills.map(s => [s.name, s.id]));

  // 3. Fetch Existing Agents
  console.log(`${CYAN}Fetching existing agents...${RESET}`);
  const existingAgents = runMulticaJson(['agent', 'list']);
  const existingAgentsMap = new Map(existingAgents.filter(a => !a.archived_at).map(a => [a.name, a]));

  const agentNameToId = new Map();
  const configuredAgentNames = new Set(agentDefs.map(d => d.name));

  // 4. Create or Update Agents
  for (const def of agentDefs) {
    console.log(`${CYAN}Processing Agent: ${BOLD}${def.name}${RESET}...`);

    const runtimeId = providerMap.get(def.provider.toLowerCase());
    if (!runtimeId) {
      console.error(`  ${RED}Error: No online runtime found for provider "${def.provider}". Skipping agent.${RESET}`);
      continue;
    }

    // Load instructions
    let instructions = "";
    if (def.instructionFiles && def.instructionFiles.length > 0) {
      instructions = def.instructionFiles.map(file => {
        const filePath = path.join(WORKSPACE_DIR, file);
        const relativeName = path.basename(file);
        const body = readInstructions(filePath);
        return `### Instructions from ${relativeName}\n\n${body}`;
      }).join('\n\n---\n\n');
    } else {
      instructions = def.instructions || "";
    }

    // Resolve skills IDs
    const skillIds = [];
    for (const name of def.skills) {
      const id = skillNameToId.get(name);
      if (id) {
        skillIds.push(id);
      } else {
        console.warn(`  ${YELLOW}Warning: Skill "${name}" not found in Multica workspace.${RESET}`);
      }
    }

    const mcpConfigStr = def.mcpConfig ? JSON.stringify(def.mcpConfig) : "null";

    // Check if agent already exists
    const existing = existingAgentsMap.get(def.name);
    let agentId = existing ? existing.id : null;

    try {
      if (existing) {
        // Update agent
        const args = [
          'agent', 'update', agentId,
          '--runtime-id', runtimeId,
          '--instructions', instructions,
          '--mcp-config', mcpConfigStr
        ];
        if (def.model) {
          args.push('--model', def.model);
        } else {
          args.push('--model', ''); // Reset to default
        }

        runMulticaJson(args);
        console.log(`  Updated agent: "${def.name}" (ID: ${agentId})`);
      } else {
        // Create agent
        const args = [
          'agent', 'create',
          '--name', def.name,
          '--runtime-id', runtimeId,
          '--instructions', instructions,
          '--mcp-config', mcpConfigStr
        ];
        if (def.model) {
          args.push('--model', def.model);
        }

        const result = runMulticaJson(args);
        agentId = result.id;
        console.log(`  Created agent: "${def.name}" (ID: ${agentId})`);
      }

      agentNameToId.set(def.name, agentId);

      // Assign skills
      if (skillIds.length > 0) {
        execFileSync('multica', ['agent', 'skills', 'set', agentId, '--skill-ids', skillIds.join(',')], { stdio: 'ignore' });
        console.log(`  Assigned ${skillIds.length} skills to "${def.name}"`);
      } else {
        execFileSync('multica', ['agent', 'skills', 'set', agentId, '--skill-ids', ''], { stdio: 'ignore' });
        console.log(`  Cleared skills for "${def.name}"`);
      }

    } catch (err) {
      console.error(`  ${RED}Failed to provision agent "${def.name}":${RESET}`, err.message);
    }
  }

  // 5. Clean Up Obsolete Local-Machine Agents (Archive them)
  console.log(`\n${CYAN}Checking for obsolete agents belonging to our runtimes...${RESET}`);
  for (const agent of existingAgents) {
    if (!agent.archived_at && activeRuntimeIds.has(agent.runtime_id)) {
      if (!configuredAgentNames.has(agent.name)) {
        try {
          runMulticaJson(['agent', 'archive', agent.id]);
          console.log(`${YELLOW}Archived obsolete local runtime agent: "${agent.name}" (ID: ${agent.id})${RESET}`);
        } catch (err) {
          console.error(`  ${RED}Failed to archive obsolete agent "${agent.name}":${RESET}`, err.message);
        }
      }
    }
  }

  // 6. Squad Provisioning
  console.log(`\n${CYAN}Starting Squad Provisioning...${RESET}`);
  let existingSquads = [];
  try {
    existingSquads = runMulticaJson(['squad', 'list']);
  } catch (err) {
    console.error(`${RED}Failed to list existing squads.${RESET}`);
  }
  const existingSquadsMap = new Map(existingSquads.map(s => [s.name, s]));

  for (const squadDef of squadDefs) {
    console.log(`${CYAN}Processing Squad: ${BOLD}${squadDef.name}${RESET}...`);

    const leaderId = agentNameToId.get(squadDef.leader);
    if (!leaderId) {
      console.error(`  ${RED}Error: Leader agent "${squadDef.leader}" not found or failed to create. Skipping squad.${RESET}`);
      continue;
    }

    let squadId = null;
    const existing = existingSquadsMap.get(squadDef.name);

    try {
      if (existing) {
        squadId = existing.id;
        // Update squad
        runMulticaJson(['squad', 'update', squadId, '--leader', leaderId, '--description', squadDef.description]);
        console.log(`  Updated squad: "${squadDef.name}" (ID: ${squadId})`);
      } else {
        // Create squad
        const result = runMulticaJson(['squad', 'create', '--name', squadDef.name, '--leader', leaderId, '--description', squadDef.description]);
        squadId = result.id;
        console.log(`  Created squad: "${squadDef.name}" (ID: ${squadId})`);
      }

      // Sync members
      const remoteMembers = runMulticaJson(['squad', 'member', 'list', squadId]);
      const remoteMemberIds = new Set(remoteMembers.map(m => m.member_id || m.id));

      for (const memberName of squadDef.members) {
        const agentId = agentNameToId.get(memberName);
        if (!agentId) {
          console.warn(`  ${YELLOW}Warning: Member agent "${memberName}" not found. Skipping.${RESET}`);
          continue;
        }

        if (!remoteMemberIds.has(agentId)) {
          runMulticaJson(['squad', 'member', 'add', squadId, '--member-id', agentId, '--type', 'agent', '--role', 'member']);
          console.log(`  Added member "${memberName}" to squad`);
        } else {
          console.log(`  Member "${memberName}" already in squad`);
        }
      }

      // Remove obsolete members
      const configuredMemberIds = new Set(squadDef.members.map(m => agentNameToId.get(m)).filter(Boolean));
      for (const remoteMember of remoteMembers) {
        const mId = remoteMember.member_id || remoteMember.id;
        if (mId === leaderId || remoteMember.role === 'leader') {
          continue; // Skip the leader agent
        }
        if (!configuredMemberIds.has(mId)) {
          try {
            runMulticaJson(['squad', 'member', 'remove', squadId, '--member-id', mId]);
            console.log(`  Removed obsolete member "${remoteMember.name || mId}" from squad`);
          } catch (err) {
            console.error(`  ${RED}Failed to remove member ${mId} from squad:${RESET}`, err.message);
          }
        }
      }

    } catch (err) {
      console.error(`  ${RED}Failed to provision squad "${squadDef.name}":${RESET}`, err.message);
    }
  }

  console.log(`\n${GREEN}${BOLD}=== Multica Agent & Squad Provisioning Completed! ===${RESET}`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
