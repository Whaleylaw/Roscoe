# Natural Language Plan: src/components/ui/badge.tsx

**Status**: Planning Phase - No code written yet
**Purpose**: Create Badge UI component for skill execution indicators
**Approval Required**: "Approves, spec"

---

## File Purpose

This file creates a reusable Badge component following shadcn/ui patterns for displaying labels, tags, and indicators throughout the UI. The component supports multiple variants including a "success" variant specifically needed by CodeExecutionBox to highlight skill execution with token savings.

This file participates as a foundational UI component used by CodeExecutionBox and potentially other components in the future.

---

## Imports We Will Need (and Why)

001: Import React namespace and all exports from react package to enable TypeScript JSX and component definition for this client component.

002: Import cva function and VariantProps type from class-variance-authority package to define variant-based styling with type safety per shadcn UI pattern.

003: Import cn utility function from at slash lib slash utils to conditionally merge Tailwind className strings with conflict resolution [uses: cn @ src/lib/utils.ts (existing)].

---

## Objects We Will Define

### Constant: `badgeVariants`
**Purpose**: Define variant-based styling using CVA (class-variance-authority)
**Type**: CVA function returning className string
**Variants**: default, success, destructive, outline
**Side effects**: None (pure function)

### Interface: `BadgeProps`
**Purpose**: TypeScript props interface for Badge component
**Extends**: React.HTMLAttributes<HTMLDivElement> and VariantProps<typeof badgeVariants>
**Properties**: variant (optional), className (optional), children, ...other HTML div props
**Side effects**: None (type definition)

### Component: `Badge`
**Purpose**: Render badge with variant styling
**Inputs**: BadgeProps (variant, className, children, ...props)
**Outputs**: JSX.Element (div with styled content)
**Side effects**: None (pure presentation)

---

## Line-by-Line Natural Language Plan

[defines: imports @ src/components/ui/badge.tsx (planned lines 001-003)]

001: Add use client directive at top of file to mark this as a React Client Component for Next dot js App Router since badge may be used in interactive contexts.

002: Import asterisk as React from react package to get React namespace for TypeScript JSX transform and component type definitions.

003: Import cva function and VariantProps type from class-variance-authority package to create variant-based component styling following shadcn UI pattern.

004: Import cn utility function from at slash lib slash utils to merge className prop with variant classes handling Tailwind conflicts [uses: cn @ src/lib/utils.ts (existing)].

[defines: badgeVariants @ src/components/ui/badge.tsx (planned lines 005-020)]

005: Define constant badgeVariants using cva function call to create variant-aware className generator for the badge component following shadcn pattern.

006: Pass base className string as first argument to cva containing common styles: inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors.

007: Add focus styles to base: focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 for keyboard accessibility per shadcn standards.

008: Pass variants configuration object as second argument to cva to define different badge appearances for various use cases.

009: Inside variants object define variant property with object containing default success destructive and outline as keys for different badge types.

010: Define default variant value: border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80 for general purpose badges.

011: Define success variant value: border-transparent bg-green-500 text-white shadow hover:bg-green-600 for skill execution indicators per CodeExecutionBox requirements.

012: Define destructive variant value: border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80 for error or warning badges.

013: Define outline variant value: text-foreground for subtle bordered badges without background fill maintaining text color only.

014: Close variants object and continue to default variants configuration object to set default values when no variant prop provided.

015: In defaultVariants object set variant property to default string literal so badges render with primary styling when variant not specified.

016: Close cva function call and assign result to badgeVariants constant making it available for Badge component className generation.

017: Add TypeScript type annotation to badgeVariants as ReturnType of cva for proper type inference in component props.

018: Add inline comment explaining that bg-green-500 in success variant specifically chosen for "skill execution" badge per architecture requirements.

019: Add inline comment noting that hover states provide visual feedback for interactive badges though most badges are static displays.

020: Add inline comment that additional variants can be added here without breaking existing usage following open-closed principle.

[defines: BadgeProps @ src/components/ui/badge.tsx (planned lines 021-028)]

021: Export TypeScript interface named BadgeProps to define props contract for Badge component with type safety for consumers.

022: Extend interface from React dot HTMLAttributes generic with HTMLDivElement as type parameter to inherit all standard div attributes like onClick className id.

023: Also extend from VariantProps generic with typeof badgeVariants as type parameter to automatically infer variant prop type from cva definition.

024: Add JSDoc comment above interface explaining Badge component accepts variant prop for styling and all standard HTML div attributes.

025: Add JSDoc example showing typical usage: Badge variant equals success children equals skill name end Badge tag.

026: Note in JSDoc that variant defaults to default per cva configuration and className can override or extend variant styles.

027: Add inline comment that no additional explicit props needed beyond variants and standard HTML attributes keeping component simple.

028: Close BadgeProps interface definition making it available for Badge function parameter typing.

[defines: Badge @ src/components/ui/badge.tsx (planned lines 029-045)]

029: Define function named Badge accepting props parameter with BadgeProps type to create the main component function following React functional component pattern.

030: Destructure className and variant from props using object destructuring to extract these specific props for special handling.

031: Also capture ...props using rest operator to collect all remaining props for spreading onto the rendered div element.

032: Inside Badge function body call badgeVariants function passing object with variant property to get computed className string based on variant selection.

033: Call cn utility function passing badgeVariants result as first argument and className prop as second to merge variant classes with any custom className.

034: Assign merged className string to constant named computedClassName for use in JSX return statement.

035: Return JSX expression starting with div element as container for badge content following semantic HTML structure.

036: Spread ...props onto div using JSX spread syntax to pass through all HTML attributes like onClick aria-label data-testid et cetera.

037: Set className prop on div to computedClassName to apply the merged variant and custom classes for proper styling.

038: Place {children} expression inside div to render whatever content is passed between Badge opening and closing tags.

039: Close div element and Badge function returning the complete JSX structure.

040: Add TypeScript return type annotation React dot JSX dot Element to Badge function signature for explicit typing.

041: Add JSDoc comment above Badge function explaining it renders a badge with variant-based styling following shadcn UI patterns.

042: Note in JSDoc that Badge supports all standard HTML div attributes for flexibility in usage contexts.

043: Add inline comment that Badge is pure presentation component with no internal state or side effects making it easy to test.

044: Add inline comment that cn utility handles Tailwind class conflicts so className prop can safely override variant styles when needed.

045: Export Badge function as default or named export depending on project conventions making it available for import by CodeExecutionBox and other components.

[defines: exports @ src/components/ui/badge.tsx (planned lines 046-050)]

046: Export Badge function using named export to follow shadcn UI convention of named exports for better tree-shaking.

047: Also export badgeVariants constant to allow consumers to reference variant className strings if needed for advanced styling use cases.

048: Add comment explaining that exporting badgeVariants allows external composition but most consumers should just use Badge component directly.

049: Add export statement for BadgeProps interface to enable TypeScript consumers to import the type for prop validation or wrapper components.

050: Close file with empty line per ESLint and Prettier formatting standards ensuring clean file termination.

---

## Cross-References

**Imports:**
- [uses: cn @ src/lib/utils.ts (existing)]
- [uses: cva @ class-variance-authority (external package v0.7.1)]
- [uses: React @ react (external package v19.1.0)]

**Exports:**
- [defines: Badge @ src/components/ui/badge.tsx (planned lines 029-045)]
- [defines: BadgeProps @ src/components/ui/badge.tsx (planned lines 021-028)]
- [defines: badgeVariants @ src/components/ui/badge.tsx (planned lines 005-020)]

**Used by:**
- [used_by: CodeExecutionBox @ src/app/components/CodeExecutionBox.tsx (planned line import)]

---

## Notes & Assumptions

- **shadcn/ui pattern**: Follows exact pattern from shadcn/ui badge component for consistency with existing UI components in project
- **variant="success"**: Specifically required by CodeExecutionBox for skill execution indicator with green styling
- **Tailwind classes**: Uses project's Tailwind configuration; assumes standard shadcn/ui color tokens (primary, destructive, etc.) are defined
- **Accessibility**: Includes focus ring styles for keyboard navigation; consumers should add aria-label when badge meaning isn't obvious
- **No icon support**: Simple text-only badge; icons can be passed as children if needed
- **Responsive**: Inline-flex ensures badge adapts to content size; responsive sizing can be controlled via className prop
- **No animation**: Static display; hover transitions only; more complex animations should be handled by parent component
- **File size**: Approximately 50 lines of formatted TypeScript code
- **Testing**: Component should have unit tests verifying all variants render correct classes
- **Future enhancements**: Could add size variants (sm, md, lg) if needed without breaking existing usage

---

## Validation

- [x] All imports resolve to existing or planned files
- [x] Component follows React best practices (functional component, props interface)
- [x] Follows shadcn/ui patterns for consistency
- [x] TypeScript types are complete and accurate
- [x] Variant system is extensible
- [x] Accessibility considerations included (focus states)
- [x] No external state or side effects (pure component)
- [x] Cross-references documented
- [x] Used by CodeExecutionBox per architecture requirement

**Citations:**
- **shadcn/ui Badge**: https://ui.shadcn.com/docs/components/badge
- **class-variance-authority**: https://cva.style/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
