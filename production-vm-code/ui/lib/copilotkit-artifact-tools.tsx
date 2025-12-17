"use client";

import { useMemo } from "react";
import { useCopilotAction } from "@copilotkit/react-core";
import { artifactRegistry } from "@/components/artifacts/registry";

/**
 * CopilotKit tools that allow the agent to create, update, and remove artifacts
 * Connects the agent's capabilities to the artifact canvas
 */
export function useCopilotArtifactTools() {
  // Register all artifact components as CopilotKit actions
  const components = useMemo(() => artifactRegistry.list(), []);

  // Create artifact tool
  useCopilotAction({
    name: "create_artifact",
    description: "Create a new UI artifact (contact card, medical provider, insurance card, etc) and display it to the user",
    parameters: [
      {
        name: "componentId",
        type: "string",
        description: `Type of artifact to create. Options: ${components.map((c) => c.id).join(", ")}`,
        required: true,
      },
      {
        name: "data",
        type: "object",
        description: "Data for the artifact component",
        required: true,
      },
    ],
    handler: async ({ componentId, data }) => {
      const canvas = (window as any).__artifactCanvas;
      if (!canvas) {
        throw new Error("Artifact canvas not mounted");
      }

      const component = artifactRegistry.get(componentId);
      if (!component) {
        throw new Error(`Unknown component: ${componentId}. Available components: ${components.map((c) => c.id).join(", ")}`);
      }

      // Validate data against schema
      try {
        component.schema.parse(data);
      } catch (error: any) {
        throw new Error(`Invalid data for ${componentId}: ${error.message}`);
      }

      const artifactId = canvas.add(componentId, data);
      return {
        success: true,
        artifactId,
        message: `Created ${component.name} artifact`,
      };
    },
  });

  // Update artifact tool
  useCopilotAction({
    name: "update_artifact",
    description: "Update an existing artifact with new data",
    parameters: [
      {
        name: "artifactId",
        type: "string",
        description: "ID of the artifact to update",
        required: true,
      },
      {
        name: "data",
        type: "object",
        description: "New data for the artifact",
        required: true,
      },
    ],
    handler: async ({ artifactId, data }) => {
      const canvas = (window as any).__artifactCanvas;
      if (!canvas) {
        throw new Error("Artifact canvas not mounted");
      }

      canvas.update(artifactId, data);
      return {
        success: true,
        message: `Updated artifact ${artifactId}`,
      };
    },
  });

  // Remove artifact tool
  useCopilotAction({
    name: "remove_artifact",
    description: "Remove an artifact from the canvas",
    parameters: [
      {
        name: "artifactId",
        type: "string",
        description: "ID of the artifact to remove",
        required: true,
      },
    ],
    handler: async ({ artifactId }) => {
      const canvas = (window as any).__artifactCanvas;
      if (!canvas) {
        throw new Error("Artifact canvas not mounted");
      }

      canvas.remove(artifactId);
      return {
        success: true,
        message: `Removed artifact ${artifactId}`,
      };
    },
  });

  // List available artifact types tool
  useCopilotAction({
    name: "list_artifact_types",
    description: "Get a list of all available artifact component types you can create",
    parameters: [],
    handler: async () => {
      const list = artifactRegistry.list();
      return {
        success: true,
        artifacts: list.map((c) => ({
          id: c.id,
          name: c.name,
          description: c.description,
          category: c.category,
        })),
      };
    },
  });
}
