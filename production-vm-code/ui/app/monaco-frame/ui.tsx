"use client";

import { useEffect, useMemo, useState } from "react";
import Editor from "@monaco-editor/react";
import {
  AssistantFrameProvider,
  ModelContextRegistry,
} from "@assistant-ui/react";
import type { JSONSchema7 } from "json-schema";

type OpenDocumentArgs = { path: string };
type OpenDocumentResult = { ok: true; path: string; bytes: number };

type SetDocumentArgs = { text: string };
type SetDocumentResult = { ok: true };

type GetDocumentArgs = Record<string, never>;
type GetDocumentResult = { ok: true; path: string | null; text: string };

const pathSchema: JSONSchema7 = {
  type: "object",
  additionalProperties: false,
  required: ["path"],
  properties: {
    path: { type: "string" },
  },
};

const setDocSchema: JSONSchema7 = {
  type: "object",
  additionalProperties: false,
  required: ["text"],
  properties: {
    text: { type: "string" },
  },
};

const emptySchema: JSONSchema7 = {
  type: "object",
  additionalProperties: false,
  properties: {},
};

export function MonacoFrameClient() {
  const [currentPath, setCurrentPath] = useState<string | null>(null);
  const [value, setValue] = useState<string>("");

  const registry = useMemo(() => new ModelContextRegistry(), []);

  useEffect(() => {
    // Allow the parent workbench to control Monaco via postMessage (e.g., "Open in Monaco" button).
    const onMessage = async (ev: MessageEvent) => {
      const data = ev.data as any;
      if (!data || typeof data !== "object") return;
      if (data.type === "monaco.openDocument" && typeof data.path === "string") {
        const path = data.path;
        const url = `/api/workspace/file?path=${encodeURIComponent(path)}`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) return;
        const text = await res.text();
        setCurrentPath(path);
        setValue(text);
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  useEffect(() => {
    // Register tools exposed to the parent assistant.
    registry.addTool<OpenDocumentArgs, OpenDocumentResult>({
      toolName: "openDocument",
      description: "Open a workspace file for editing in Monaco",
      parameters: pathSchema,
      execute: async ({ path }) => {
        const url = `/api/workspace/file?path=${encodeURIComponent(path)}`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) {
          throw new Error(`Failed to open document (${res.status})`);
        }
        const text = await res.text();
        setCurrentPath(path);
        setValue(text);
        return { ok: true, path, bytes: text.length };
      },
    });

    registry.addTool<SetDocumentArgs, SetDocumentResult>({
      toolName: "setDocument",
      description: "Replace the current Monaco buffer with provided text",
      parameters: setDocSchema,
      execute: async ({ text }) => {
        setValue(text);
        return { ok: true };
      },
    });

    registry.addTool<GetDocumentArgs, GetDocumentResult>({
      toolName: "getDocument",
      description: "Get the current Monaco buffer text (and path, if any)",
      parameters: emptySchema,
      execute: async () => {
        return { ok: true, path: currentPath, text: value };
      },
    });

    const unsubscribe = AssistantFrameProvider.addModelContextProvider(registry);
    return () => unsubscribe();
  }, [registry, currentPath, value]);

  return (
    <div className="flex h-full flex-col">
      <div className="border-b px-3 py-2 text-sm">
        <span className="font-semibold">Monaco</span>
        <span className="ml-2 text-muted-foreground">
          {currentPath ?? "(no document loaded)"}
        </span>
      </div>
      <div className="min-h-0 flex-1">
        <Editor
          height="100%"
          defaultLanguage="markdown"
          value={value}
          onChange={(v) => setValue(v ?? "")}
          options={{
            minimap: { enabled: false },
            wordWrap: "on",
            fontSize: 14,
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </div>
  );
}

