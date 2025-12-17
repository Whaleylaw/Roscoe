"use client";

import { useCopilotAction } from "@copilotkit/react-core";
import { useWorkbenchStore } from "@/lib/workbench-store";

/**
 * Workspace tools for CopilotKit (file browser, document viewer)
 * Migrated from assistant-ui WorkbenchContextTools
 *
 * Provides 6 actions for interacting with the workspace:
 * 1. get_active_viewer - Get currently viewed file path
 * 2. get_file_browser_path - Get current folder in browser
 * 3. workspace_get_file_url - Get URL for a workspace file
 * 4. workspace_list - List files/folders in directory
 * 5. workspace_read_text - Read text file from workspace
 * 6. get_viewer_text - Get text from currently viewed file
 */
export function useCopilotWorkspaceTools() {
  const selectedPath = useWorkbenchStore((s) => s.selectedPath);
  const browserPath = useWorkbenchStore((s) => s.browserPath);

  useCopilotAction({
    name: "get_active_viewer",
    description: "Get the currently viewed file path in the document viewer (if any)",
    parameters: [],
    handler: async () => {
      return { ok: true, path: selectedPath };
    },
  });

  useCopilotAction({
    name: "get_file_browser_path",
    description: "Get the current folder being shown in the file browser",
    parameters: [],
    handler: async () => {
      return { ok: true, path: browserPath };
    },
  });

  useCopilotAction({
    name: "workspace_get_file_url",
    description: "Get a URL the user can open/download for a workspace file",
    parameters: [
      {
        name: "path",
        type: "string",
        description: "File path in workspace",
        required: true,
      },
    ],
    handler: async ({ path }) => {
      // Validate path parameter
      if (!path || typeof path !== "string") {
        throw new Error("Invalid path parameter - must be a non-empty string");
      }

      const url = new URL(
        `/api/workspace/file?path=${encodeURIComponent(path)}`,
        window.location.href
      ).href;

      return { ok: true, path, url };
    },
  });

  useCopilotAction({
    name: "workspace_list",
    description: "List files/folders in a workspace directory",
    parameters: [
      {
        name: "path",
        type: "string",
        description: "Directory path to list",
        required: true,
      },
    ],
    handler: async ({ path }) => {
      // Validate path parameter
      if (!path || typeof path !== "string") {
        throw new Error("Invalid path parameter - must be a non-empty string");
      }

      try {
        const res = await fetch(
          `/api/workspace/list?path=${encodeURIComponent(path)}`,
          { cache: "no-store" }
        );

        const data = await res.json();

        if (!res.ok || !data?.ok) {
          throw new Error(data?.error || `Failed to list directory (${res.status})`);
        }

        return { ok: true, path: data.path, entries: data.entries };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        throw new Error(`Failed to list directory: ${errorMessage}`);
      }
    },
  });

  useCopilotAction({
    name: "workspace_read_text",
    description: "Read a text file from the workspace (.md/.txt/.json/.csv/.log)",
    parameters: [
      {
        name: "path",
        type: "string",
        description: "File path to read",
        required: true,
      },
      {
        name: "maxBytes",
        type: "number",
        description: "Maximum bytes to read (1-200000)",
      },
    ],
    handler: async ({ path, maxBytes }) => {
      // Validate path parameter
      if (!path || typeof path !== "string") {
        throw new Error("Invalid path parameter - must be a non-empty string");
      }

      // Validate and clamp maxBytes
      const limit = maxBytes
        ? Math.max(1, Math.min(200000, maxBytes))
        : 20000;

      try {
        const url = `/api/workspace/file?path=${encodeURIComponent(path)}`;
        const res = await fetch(url, { cache: "no-store" });

        if (!res.ok) {
          throw new Error(`Failed to read file (${res.status})`);
        }

        const contentType = res.headers.get("content-type") || "application/octet-stream";
        const text = await res.text();
        const truncated = text.length > limit;

        return {
          ok: true,
          path,
          contentType,
          text: truncated ? text.slice(0, limit) : text,
          truncated,
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        throw new Error(`Failed to read file: ${errorMessage}`);
      }
    },
  });

  useCopilotAction({
    name: "get_viewer_text",
    description: "If the viewer is showing a text file, return its text (possibly truncated)",
    parameters: [
      {
        name: "maxBytes",
        type: "number",
        description: "Maximum bytes to read (1-200000)",
      },
    ],
    handler: async ({ maxBytes }) => {
      if (!selectedPath) {
        return { ok: true, path: null, text: null, truncated: false };
      }

      // Validate and clamp maxBytes
      const limit = maxBytes
        ? Math.max(1, Math.min(200000, maxBytes))
        : 20000;

      try {
        const url = `/api/workspace/file?path=${encodeURIComponent(selectedPath)}`;
        const res = await fetch(url, { cache: "no-store" });

        if (!res.ok) {
          throw new Error(`Failed to read viewer file (${res.status})`);
        }

        const text = await res.text();
        const truncated = text.length > limit;

        return {
          ok: true,
          path: selectedPath,
          text: truncated ? text.slice(0, limit) : text,
          truncated,
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : "Unknown error";
        throw new Error(`Failed to read viewer file: ${errorMessage}`);
      }
    },
  });
}
