"use client";

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

// Define variant-based styling using CVA (class-variance-authority)
// bg-green-500 in success variant specifically chosen for "skill execution" badge per architecture requirements
// Hover states provide visual feedback for interactive badges though most badges are static displays
// Additional variants can be added here without breaking existing usage following open-closed principle
const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
        success:
          "border-transparent bg-green-500 text-white shadow hover:bg-green-600",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
        outline: "text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

/**
 * Badge component accepts variant prop for styling and all standard HTML div attributes
 * @example
 * <Badge variant="success">Skill Name</Badge>
 *
 * Note: variant defaults to "default" per cva configuration and className can override or extend variant styles
 */
export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  // No additional explicit props needed beyond variants and standard HTML attributes keeping component simple
}

/**
 * Renders a badge with variant-based styling following shadcn UI patterns
 * Badge supports all standard HTML div attributes for flexibility in usage contexts
 * Badge is pure presentation component with no internal state or side effects making it easy to test
 * cn utility handles Tailwind class conflicts so className prop can safely override variant styles when needed
 */
function Badge({
  className,
  variant,
  ...props
}: BadgeProps): React.JSX.Element {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

// Export Badge function using named export to follow shadcn UI convention for better tree-shaking
// Exporting badgeVariants allows external composition but most consumers should just use Badge component directly
export { Badge, badgeVariants };
