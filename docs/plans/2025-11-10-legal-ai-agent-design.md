# Legal AI Agent - Design Document

**Date:** November 10, 2025
**Author:** Claude Code (with Aaron Whaley)
**Status:** Approved for Implementation

## Executive Summary

This document outlines the design for a general-purpose personal AI assistant agent for Whaley Law Firm, built using the Claude Agent SDK. The agent will serve as a foundation platform with extensible capabilities for legal workflows, starting with core tools and expanding to domain-specific legal skills and subagents over time.

## Goals

### Primary Goal
Build a general-purpose personal assistant agent powered by Claude SDK with:
- Core capabilities (web search, code execution, file operations, database access)
- Extensible architecture (skills system, workflow system, tool registration)
- Sub-agent support (spawn specialized agents for specific tasks)
- Foundation for legal-specific enhancements

### Secondary Goals
- Enable iterative addition of legal-specific skills/workflows/tools
- Support both CLI interaction (immediate) and future UI integration (CopilotKit)
- Leverage existing infrastructure (Supabase, converted documents, Archon knowledge base)
- Maintain compatibility with Claude Code patterns and skills

## Architecture

### Approach: Pure Claude SDK with Layered Architecture

```
┌─────────────────────────────────────────┐
│     Main Agent (CLI Entry Point)        │
│  - query() with streaming responses     │
│  - settingSources: ["user", "project"]  │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴───────────┬──────────────┐
    │                        │              │
┌───▼────┐         ┌────────▼────┐    ┌───▼────────┐
│ Skills │         │ Subagents   │    │ MCP Tools  │
│System  │         │ (programm.) │    │ (.mcp.json)│
└────────┘         └─────────────┘    └────────────┘
```

**Key Architectural Decisions:**
- **Language**: TypeScript/Node.js (better CopilotKit integration, modern ecosystem)
- **Framework**: Pure Claude Agent SDK (native patterns, no framework complexity)
- **Skills**: Filesystem-based (reuse existing, easy to add legal-specific)
- **Subagents**: Programmatic definition (type-safe, version controlled)
- **MCP Servers**: Configuration-based (flexible, extensible)
- **Deployment**: Local CLI first, UI layer later

## Project Structure

```
whaley-law-agent/
├── src/
│   ├── index.ts                 # Main CLI entry point
│   ├── agent/
│   │   ├── core.ts              # Core agent logic with query()
│   │   ├── config.ts            # Agent configuration & options
│   │   └── subagents.ts         # Subagent definitions
│   ├── mcp/
│   │   └── servers.ts           # MCP server configurations
│   └── utils/
│       ├── streaming.ts         # Stream handling utilities
│       └── logger.ts            # Logging setup
├── .claude/
│   ├── skills/                  # Project-specific skills
│   └── agents/                  # Additional agent definitions (optional)
├── .mcp.json                    # MCP server configuration
├── package.json
├── tsconfig.json
└── README.md
```

## Component Designs

### 1. MCP Server Configuration

**File: `.mcp.json`**

Configured MCP servers provide access to:
- **Supabase**: Database queries, table operations, migrations
- **Perplexity**: Web search with citations, reasoning
- **Filesystem**: Read converted Markdown documents, case files
- **Archon**: RAG knowledge base, project management, task tracking

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

### 2. Agent Configuration

**File: `src/agent/config.ts`**

Core configuration for the Claude Agent SDK:

```typescript
import { ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

export function getAgentOptions(): ClaudeAgentOptions {
  return {
    cwd: process.cwd(),

    // Load skills from filesystem
    settingSources: ["user", "project"],

    // Enable all core tools + MCP
    allowedTools: [
      // Skills system
      "Skill",

      // File operations
      "Read", "Write", "Edit", "Glob", "Grep",

      // Code execution
      "Bash",

      // MCP tools (expandable)
      "mcp__supabase__execute_sql",
      "mcp__supabase__list_tables",
      "mcp__supabase__apply_migration",
      "mcp__perplexity__search",
      "mcp__perplexity__reason",
      "mcp__filesystem__list_files",
      "mcp__filesystem__read_file",
      "mcp__archon__rag_search_knowledge_base",
      "mcp__archon__find_tasks",
    ],

    // MCP servers auto-loaded from .mcp.json
    mcpServers: {},
  };
}
```

### 3. Subagent Definitions

**File: `src/agent/subagents.ts`**

Initial subagents (will expand with legal-specific agents):

```typescript
import { AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

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
      "Read", "Grep"
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
      "Read", "Grep", "Glob",
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

### 4. Core Agent Implementation

**File: `src/agent/core.ts`**

Main agent loop with streaming:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { getAgentOptions } from "./config";
import { subagents } from "./subagents";

export async function runAgent(userPrompt: string) {
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
          break;

        case "result":
          if (message.subtype === "success") {
            console.log(`\n✅ ${message.result}\n`);
          } else if (message.subtype === "error_during_execution") {
            console.error(`\n❌ Error: ${message.error}\n`);
          }
          break;

        case "text":
          process.stdout.write(message.content);
          break;
      }
    }
  } catch (error) {
    console.error("Agent error:", error);
    throw error;
  }
}

function handleSystemMessage(message: any) {
  if (message.subtype === "init") {
    console.log("📋 Skills loaded:", message.skills?.length || 0);
    console.log("🔌 MCP servers:", message.mcp_servers?.length || 0);

    const failed = message.mcp_servers?.filter((s: any) => s.status !== "connected");
    if (failed?.length > 0) {
      console.warn("⚠️  Failed MCP servers:", failed.map((s: any) => s.name));
    }
    console.log();
  }
}
```

### 5. CLI Interface

**File: `src/index.ts`**

Interactive command-line interface:

```typescript
import { runAgent } from "./agent/core";
import readline from "readline";

async function main() {
  console.log("🏛️  Whaley Law Firm - AI Assistant");
  console.log("═══════════════════════════════════\n");

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: "You: "
  });

  rl.prompt();

  rl.on("line", async (input) => {
    if (input.trim().toLowerCase() === "exit") {
      console.log("Goodbye!");
      process.exit(0);
    }

    if (input.trim()) {
      await runAgent(input);
    }

    rl.prompt();
  });
}

main().catch(console.error);
```

## Skills System Integration

The agent will automatically load existing skills from `.claude/skills/`:

**Current Skills (Dev-focused):**
- `using-superpowers` - Mandatory workflow skill
- `brainstorming` - Design refinement
- `systematic-debugging` - Debugging framework
- `test-driven-development` - TDD workflow
- `supabase-edge-functions-specialist` - Supabase expertise
- ... (23+ total existing skills)

**Future Legal Skills (To Be Added):**
- `demand-letter-drafting` - Generate demand letters from case data
- `medical-record-analysis` - Extract injuries, treatments, providers
- `settlement-calculation` - Calculate settlement values based on damages
- `deposition-prep` - Prepare deposition questions from case facts
- `timeline-generation` - Create case timelines from documents/notes

Skills are automatically invoked by Claude when relevant to the task based on their `description` field in the SKILL.md frontmatter.

## Testing Strategy

### Phase 1: Core Agent Testing
```bash
# Test basic initialization
npm run dev "What skills do you have available?"

# Test MCP connectivity
npm run dev "List all tables in the Supabase database"

# Test file system access
npm run dev "What converted documents do we have for case Colleen-Colvin-MVA-10-01-2023?"

# Test web search
npm run dev "What are the statute of limitations for personal injury in Kentucky?"
```

### Phase 2: Subagent Testing
```bash
# Test document analyzer
npm run dev "Analyze the medical records in the Wayne-Weber case"

# Test legal researcher
npm run dev "Find recent Kentucky case law on comparative negligence"

# Test database specialist
npm run dev "Show me all open MVA cases with medical providers listed"
```

### Success Criteria
- ✅ Agent starts without errors
- ✅ All MCP servers connect successfully
- ✅ Skills load from `.claude/skills/`
- ✅ Subagents spawn correctly
- ✅ Streaming responses work smoothly
- ✅ Can access Supabase data
- ✅ Can read converted documents
- ✅ Web search returns results

## Development Roadmap

### Week 1: Foundation
- Set up TypeScript project structure
- Configure Claude SDK with basic options
- Implement CLI with streaming
- Connect to MCP servers (Supabase, filesystem)
- Test basic queries and validation

### Week 2: Skills & Subagents
- Verify existing skills load correctly
- Implement core subagents (legal-researcher, document-analyzer, database-specialist)
- Test subagent invocation patterns
- Add error handling and logging

### Week 3: Legal Domain Customization
- Create first legal-specific skill (e.g., demand-letter-drafting)
- Add case-specific subagent (e.g., medical-records-analyzer)
- Test with real case data
- Iterate based on actual usage patterns

### Week 4: Polish & Optimization
- Add conversation history/memory
- Improve CLI UX (better formatting, colors, progress indicators)
- Add configuration file for user preferences
- Document common workflows and usage patterns

### Post-v1: Enhancements
- Add legal-specific skills as identified needs arise
- Create specialized subagents for different case types (MVA, WC, Premise)
- Integrate additional MCP servers (legal research databases, court filing systems)
- Eventually: Add CopilotKit UI layer for web-based access

## Future Enhancements

### Legal-Specific Subagents (Future)
```typescript
"settlement-negotiator": {
  description: "Expert in settlement negotiations and valuation",
  // Specialized for settlement strategy and calculations
},

"medical-records-specialist": {
  description: "Analyzes medical records for injury documentation",
  // Trained on medical terminology and injury patterns
},

"discovery-specialist": {
  description: "Drafts discovery requests and responses",
  // Knows discovery rules and procedures
}
```

### Additional MCP Servers (Future)
- Westlaw/LexisNexis (if MCP servers become available)
- Court filing systems integration
- Medical records APIs
- Calendar/deadline tracking systems
- Email integration (Gmail MCP)

## Migration Path to CopilotKit

When ready to add a web UI (Phase 2+), minimal code changes required:

```typescript
// Current: CLI agent
import { query } from "@anthropic-ai/claude-agent-sdk";

// Future: Add CopilotKit wrapper
import { CopilotRuntime } from "@copilotkit/runtime";
import { AnthropicAdapter } from "@copilotkit/runtime";

const runtime = new CopilotRuntime({
  adapter: new AnthropicAdapter({
    // Reuse all existing agent config
    ...getAgentOptions(),
  }),
});

// Core agent logic stays the same - just add UI layer
```

**Zero refactoring** of core agent, skills, or subagents needed.

## Design Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Language** | TypeScript/Node.js | Better CopilotKit integration, modern ecosystem |
| **Architecture** | Pure Claude SDK | Native SDK patterns, no framework complexity |
| **Skills** | Filesystem-based | Reuse existing skills, easy to add legal-specific ones |
| **Subagents** | Programmatic | Type-safe, easy to version control and test |
| **MCP Servers** | Configuration-based | Flexible, supports both stdio and HTTP transports |
| **Tools** | File ops + Bash + MCP | Covers all use cases, extensible as needed |
| **Deployment** | Local CLI first | Fast iteration, then add UI layer when ready |
| **Testing** | Manual → Automated | Quick validation initially, build test suite over time |

## Data Flow

### Typical User Interaction
1. User enters query in CLI
2. Main agent (`query()`) processes request
3. Agent autonomously:
   - Checks if skills apply (loads from `.claude/skills/`)
   - Determines if subagent needed (spawns specialized agent)
   - Invokes MCP tools as needed (Supabase, Perplexity, filesystem, Archon)
4. Streams responses back to user in real-time
5. Agent completes with final result or error

### Example: "Analyze medical records for Wayne Weber case"
1. Agent recognizes document analysis task
2. Spawns `document-analyzer` subagent
3. Subagent uses `mcp__filesystem__list_files` to find case folder
4. Subagent reads medical documents with `mcp__filesystem__read_file`
5. Subagent extracts injuries, treatments, providers, dates
6. Results streamed back to main agent
7. Main agent presents summary to user

## Security Considerations

- **API Keys**: Stored in environment variables, never committed to git
- **Database Access**: Uses Supabase service role key (full access) - keep secure
- **File System**: MCP server restricts access to specific paths only
- **Code Execution**: Bash tool enabled - use caution, validate inputs
- **MCP Servers**: Trusted sources only (@modelcontextprotocol, Archon local)

## Dependencies

**Core:**
- `@anthropic-ai/claude-agent-sdk` - Claude Agent SDK
- `typescript` - Type safety
- `readline` - CLI interface

**MCP Servers (external):**
- `@modelcontextprotocol/server-supabase` - Database access
- `@modelcontextprotocol/server-perplexity` - Web search
- `@modelcontextprotocol/server-filesystem` - File operations
- Archon MCP server (local HTTP)

**Development:**
- `tsx` - TypeScript execution
- `@types/node` - Node.js types

## Success Metrics

### Technical Metrics
- Agent startup time < 5 seconds
- MCP server connection success rate > 95%
- Skills loading success rate 100%
- Query response time < 30 seconds for typical requests

### User Metrics
- Can successfully answer legal research questions
- Can analyze documents and extract key information
- Can query case data from Supabase effectively
- CLI is usable and responsive

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| MCP server connectivity failures | High | Graceful degradation, clear error messages, retry logic |
| Skills not loading | Medium | Validation on startup, clear error reporting |
| Subagent invocation issues | Medium | Test thoroughly, add fallback to main agent |
| API rate limits (Perplexity, Anthropic) | Medium | Implement rate limiting, caching where appropriate |
| Large document processing timeouts | Low | Stream results, implement pagination for large datasets |

## Conclusion

This design provides a solid foundation for a general-purpose AI assistant using the Claude Agent SDK. The architecture is:
- **Extensible**: Easy to add legal-specific skills and subagents
- **Maintainable**: Clean separation of concerns, type-safe TypeScript
- **Scalable**: Can grow from CLI to web UI without major refactoring
- **Flexible**: MCP servers and skills can be added/modified independently

The initial focus on core capabilities with dev-focused skills allows for rapid iteration and testing. Legal-specific enhancements will be added incrementally based on actual usage patterns and identified needs.

## Appendices

### A. Relevant Documentation
- Claude Agent SDK: https://docs.claude.com/en/docs/agent-sdk/overview
- Skills Guide: `docs/# Agent Skills in the SDK.md`
- Subagents Guide: `docs/# Subagents in the SDK.md`
- MCP Guide: `docs/# MCP in the SDK.md`

### B. Related Files
- `CLAUDE.md` - Repository overview and development workflows
- `PDF_CONVERSION_README.md` - Document processing pipeline
- `.claude/skills/` - Existing skills directory (23+ skills)

### C. Environment Variables Required
```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
SUPABASE_URL=https://pdhrmsoydwvoafunalez.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Perplexity
PERPLEXITY_API_KEY=pplx-...
```
