/**
 * Tool categorization utilities for Deep Agents UI
 * Categorizes tool names from various sources (LangChain toolkits, MCP servers, RunLoop executor)
 * into visual categories for consistent badge rendering and filtering.
 */

/**
 * Available tool categories for visual grouping and styling
 */
export type MCPCategory =
  | 'supabase'
  | 'tavily'
  | 'gmail'
  | 'calendar'
  | 'code'
  | 'builtin'
  | 'other';

/**
 * Categorizes a tool name into one of the predefined MCPCategory types.
 * Checks categories in specificity order (most specific patterns first) to ensure
 * accurate classification and prevent false positives from generic substring matching.
 *
 * Pattern Matching Order:
 * 1. Builtin tools (exact matches for middleware tools)
 * 2. Code execution (RunLoop executor patterns)
 * 3. Gmail tools (LangChain toolkit patterns)
 * 4. Calendar tools (LangChain toolkit patterns)
 * 5. Supabase tools (MCP server patterns)
 * 6. Tavily tools (MCP server patterns)
 * 7. Other (fallback for uncategorized tools)
 *
 * @param toolName - The name of the tool to categorize (case-insensitive after normalization)
 * @returns One of 7 MCPCategory values: 'builtin' | 'code' | 'gmail' | 'calendar' | 'supabase' | 'tavily' | 'other'
 *
 * @example
 * ```typescript
 * getMCPCategory('runloop_execute_code') // returns 'code'
 * getMCPCategory('create_gmail_draft') // returns 'gmail'
 * getMCPCategory('create_calendar_event') // returns 'calendar'
 * getMCPCategory('write_todos') // returns 'builtin'
 * getMCPCategory('unknown_tool') // returns 'other'
 * getMCPCategory('CREATE_GMAIL_DRAFT') // returns 'gmail' (case-insensitive)
 * ```
 *
 * @note This function is pure with no side effects, suitable for memoization if performance optimization needed.
 * @note Official LangChain toolkit tool names documented in implementation with citation links.
 * @see https://python.langchain.com/docs/integrations/tools/google_gmail - Gmail Toolkit Documentation
 * @see https://python.langchain.com/docs/integrations/tools/google_calendar - Calendar Toolkit Documentation
 * @see https://github.com/runloopai/api-client-python - RunLoop Python SDK
 */
export function getMCPCategory(toolName: string): MCPCategory {
  // Normalize tool name to lowercase for case-insensitive matching
  // This ensures robust matching regardless of tool name casing conventions from different toolkit sources
  const normalizedName = toolName.toLowerCase();

  // PRIORITY 1: Builtin middleware tools (exact matches checked first to prevent false positives)
  // These are the most specific patterns and should be checked first
  if (
    normalizedName === 'write_todos' ||
    normalizedName === 'ls' ||
    normalizedName === 'read_file' ||
    normalizedName === 'write_file' ||
    normalizedName === 'edit_file' ||
    normalizedName === 'task'
  ) {
    return 'builtin';
  }
  // Builtin tools checked first as they have most specific exact-match patterns preventing false positives from substring matching

  // PRIORITY 2: Code execution tools (critical high-priority tool category for skills-first workflow)
  // runloop_execute_code is the correct tool name from RunLoopExecutor per corrected architecture
  if (
    normalizedName.includes('runloop_execute_code') ||
    normalizedName.includes('runloop') ||
    normalizedName.includes('execute_code') ||
    normalizedName.includes('python_repl') // backward compatibility
  ) {
    return 'code';
  }
  // Code execution checked second as it's critical high-priority tool category for skills-first workflow
  // runloop_execute_code is the correct tool name from RunLoopExecutor per corrected architecture

  // PRIORITY 3: Gmail tools (LangChain toolkit patterns)
  // Gmail patterns match official LangChain toolkit tool names from langchain_google_community package
  // Reference: https://python.langchain.com/docs/integrations/tools/google_gmail
  // The 5 official tool names: create_gmail_draft, send_gmail_message, search_gmail, get_gmail_message, get_gmail_thread
  if (
    normalizedName.includes('create_gmail_draft') ||
    normalizedName.includes('send_gmail_message') ||
    normalizedName.includes('search_gmail') ||
    normalizedName.includes('get_gmail_message') ||
    normalizedName.includes('get_gmail_thread') ||
    normalizedName.includes('gmail') ||
    normalizedName.includes('email')
  ) {
    return 'gmail';
  }
  // Gmail patterns match official LangChain toolkit tool names from langchain_google_community package
  // Reference: https://python.langchain.com/docs/integrations/tools/google_gmail
  // The 5 official tool names: create_gmail_draft, send_gmail_message, search_gmail, get_gmail_message, get_gmail_thread

  // PRIORITY 4: Calendar tools (LangChain toolkit patterns)
  // Calendar patterns match official LangChain toolkit tool names from langchain_google_community package
  // Reference: https://python.langchain.com/docs/integrations/tools/google_calendar
  // The 7 official tool names: create_calendar_event, search_calendar_events, update_calendar_event, get_calendars_info, move_calendar_event, delete_calendar_event, get_current_datetime
  if (
    normalizedName.includes('create_calendar_event') ||
    normalizedName.includes('search_calendar_events') ||
    normalizedName.includes('update_calendar_event') ||
    normalizedName.includes('get_calendars_info') ||
    normalizedName.includes('move_calendar_event') ||
    normalizedName.includes('delete_calendar_event') ||
    normalizedName.includes('get_current_datetime') ||
    normalizedName.includes('calendar') ||
    normalizedName.includes('event') ||
    normalizedName.includes('schedule')
  ) {
    return 'calendar';
  }
  // Calendar patterns match official LangChain toolkit tool names from langchain_google_community package
  // Reference: https://python.langchain.com/docs/integrations/tools/google_calendar
  // The 7 official tool names: create_calendar_event, search_calendar_events, update_calendar_event, get_calendars_info, move_calendar_event, delete_calendar_event, get_current_datetime

  // PRIORITY 5: Supabase MCP tools (reordered to fifth for specificity)
  // Supabase patterns match MCP server tools from corrected package at @supabase/mcp-server-postgrest
  // Specific tool names determined by MCP server implementation not documented in this plan
  if (
    normalizedName.includes('supabase') ||
    normalizedName.includes('query') ||
    normalizedName.includes('insert') ||
    normalizedName.includes('update') ||
    normalizedName.includes('delete') ||
    normalizedName.includes('storage')
  ) {
    return 'supabase';
  }
  // Supabase patterns match MCP server tools from corrected package at @supabase/mcp-server-postgrest
  // Specific tool names determined by MCP server implementation not documented in this plan

  // PRIORITY 6: Tavily MCP tools (reordered to sixth for specificity)
  // Tavily patterns match MCP server tools from corrected package at @mcptools/mcp-tavily
  // Specific tool names determined by MCP server implementation not documented in this plan
  if (
    normalizedName.includes('tavily') ||
    normalizedName.includes('search') ||
    normalizedName.includes('web_search')
  ) {
    return 'tavily';
  }
  // Tavily patterns match MCP server tools from corrected package at @mcptools/mcp-tavily
  // Specific tool names determined by MCP server implementation not documented in this plan

  // PRIORITY 7: Other (fallback for uncategorized tools)
  // Other category serves as safe fallback preventing runtime errors from uncategorized tools ensuring type safety
  return 'other';
}

/**
 * Icon mappings for each tool category
 * Used for visual identification in the UI
 */
export const CATEGORY_ICONS: Record<MCPCategory, string> = {
  supabase: '🗄️',
  tavily: '🔍',
  gmail: '📧',
  calendar: '📅',
  code: '⚡',
  builtin: '🛠️',
  other: '🔧',
};

/**
 * Color mappings for each tool category
 * Tailwind CSS classes for consistent badge styling
 */
export const CATEGORY_COLORS: Record<MCPCategory, string> = {
  supabase: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100',
  tavily: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100',
  gmail: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100',
  calendar: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100',
  code: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100',
  builtin: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-100',
  other: 'bg-zinc-100 text-zinc-800 dark:bg-zinc-900 dark:text-zinc-100',
};
