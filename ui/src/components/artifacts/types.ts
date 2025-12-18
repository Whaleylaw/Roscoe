import { ComponentType } from "react";

/**
 * Base type for all artifact components
 * Artifacts are dynamic UI components that can be rendered by the agent
 */
export interface ArtifactComponent<TProps = any> {
  /** Unique identifier for this component type */
  id: string;
  /** Display name */
  name: string;
  /** Description for the agent */
  description: string;
  /** The React component */
  component: ComponentType<TProps>;
  /** Zod schema for props validation */
  schema: any; // Will be Zod schema
  /** Category for organization */
  category: "contact" | "medical" | "insurance" | "legal" | "document" | "ui";
}

/**
 * Props passed to all artifact components
 */
export interface ArtifactProps {
  /** Unique ID for this artifact instance */
  artifactId: string;
  /** User-provided or agent-generated data */
  data: Record<string, any>;
  /** Callback when artifact requests an action */
  onAction?: (action: string, payload: any) => void;
}
