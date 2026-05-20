#!/usr/bin/env bun
/**
 * Linear Issue Triage Helper Script
 * Path: ~/dev/quiver-hq/skills/linear-triage/scripts/triage.js
 * 
 * Fetches Linear issues based on filters (assigned, team, cycle, url) 
 * and writes them as beautiful local Markdown files for easy offline triage.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function runCmd(cmd) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'ignore'] }).trim();
  } catch (err) {
    return null;
  }
}

function getLoggedInUser() {
  const whoami = runCmd('bunx linear auth whoami');
  if (!whoami) return null;
  
  const match = whoami.match(/Display name:\s*([^\n\r]+)/i);
  return match ? match[1].trim() : null;
}

// Parse command line arguments
const args = process.argv.slice(2);
let url = null;
let team = null;
let cycle = null;
let assignee = null;
let filterTodo = false;
let allStates = false;
let targetDirOverride = null;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--url' && args[i + 1]) {
    url = args[++i];
  } else if (args[i] === '--team' && args[i + 1]) {
    team = args[++i];
  } else if (args[i] === '--cycle' && args[i + 1]) {
    cycle = args[++i];
  } else if (args[i] === '--assignee' && args[i + 1]) {
    assignee = args[++i];
  } else if (args[i] === '--todo') {
    filterTodo = true;
  } else if (args[i] === '--all-states') {
    allStates = true;
  } else if (args[i] === '--dir' && args[i + 1]) {
    targetDirOverride = args[++i];
  }
}

// If a Linear URL is provided, parse it to extract team, cycle, or issue ID
if (url) {
  console.log(`Parsing URL: ${url}`);
  
  // Case 1: Specific Issue URL (e.g., https://linear.app/buildwithfoundation/issue/FOU-3522/lombardo-...)
  const issueMatch = url.match(/\/issue\/([A-Za-z0-9]+-[0-9]+)/i);
  if (issueMatch) {
    const singleIssueId = issueMatch[1].toUpperCase();
    console.log(`Detected single issue ID: ${singleIssueId}`);
    triageSingleIssue(singleIssueId);
    process.exit(0);
  }
  
  // Case 2: Team Cycle URL (e.g., https://linear.app/buildwithfoundation/team/FOU/cycle/active)
  const teamCycleMatch = url.match(/\/team\/([^\/]+)\/cycle\/([^\/]+)/i);
  if (teamCycleMatch) {
    team = teamCycleMatch[1];
    cycle = teamCycleMatch[2];
    console.log(`Parsed team: ${team}, cycle: ${cycle} from URL`);
  } else {
    // Case 3: Team URL only
    const teamMatch = url.match(/\/team\/([^\/]+)/i);
    if (teamMatch) {
      team = teamMatch[1];
      console.log(`Parsed team: ${team} from URL`);
    }
  }
}

// Get directory target folder
const today = new Date().toLocaleDateString('sv-SE'); // YYYY-MM-DD local format
const targetDir = targetDirOverride 
  ? path.resolve(targetDirOverride)
  : path.join(process.cwd(), 'temp', 'linear', today);

console.log(`Triaging into folder: ${targetDir}`);
fs.mkdirSync(targetDir, { recursive: true });

// Determine query filters
let queryCmd = 'bunx linear issue query --json --limit 100';

if (team) {
  queryCmd += ` --team ${team}`;
} else if (!assignee && !url) {
  // If no team, no assignee, and no url, query all teams
  queryCmd += ' --all-teams';
}

if (cycle) {
  queryCmd += ` --cycle ${cycle}`;
}

// Resolve assignee
if (!assignee && !team && !cycle && !url) {
  const defaultUser = getLoggedInUser();
  if (defaultUser) {
    assignee = defaultUser;
    console.log(`Automatically detected logged-in user: ${assignee}`);
  } else {
    // Fallback to Chris's known user accounts
    assignee = 'chris.esplin';
    console.log(`Could not detect logged-in user. Defaulting to: ${assignee}`);
  }
}

if (assignee) {
  queryCmd += ` --assignee ${assignee}`;
}

// If not showing all states and no specific states requested, query active ones
if (!allStates) {
  queryCmd += ' --state started --state unstarted';
}

console.log(`Executing query: ${queryCmd}`);
const queryResultJson = runCmd(queryCmd);

if (!queryResultJson) {
  console.error('✗ Failed to query issues. Please check if you are authenticated via "bunx linear auth login".');
  process.exit(1);
}

let data;
try {
  data = JSON.parse(queryResultJson);
} catch (err) {
  console.error('✗ Failed to parse JSON response from Linear CLI.');
  process.exit(1);
}

const issues = data.nodes || [];
if (issues.length === 0) {
  console.log('No issues matched the filters.');
  
  // Write an empty summary just to be clean
  fs.writeFileSync(
    path.join(targetDir, 'summary.md'),
    `# Linear Triage Summary - ${today}\n\nNo issues found matching the query.\n\n*Query:* \`${queryCmd}\`\n`
  );
  process.exit(0);
}

console.log(`Found ${issues.length} issue(s). Starting triage details download...`);

// Let's keep track of issues for the summary
const triagedIssues = [];

for (const issue of issues) {
  const id = issue.identifier;
  console.log(`-> Fetching details for ${id}: ${issue.title}`);
  
  // Fetch issue full view (markdown)
  const viewContent = runCmd(`bunx linear issue view ${id}`) || '_No description available or fetch failed._';
  
  // Fetch comments
  const commentsContent = runCmd(`bunx linear issue comment list ${id}`) || 'No comments found for this issue';
  
  // Formulate local markdown file
  const labelsList = issue.labels?.nodes?.map(l => l.name).join(', ') || 'None';
  const issueMarkdown = `---
id: ${id}
title: ${issue.title}
url: ${issue.url}
state: ${issue.state?.name || 'Unknown'}
priority: ${issue.priorityLabel || 'No Priority'}
assignee: ${issue.assignee?.name || 'Unassigned'}
project: ${issue.project?.name || 'None'}
cycle: ${issue.cycle ? 'Cycle ' + issue.cycle.number : 'None'}
labels: ${labelsList}
triagedAt: ${new Date().toISOString()}
---

# ${id}: ${issue.title}

*   **URL:** [Linear Link](${issue.url})
*   **State:** \`${issue.state?.name || 'Unknown'}\`
*   **Priority:** \`${issue.priorityLabel || 'No Priority'}\`
*   **Assignee:** ${issue.assignee?.name || 'Unassigned'} (${issue.assignee?.displayName || ''})
*   **Project:** ${issue.project?.name || 'None'}
*   **Cycle:** ${issue.cycle ? 'Cycle ' + issue.cycle.number : 'None'}
*   **Labels:** \`${labelsList}\`

---

${viewContent}

---

## Comments

${commentsContent}
`;

  const fileName = `${id}.md`;
  const filePath = path.join(targetDir, fileName);
  fs.writeFileSync(filePath, issueMarkdown, 'utf8');
  
  triagedIssues.push({
    id,
    title: issue.title,
    url: issue.url,
    state: issue.state?.name || 'Unknown',
    priority: issue.priorityLabel || 'No Priority',
    assignee: issue.assignee?.name || 'Unassigned',
    fileName
  });
}

// Generate the master summary.md
console.log('Generating summary.md...');

let summaryMd = `# Linear Triage Summary - ${today}

Total Issues Triaged: **${triagedIssues.length}**

| ID | Title | State | Priority | Assignee | Local Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
`;

for (const issue of triagedIssues) {
  summaryMd += `| **[${issue.id}](${issue.url})** | ${issue.title} | \`${issue.state}\` | \`${issue.priority}\` | ${issue.assignee} | [${issue.fileName}](./${issue.fileName}) |\n`;
}

summaryMd += `
---
*Generated by quiver-hq Linear Triage Skill on ${new Date().toLocaleString()}*
*Query parameters:* \`${queryCmd}\`
`;

fs.writeFileSync(path.join(targetDir, 'summary.md'), summaryMd, 'utf8');
console.log(`✓ Successfully triaged ${triagedIssues.length} issues into ${targetDir}`);


// Helper function to triage a single issue specifically
function triageSingleIssue(issueId) {
  const viewContent = runCmd(`bunx linear issue view ${issueId}`);
  if (!viewContent) {
    console.error(`✗ Could not find or fetch issue: ${issueId}`);
    process.exit(1);
  }
  
  const commentsContent = runCmd(`bunx linear issue comment list ${issueId}`) || 'No comments found';
  
  // Extract info from view output or make a basic one
  const targetDir = path.join(process.cwd(), 'temp', 'linear', today);
  fs.mkdirSync(targetDir, { recursive: true });
  
  const issueMarkdown = `---
id: ${issueId}
triagedAt: ${new Date().toISOString()}
---

${viewContent}

---

## Comments

${commentsContent}
`;

  const filePath = path.join(targetDir, `${issueId}.md`);
  fs.writeFileSync(filePath, issueMarkdown, 'utf8');
  
  // Write a simple summary for this single issue
  const summaryMd = `# Linear Triage Summary - ${today} (Single Issue)

Triaged single issue: **[${issueId}](https://linear.app/issue/${issueId})**

*   Local File: [${issueId}.md](./${issueId}.md)
*   Time: ${new Date().toLocaleString()}

---
${viewContent}
`;
  
  fs.writeFileSync(path.join(targetDir, 'summary.md'), summaryMd, 'utf8');
  console.log(`✓ Successfully triaged single issue ${issueId} into ${targetDir}`);
}
