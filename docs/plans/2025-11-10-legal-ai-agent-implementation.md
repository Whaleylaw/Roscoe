# Legal AI Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a general-purpose personal AI assistant using Claude Agent SDK with extensible architecture for legal workflows.

**Architecture:** Pure Claude SDK with layered architecture (Main Agent → Skills/Subagents/MCP Tools), TypeScript/Node.js, local CLI interface with future CopilotKit UI integration.

**Tech Stack:** @anthropic-ai/claude-agent-sdk, TypeScript, Node.js, readline (CLI), MCP servers (Supabase, Perplexity, filesystem, Archon)

---

## Task 1: Project Initialization

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `.env.example`
- Create: `README.md`

**Step 1: Initialize Node.js project**

Run:
```bash
npm init -y
```

Expected: `package.json` created

**Step 2: Install dependencies**

Run:
```bash
npm install @anthropic-ai/claude-agent-sdk typescript @types/node tsx
npm install --save-dev @types/readline
```

Expected: Dependencies installed, `package-lock.json` created

**Step 3: Create tsconfig.json**

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "moduleResolution": "node"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Step 4: Update package.json scripts**

Edit `package.json` to add:
```json
{
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

**Step 5: Create .env.example**

Create `.env.example`:
```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Perplexity
PERPLEXITY_API_KEY=pplx-...
```

**Step 6: Create README.md**

Create `README.md`:
```markdown
# Whaley Law Firm AI Agent

General-purpose AI assistant built with Claude Agent SDK.

## Setup

1. Copy `.env.example` to `.env` and fill in API keys
2. Install dependencies: `npm install`
3. Run agent: `npm run dev`

## Usage

```bash
npm run dev
```

Type queries at the `You:` prompt. Type `exit` to quit.

## Architecture

- **Main Agent**: Claude SDK with streaming responses
- **Skills**: Loaded from `.claude/skills/`
- **Subagents**: Specialized agents (legal-researcher, document-analyzer, etc.)
- **MCP Servers**: Supabase, Perplexity, filesystem, Archon

## Development

- `npm run dev` - Run in development mode
- `npm run build` - Build TypeScript
- `npm start` - Run built JavaScript
```

**Step 7: Create src/ directory structure**

Run:
```bash
mkdir -p src/agent src/mcp src/utils
```

**Step 8: Commit project initialization**

Run:
```bash
git add .
git commit -m "feat: initialize TypeScript project for legal AI agent

- Set up package.json with Claude SDK dependency
- Configure TypeScript with strict mode
- Add development scripts (dev, build, start)
- Create project structure (src/agent, src/mcp, src/utils)
- Add .env.example for API keys"
```

Expected: Clean commit with project foundation

---

## Task 2: MCP Server Configuration

**Files:**
- Create: `.mcp.json`
- Modify: `.gitignore` (add node_modules, dist, .env)

**Step 1: Create .mcp.json**

Create `.mcp.json` in project root:
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-supabase"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_SERVICE_ROLE_KEY": "${SUPABASE_SERVICE_ROLE_KEY}"
      }
    },
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-perplexity"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_PATHS": "${PWD}/converted_documents:${PWD}/docs"
      }
    },
    "archon": {
      "type": "http",
      "url": "http://localhost:8051/mcp"
    }
  }
}
```

**Step 2: Update .gitignore**

Add to `.gitignore`:
```
# TypeScript/Node.js (add to existing)
node_modules/
dist/
.env
*.tsbuildinfo
```

**Step 3: Verify environment variables**

Run:
```bash
# Check if .env exists in parent directory (it does from CLAUDE.md context)
ls -la ../.env
```

Expected: `.env` file exists in parent directory with required keys

**Step 4: Commit MCP configuration**

Run:
```bash
git add .mcp.json .gitignore
git commit -m "feat: configure MCP servers for database, search, and file access

- Add Supabase MCP for database operations
- Add Perplexity MCP for web search with citations
- Add filesystem MCP for document access
- Add Archon HTTP MCP for knowledge base
- Update .gitignore for Node.js artifacts"
```

---

## Task 3: Agent Configuration Module

**Files:**
- Create: `src/agent/config.ts`

**Step 1: Write config.ts**

Create `src/agent/config.ts`:
```typescript
import { ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

/**
 * Get agent configuration options for Claude SDK
 * Loads skills from filesystem and enables all core tools + MCP
 */
export function getAgentOptions(): ClaudeAgentOptions {
  return {
    // Current working directory
    cwd: process.cwd(),

    // Load skills from filesystem (.claude/skills/, ~/.claude/skills/)
    settingSources: ["user", "project"],

    // Enable all core tools + MCP
    allowedTools: [
      // Skills system
      "Skill",

      // File operations
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",

      // Code execution
      "Bash",

      // Supabase MCP tools
      "mcp__supabase__execute_sql",
      "mcp__supabase__list_tables",
      "mcp__supabase__apply_migration",
      "mcp__supabase__get_advisors",
      "mcp__supabase__get_logs",

      // Perplexity MCP tools
      "mcp__perplexity__search",
      "mcp__perplexity__reason",
      "mcp__perplexity__deep_research",

      // Filesystem MCP tools
      "mcp__filesystem__read_file",
      "mcp__filesystem__list_files",

      // Archon MCP tools
      "mcp__archon__rag_search_knowledge_base",
      "mcp__archon__rag_search_code_examples",
      "mcp__archon__find_tasks",
      "mcp__archon__find_projects",
    ],

    // MCP servers auto-loaded from .mcp.json
    mcpServers: {},
  };
}
```

**Step 2: Verify TypeScript compilation**

Run:
```bash
npx tsc --noEmit
```

Expected: No compilation errors

**Step 3: Commit agent configuration**

Run:
```bash
git add src/agent/config.ts
git commit -m "feat: add agent configuration with skills and MCP tools

- Configure settingSources for filesystem skills loading
- Enable core tools (Read, Write, Edit, Glob, Grep, Bash)
- Enable Supabase MCP tools for database access
- Enable Perplexity MCP for web search and research
- Enable filesystem MCP for document access
- Enable Archon MCP for knowledge base queries"
```

---

## Task 4: Subagent Definitions

**Files:**
- Create: `src/agent/subagents.ts`

**Step 1: Write subagents.ts**

Create `src/agent/subagents.ts`:
```typescript
import { AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

/**
 * Subagent definitions for specialized tasks
 * These agents are programmatically defined and invoked by the main agent
 */
export const subagents: Record<string, AgentDefinition> = {

  "legal-researcher": {
    description: "Use for legal research, case law searches, and statute lookups. Expert in finding relevant precedents and legal authority.",
    prompt: `You are a legal research specialist with deep knowledge of legal research methodologies.

When conducting research:
- Search multiple sources (Perplexity for case law, Archon knowledge base for firm precedents)
- Cite all sources with proper legal citations
- Summarize key holdings and relevance to current matter
- Identify applicable statutes and regulations

Always provide thorough, well-cited research.`,
    tools: [
      "mcp__perplexity__search",
      "mcp__perplexity__reason",
      "mcp__archon__rag_search_knowledge_base",
      "Read",
      "Grep"
    ],
    model: "sonnet"
  },

  "document-analyzer": {
    description: "Use PROACTIVELY for analyzing legal documents, contracts, medical records, or case files. Extracts key facts and identifies issues.",
    prompt: `You are a document analysis specialist for a personal injury law firm.

When analyzing documents:
- Extract key facts, dates, parties, amounts
- Identify potential issues or red flags
- Summarize medical findings and injuries
- Note missing information or gaps
- Organize findings clearly

Focus on thoroughness and accuracy.`,
    tools: [
      "Read",
      "Grep",
      "Glob",
      "mcp__filesystem__read_file",
      "mcp__filesystem__list_files"
    ],
    model: "sonnet"
  },

  "database-specialist": {
    description: "Use for complex Supabase queries, data analysis, or database operations. Expert in SQL and case data structures.",
    prompt: `You are a database specialist with expertise in Supabase and PostgreSQL.

When working with data:
- Write efficient, safe SQL queries
- Use proper JOINs and indexes
- Analyze data patterns and relationships
- Suggest data improvements
- Always use READ-ONLY queries unless explicitly asked to modify data

Prioritize data integrity and query performance.`,
    tools: [
      "mcp__supabase__execute_sql",
      "mcp__supabase__list_tables",
      "mcp__supabase__get_advisors"
    ],
    model: "sonnet"
  },

  "code-runner": {
    description: "Use for running code, scripts, or computational tasks. Safe execution environment.",
    prompt: `You are a code execution specialist.

When running code:
- Validate inputs and outputs
- Handle errors gracefully
- Provide clear execution results
- Suggest optimizations if relevant

Execute code safely and efficiently.`,
    tools: ["Bash", "Read", "Write"],
    model: "haiku"  // Faster for simple execution
  }

};
```

**Step 2: Verify TypeScript compilation**

Run:
```bash
npx tsc --noEmit
```

Expected: No compilation errors

**Step 3: Commit subagent definitions**

Run:
```bash
git add src/agent/subagents.ts
git commit -m "feat: add initial subagent definitions

- legal-researcher: legal research and case law queries
- document-analyzer: document analysis and fact extraction
- database-specialist: Supabase query specialist
- code-runner: safe code execution with Haiku model

Each subagent has specialized prompts, tool restrictions, and model selection."
```

---

## Task 5: Core Agent Implementation

**Files:**
- Create: `src/agent/core.ts`

**Step 1: Write core.ts**

Create `src/agent/core.ts`:
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { getAgentOptions } from "./config";
import { subagents } from "./subagents";

/**
 * Main agent execution function
 * Streams responses from Claude SDK with full tool and subagent support
 */
export async function runAgent(userPrompt: string): Promise<void> {
  const options = getAgentOptions();
  options.agents = subagents;

  console.log("🤖 Agent starting...\n");

  try {
    for await (const message of query({
      prompt: userPrompt,
      options
    })) {

      switch (message.type) {
        case "system":
          handleSystemMessage(message);
          break;

        case "thought":
          console.log(`💭 ${message.content}`);
          break;

        case "tool_use":
          console.log(`🔧 Using tool: ${message.tool_name}`);
          if (message.tool_input) {
            console.log(`   Input: ${JSON.stringify(message.tool_input).substring(0, 100)}...`);
          }
          break;

        case "tool_result":
          // Don't log full results - can be very verbose
          console.log(`   ✓ Tool completed`);
          break;

        case "result":
          if (message.subtype === "success") {
            console.log(`\n✅ Task completed\n`);
          } else if (message.subtype === "error_during_execution") {
            console.error(`\n❌ Error: ${message.error}\n`);
          }
          break;

        case "text":
          process.stdout.write(message.content);
          break;

        default:
          // Log unknown message types for debugging
          console.log(`[${message.type}]`, message);
      }
    }

    // Add newline after streaming completes
    console.log("\n");

  } catch (error) {
    console.error("❌ Agent error:", error);
    throw error;
  }
}

/**
 * Handle system initialization messages
 */
function handleSystemMessage(message: any): void {
  if (message.subtype === "init") {
    console.log("📋 Skills loaded:", message.skills?.length || 0);
    console.log("🔌 MCP servers:", message.mcp_servers?.length || 0);

    // Check for failed MCP servers
    const failed = message.mcp_servers?.filter((s: any) => s.status !== "connected");
    if (failed && failed.length > 0) {
      console.warn("⚠️  Failed MCP servers:", failed.map((s: any) => s.name).join(", "));
    }

    console.log();
  }
}
```

**Step 2: Verify TypeScript compilation**

Run:
```bash
npx tsc --noEmit
```

Expected: No compilation errors

**Step 3: Commit core agent**

Run:
```bash
git add src/agent/core.ts
git commit -m "feat: implement core agent with streaming support

- Stream responses from Claude SDK query() function
- Handle all message types (system, thought, tool_use, result, text)
- Display system initialization info (skills, MCP servers)
- Warn on failed MCP server connections
- Graceful error handling and logging"
```

---

## Task 6: CLI Interface

**Files:**
- Create: `src/index.ts`

**Step 1: Write index.ts**

Create `src/index.ts`:
```typescript
import { runAgent } from "./agent/core";
import * as readline from "readline";

/**
 * Main CLI entry point
 * Provides interactive readline interface for querying the agent
 */
async function main() {
  console.log("🏛️  Whaley Law Firm - AI Assistant");
  console.log("═══════════════════════════════════════");
  console.log("Type your queries below. Type 'exit' to quit.\n");

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: "You: "
  });

  rl.prompt();

  rl.on("line", async (input: string) => {
    const trimmed = input.trim();

    // Handle exit command
    if (trimmed.toLowerCase() === "exit") {
      console.log("\nGoodbye!");
      process.exit(0);
    }

    // Skip empty input
    if (!trimmed) {
      rl.prompt();
      return;
    }

    // Run agent with user input
    try {
      await runAgent(trimmed);
    } catch (error) {
      console.error("Error running agent:", error);
    }

    // Show prompt for next query
    rl.prompt();
  });

  // Handle Ctrl+C
  rl.on("close", () => {
    console.log("\nGoodbye!");
    process.exit(0);
  });
}

// Start the CLI
main().catch(console.error);
```

**Step 2: Verify TypeScript compilation**

Run:
```bash
npx tsc --noEmit
```

Expected: No compilation errors

**Step 3: Test basic compilation**

Run:
```bash
npm run build
```

Expected: TypeScript compiles successfully, `dist/` directory created

**Step 4: Commit CLI interface**

Run:
```bash
git add src/index.ts
git commit -m "feat: add interactive CLI interface

- Readline interface for user queries
- Exit command support
- Ctrl+C handling
- Error handling for agent failures
- Friendly prompts and formatting"
```

---

## Task 7: Environment Setup & First Test

**Files:**
- Modify: `../.env` (verify keys exist)

**Step 1: Verify parent directory .env**

Run:
```bash
ls -la ../.env && echo "✓ .env exists"
cat ../.env | grep -E "ANTHROPIC_API_KEY|SUPABASE_URL|PERPLEXITY_API_KEY" | wc -l
```

Expected: Shows 3 (all required keys present)

**Step 2: Create symlink to parent .env (for convenience)**

Run:
```bash
ln -s ../.env .env
```

Expected: Symlink created

**Step 3: Test agent startup (basic query)**

Run:
```bash
echo "What skills do you have?" | npm run dev
```

Expected:
- Agent starts without errors
- Skills load successfully
- MCP servers connect (or show clear warnings)
- Agent responds with list of available skills

**Step 4: Test MCP connectivity**

Run:
```bash
echo "List tables in Supabase" | npm run dev
```

Expected:
- Supabase MCP connects
- Tables listed (case_projects, doc_files, etc.)

**Step 5: Commit environment setup**

Run:
```bash
git add .env
git commit -m "feat: link to parent .env for API keys

- Symlink to parent directory .env
- Provides access to ANTHROPIC_API_KEY, SUPABASE_*, PERPLEXITY_API_KEY
- Allows agent to connect to all MCP servers"
```

---

## Task 8: Testing & Validation

**Files:**
- Create: `test-queries.sh` (manual test script)

**Step 1: Create test script**

Create `test-queries.sh`:
```bash
#!/bin/bash
# Manual testing script for legal AI agent

echo "=== Test 1: Skills Check ==="
echo "What skills do you have available?" | npm run dev
echo ""

echo "=== Test 2: Supabase Connection ==="
echo "List all tables in the Supabase database" | npm run dev
echo ""

echo "=== Test 3: Filesystem Access ==="
echo "What converted documents exist for case Colleen-Colvin-MVA-10-01-2023?" | npm run dev
echo ""

echo "=== Test 4: Web Search ==="
echo "What is the statute of limitations for personal injury in Kentucky?" | npm run dev
echo ""

echo "=== Test 5: Document Analysis Subagent ==="
echo "Use the document-analyzer to list medical files in converted_documents" | npm run dev
echo ""

echo "=== Test 6: Database Query Subagent ==="
echo "Use the database-specialist to show schema for case_projects table" | npm run dev
echo ""

echo "=== All tests complete ==="
```

**Step 2: Make script executable**

Run:
```bash
chmod +x test-queries.sh
```

**Step 3: Run test suite**

Run:
```bash
./test-queries.sh 2>&1 | tee test-output.log
```

Expected:
- All tests run successfully
- Skills load
- MCP servers connect
- Subagents invoke correctly
- No critical errors

**Step 4: Review test output**

Run:
```bash
grep -E "✅|❌|⚠️" test-output.log
```

Expected: Mostly ✅ (success), investigate any ❌ (errors)

**Step 5: Commit test script**

Run:
```bash
git add test-queries.sh
git commit -m "test: add manual testing script

Tests:
1. Skills availability
2. Supabase MCP connection
3. Filesystem access to converted documents
4. Perplexity web search
5. Document analyzer subagent
6. Database specialist subagent

Run with: ./test-queries.sh"
```

---

## Task 9: Documentation Updates

**Files:**
- Modify: `README.md`
- Create: `docs/USAGE.md`

**Step 1: Update README.md**

Edit `README.md` to add:
```markdown
## Features

- **Skills System**: Automatically loads skills from `.claude/skills/`
- **Subagents**: Specialized agents (legal-researcher, document-analyzer, database-specialist, code-runner)
- **MCP Servers**:
  - Supabase (database access)
  - Perplexity (web search)
  - Filesystem (document access)
  - Archon (knowledge base)
- **Streaming Responses**: Real-time output from Claude
- **Interactive CLI**: Readline interface with command history

## Testing

Run manual tests:
```bash
./test-queries.sh
```

## Examples

```bash
# Legal research
You: What is the statute of limitations for personal injury in Kentucky?

# Document analysis
You: Analyze medical records for the Wayne-Weber case

# Database query
You: Show all open MVA cases with settlement amounts over $50,000

# Code execution
You: Calculate total medical expenses for case ABC-123
```

## Project Structure

- `src/index.ts` - CLI entry point
- `src/agent/core.ts` - Main agent logic
- `src/agent/config.ts` - Agent configuration
- `src/agent/subagents.ts` - Subagent definitions
- `.mcp.json` - MCP server configuration
- `.claude/skills/` - Project skills
```

**Step 2: Create USAGE.md**

Create `docs/USAGE.md`:
```markdown
# Usage Guide - Legal AI Agent

## Starting the Agent

```bash
npm run dev
```

## Basic Queries

### Legal Research
- "What is the statute of limitations for personal injury in Kentucky?"
- "Find recent case law on comparative negligence"
- "What are the elements of a premises liability claim?"

### Document Analysis
- "Analyze medical records in the Wayne-Weber case"
- "Extract key facts from the police report in case MVA-2024-001"
- "Summarize injuries documented in medical file XYZ"

### Database Queries
- "List all open MVA cases"
- "Show cases with medical liens over $10,000"
- "Find cases handled by Dr. Smith"

### File Operations
- "List converted documents for case ABC-123"
- "Search for 'whiplash' in medical records"
- "Show folder structure for premises liability cases"

## Subagents

Subagents are automatically invoked based on task relevance:

- **legal-researcher**: Legal research and citations
- **document-analyzer**: Document analysis and fact extraction
- **database-specialist**: Complex SQL queries
- **code-runner**: Computational tasks

You can explicitly request a subagent:
```
Use the document-analyzer to review the settlement demand
```

## Skills

Skills are loaded from `.claude/skills/` and invoked automatically:
- `brainstorming` - Design refinement
- `systematic-debugging` - Debugging workflows
- `test-driven-development` - TDD processes
- (23+ total skills)

## Tips

1. **Be specific**: "Analyze medical records for Case-123" is better than "analyze docs"
2. **Request citations**: "Find case law with citations"
3. **Use subagents**: "Use database-specialist to query X"
4. **Check MCP status**: "What MCP servers are connected?"

## Troubleshooting

### MCP Server Not Connected
```
⚠️  Failed MCP servers: perplexity
```
**Fix**: Check API key in `.env`, verify MCP server package installed

### Skills Not Loading
```
📋 Skills loaded: 0
```
**Fix**: Verify `.claude/skills/` exists, check `settingSources` configuration

### Database Query Fails
**Fix**: Check Supabase credentials, verify table names, test with simple query first
```

**Step 3: Commit documentation**

Run:
```bash
git add README.md docs/USAGE.md
git commit -m "docs: add comprehensive usage guide and examples

- Update README with features, testing, examples
- Create USAGE.md with detailed query examples
- Document subagent invocation patterns
- Add troubleshooting section for common issues"
```

---

## Task 10: Final Integration Test

**Step 1: Interactive test session**

Run:
```bash
npm run dev
```

Test each capability:
1. "What skills are available?"
2. "List Supabase tables"
3. "Use document-analyzer to list files in converted_documents"
4. "What is premises liability under Kentucky law?"
5. "exit"

Expected: All queries work, agent responds appropriately

**Step 2: Verify git status**

Run:
```bash
git status
```

Expected: Working directory clean

**Step 3: Create final commit**

Run:
```bash
git commit --allow-empty -m "chore: mark legal AI agent v1.0 complete

Core features implemented:
- ✅ Claude Agent SDK integration
- ✅ Skills system (23+ skills loaded)
- ✅ Subagent definitions (4 initial agents)
- ✅ MCP servers (Supabase, Perplexity, filesystem, Archon)
- ✅ Streaming CLI interface
- ✅ Comprehensive testing
- ✅ Documentation

Ready for legal-specific skill development and production use."
```

**Step 4: Tag release**

Run:
```bash
git tag -a v1.0.0 -m "Legal AI Agent v1.0.0 - Core Platform"
```

---

## Next Steps (Future Development)

### Week 2: Legal-Specific Skills

Create first legal skill:
- `demand-letter-drafting/SKILL.md`
- `medical-record-analysis/SKILL.md`
- `settlement-calculation/SKILL.md`

### Week 3: Advanced Subagents

Add specialized legal subagents:
- `medical-records-specialist`
- `settlement-negotiator`
- `discovery-specialist`

### Week 4: UI Integration

Explore CopilotKit integration:
- Create Next.js app with CopilotKit
- Wrap existing agent in CopilotRuntime
- Test UI with existing skills/subagents

---

## Success Criteria Checklist

- [ ] TypeScript project compiles without errors
- [ ] All dependencies installed correctly
- [ ] MCP servers configured and connecting
- [ ] Skills loading from `.claude/skills/`
- [ ] Subagents defined and invocable
- [ ] CLI interface functional (readline, exit, prompts)
- [ ] Can query Supabase database
- [ ] Can search web with Perplexity
- [ ] Can access converted documents
- [ ] Can invoke Archon knowledge base
- [ ] Test script runs successfully
- [ ] Documentation complete and accurate
- [ ] Git commits clean and descriptive
- [ ] Ready for legal skill development

---

## Troubleshooting

### "Module not found" errors
- Run `npm install` again
- Check `tsconfig.json` paths
- Verify `node_modules/` exists

### MCP server connection failures
- Check `.env` file has correct keys
- Verify MCP server packages installed (`npx -y @modelcontextprotocol/server-*`)
- Test individual MCP server with `npx`

### Skills not loading
- Verify `.claude/skills/` directory exists
- Check `settingSources: ["user", "project"]` in config
- Run `ls -la .claude/skills/*/SKILL.md` to confirm files

### TypeScript compilation errors
- Run `npx tsc --noEmit` to check specific errors
- Verify all imports are correct
- Check `tsconfig.json` configuration

---

## Implementation Notes

This plan follows:
- **DRY**: Reuse configuration, avoid duplication
- **YAGNI**: Build only what's needed now, extend later
- **TDD**: Manual testing throughout, automated tests later
- **Frequent commits**: One commit per task, clear messages

Each task is designed to be completable in 10-20 minutes, with clear verification steps.

Use @superpowers:executing-plans to run this plan task-by-task in a dedicated session.
