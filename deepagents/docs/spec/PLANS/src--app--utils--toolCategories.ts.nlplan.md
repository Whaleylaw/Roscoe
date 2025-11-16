# Natural Language Plan: src/app/utils/toolCategories.ts

## File Purpose

This file exists to provide utility functions and constants for categorizing agent tools by their MCP server source. It enables the UI to visually distinguish between different types of tools (database, search, email, calendar, code execution, built-in) through icons and color coding.

This file participates as a dependency for `src/app/components/ToolCallBox.tsx` which uses the categorization to display badges, and potentially `src/app/components/ChatInterface.tsx` for tool filtering functionality.

## Imports We Will Need (and Why)

This file has no imports as it is a pure TypeScript utility module exporting only types, constants, and pure functions with no external dependencies.

## Objects We Will Define

### Type: `MCPCategory`
**Purpose**: Define valid MCP server categories as TypeScript union type
**Values**: 'supabase' | 'tavily' | 'gmail' | 'calendar' | 'code' | 'builtin' | 'other'
**Side effects**: None (type definition only)

### Function: `getMCPCategory(toolName: string): MCPCategory`
**Purpose**: Determine which MCP category a tool belongs to based on its name
**Inputs**: `toolName` - The name of the tool (string)
**Outputs**: MCPCategory enum value (one of the 7 categories)
**Side effects**: None (pure function)

### Constant: `CATEGORY_ICONS`
**Purpose**: Map each category to its emoji icon for visual display
**Type**: `Record<MCPCategory, string>`
**Values**: Object mapping category names to emoji strings
**Side effects**: None (constant data)

### Constant: `CATEGORY_COLORS`
**Purpose**: Map each category to Tailwind CSS classes for badge styling
**Type**: `Record<MCPCategory, string>`
**Values**: Object mapping category names to Tailwind class strings
**Side effects**: None (constant data)

## Line-by-Line Natural Language Plan

[defines: MCPCategory @ src/app/utils/toolCategories.ts (planned lines 001-008)]
001: Export TypeScript type alias named MCPCategory as union type of seven string literals for all supported MCP server categories.

002: Include supabase as first union member representing database operations category for Supabase MCP server tools.

003: Include tavily as second union member representing web search category for Tavily MCP server tools.

004: Include gmail as third union member representing email operations category for Gmail MCP server tools.

005: Include calendar as fourth union member representing scheduling category for Google Calendar MCP server tools.

006: Include code as fifth union member representing Python code execution category for python underscore repl tool.

007: Include builtin as sixth union member representing DeepAgent middleware category for write underscore todos ls read underscore file write underscore file task tools.

008: Include other as seventh union member representing fallback category for any tools not matching above patterns.

[defines: getMCPCategory @ src/app/utils/toolCategories.ts (planned lines 009-060)]
009: Export function getMCPCategory accepting toolName parameter of type string and returning MCPCategory type.

010: Check if toolName includes substring supabase using string includes method to detect Supabase MCP tools.

011: Also check if toolName includes substring query as many database tools contain query in name.

012: Also check if toolName includes substring insert as database insert operations common pattern.

013: Also check if toolName includes substring update as database update operations common pattern.

014: Also check if toolName includes substring delete as database delete operations common pattern.

015: Also check if toolName includes substring storage as Supabase storage operations are database-related.

016: If any of above supabase-related checks pass then return string literal supabase as the category.

017: Check if toolName includes substring tavily using string includes method to detect Tavily MCP tools.

018: Also check if toolName includes substring search as Tavily is primarily a search tool.

019: Also check if toolName includes substring web underscore search as alternative naming pattern for search tools.

020: If any of above tavily-related checks pass then return string literal tavily as the category.

021: Check if toolName includes substring gmail using string includes method to detect Gmail MCP tools.

022: Also check if toolName includes substring email as generic email tool naming.

023: Also check if toolName includes substring send underscore message as common Gmail operation.

024: Also check if toolName includes substring read underscore message as common Gmail operation.

025: If any of above gmail-related checks pass then return string literal gmail as the category.

026: Check if toolName includes substring calendar using string includes method to detect Calendar MCP tools.

027: Also check if toolName includes substring event as calendar events are primary operation.

028: Also check if toolName includes substring schedule as alternative calendar naming.

029: If any of above calendar-related checks pass then return string literal calendar as the category.

030: Check if toolName includes substring python underscore repl to detect code execution tool.

031: Also check if toolName exactly equals PythonREPLTool as alternative naming from langchain-experimental package.

032: If either code execution check passes then return string literal code as the category.

033: Check if toolName exactly equals write underscore todos using strict equality to detect TodoListMiddleware tool.

034: Also check if toolName exactly equals ls for FilesystemMiddleware list directory tool.

035: Also check if toolName exactly equals read underscore file for FilesystemMiddleware read operation.

036: Also check if toolName exactly equals write underscore file for FilesystemMiddleware write operation.

037: Also check if toolName exactly equals edit underscore file for FilesystemMiddleware edit operation.

038: Also check if toolName exactly equals task for SubAgentMiddleware delegation tool.

039: If any of above builtin middleware checks pass then return string literal builtin as the category.

040: If none of above category checks matched then return string literal other as fallback category.

041: Add JSDoc comment above function explaining purpose parameters and return value with examples of tool names for each category.

042: Add inline comments within function explaining each category detection block for maintainability.

043: Note that function is case-sensitive and uses substring matching for flexibility in tool naming variations.

044: Document that order of checks matters as some patterns could match multiple categories.

045: Explain that more specific patterns like python underscore repl checked before generic patterns.

046: Add note that function is pure with no side effects making it suitable for memoization if performance needed.

047: Consider adding test cases in comment showing expected category for sample tool names.

048: Document that function designed to be extensible if new MCP servers added in future.

049: Add comment that exact equality checks for builtin tools prevent false positives from substring matching.

050: Note that supabase category checked first as it's most common in this application's use case.

051: Explain that other category serves as safe fallback preventing runtime errors from uncategorized tools.

052: Add example showing how function used in ToolCallBox component to determine badge display.

053: Document performance consideration that function called once per tool call render so must be fast.

054: Note that function does not validate toolName parameter allowing flexibility for new tools.

055: Explain that empty string or undefined toolName would fall through to other category safely.

056: Add comment that case sensitivity intentional as LangChain tool names follow camelCase or snake_case conventions.

057: Document that includes method used instead of regex for readability and performance.

058: Note that function could be enhanced with regex patterns if more complex matching needed.

059: Add comment explaining connection to backend MCP server configuration in src slash mcp slash clients dot py.

060: Conclude function with implicit return of other category as final fallback ensuring function always returns valid MCPCategory type.

[defines: CATEGORY_ICONS @ src/app/utils/toolCategories.ts (planned lines 061-070)]
061: Export constant object CATEGORY_ICONS with type annotation Record less than MCPCategory comma string greater than.

062: Define supabase property with value file cabinet emoji U+1F5C4 for database visual representation.

063: Define tavily property with value magnifying glass emoji U+1F50D for search visual representation.

064: Define gmail property with value envelope emoji U+1F4E7 for email visual representation.

065: Define calendar property with value calendar emoji U+1F4C5 for scheduling visual representation.

066: Define code property with value lightning bolt emoji U+26A1 for code execution visual representation indicating speed and power.

067: Define builtin property with value tools emoji U+1F6E0 for middleware tools visual representation.

068: Define other property with value wrench emoji U+1F527 for generic tools visual representation as fallback.

069: Add JSDoc comment explaining object maps categories to emoji icons for display in UI badges.

070: Add note that emojis chosen for visual clarity and universal recognition across platforms.

[defines: CATEGORY_COLORS @ src/app/utils/toolCategories.ts (planned lines 071-090)]
071: Export constant object CATEGORY_COLORS with type annotation Record less than MCPCategory comma string greater than.

072: Define supabase property with Tailwind classes bg-green-500 slash 10 text-green-700 border-green-300 for green database color scheme.

073: Define tavily property with Tailwind classes bg-blue-500 slash 10 text-blue-700 border-blue-300 for blue search color scheme.

074: Define gmail property with Tailwind classes bg-red-500 slash 10 text-red-700 border-red-300 for red email color scheme matching Gmail branding.

075: Define calendar property with Tailwind classes bg-purple-500 slash 10 text-purple-700 border-purple-300 for purple scheduling color scheme.

076: Define code property with Tailwind classes bg-orange-500 slash 10 text-orange-700 border-orange-300 for orange code execution color scheme indicating activity.

077: Define builtin property with Tailwind classes bg-gray-500 slash 10 text-gray-700 border-gray-300 for neutral gray middleware color scheme.

078: Define other property with Tailwind classes bg-zinc-500 slash 10 text-zinc-700 border-zinc-300 for zinc fallback color scheme.

079: Add JSDoc comment explaining object maps categories to Tailwind CSS classes for badge styling.

080: Note that color scheme uses 10% opacity backgrounds for subtle visual distinction without overwhelming UI.

081: Explain that text colors use 700 shade for readability against light backgrounds.

082: Document that border colors use 300 shade for subtle borders matching badge design system.

083: Add comment that colors chosen for accessibility with sufficient contrast ratios.

084: Note that color choices align with common UI conventions database green search blue email red calendar purple.

085: Explain that code execution orange chosen to stand out as unique and important operation.

086: Document that builtin gray intentionally neutral to distinguish from MCP server categories.

087: Add comment that Tailwind classes assume project configured with standard Tailwind color palette.

088: Note that classes can be easily customized by modifying this constant without changing component code.

089: Explain that slash 10 syntax is Tailwind opacity modifier for transparent backgrounds.

090: Add comment that color system extensible if new MCP servers require additional categories.

## Cross-References

No cross-references to other files in this plan as this is a pure utility module with no imports.

[defines: MCPCategory @ src/app/utils/toolCategories.ts (planned lines 001-008)]
[defines: getMCPCategory @ src/app/utils/toolCategories.ts (planned lines 009-060)]
[defines: CATEGORY_ICONS @ src/app/utils/toolCategories.ts (planned lines 061-070)]
[defines: CATEGORY_COLORS @ src/app/utils/toolCategories.ts (planned lines 071-090)]

## Notes & Assumptions

- Assumes Tailwind CSS is configured in project with standard color palette
- Tool name patterns based on current MCP server naming conventions from langchain-mcp-adapters
- Function designed for client-side only, no server-side rendering considerations
- Emojis assumed to render consistently across browsers (all modern browsers support Unicode emojis)
- Color accessibility not rigorously tested but follows general best practices
- No internationalization needed as emojis are universal and colors are visual only
- Function could be memoized for performance but likely unnecessary given simplicity
- Type safety ensures all categories covered in icon and color maps at compile time
- Order of checks in getMCPCategory important - more specific patterns before general ones
- File has zero runtime dependencies making it highly portable and testable
