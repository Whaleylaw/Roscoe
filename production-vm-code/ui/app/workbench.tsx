"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  AssistantRuntimeProvider,
  AssistantFrameHost,
  ModelContextRegistry,
  useAssistantRuntime,
} from "@assistant-ui/react";
import { useLangGraphRuntime } from "@assistant-ui/react-langgraph";
import type { JSONSchema7 } from "json-schema";

import { createThread, getThreadState, sendMessage } from "@/lib/chatApi";
import { Thread } from "@/components/assistant-ui/thread";
import { FileBrowser } from "@/components/workbench/file-browser";
import { DocumentViewer } from "@/components/workbench/document-viewer";
import { Button } from "@/components/ui/button";
import { useWorkbenchStore } from "@/lib/workbench-store";

function FrameHost({ iframe }: { iframe: HTMLIFrameElement | null }) {
  const runtime = useAssistantRuntime();

  useEffect(() => {
    if (!iframe?.contentWindow) return;
    const host = new AssistantFrameHost(iframe.contentWindow);
    const unsubscribe = runtime.registerModelContextProvider(host);
    return () => {
      unsubscribe?.();
      host.dispose();
    };
  }, [iframe, runtime]);

  return null;
}

const THREAD_STORAGE_KEY = "roscoe.langgraph.thread_id";
const getStoredThreadId = () => {
  try {
    return window.localStorage.getItem(THREAD_STORAGE_KEY);
  } catch {
    return null;
  }
};
const setStoredThreadId = (id: string) => {
  try {
    window.localStorage.setItem(THREAD_STORAGE_KEY, id);
  } catch {
    // ignore
  }
};

function WorkbenchContextTools() {
  const runtime = useAssistantRuntime();
  const selectedPath = useWorkbenchStore((s) => s.selectedPath);
  const browserPath = useWorkbenchStore((s) => s.browserPath);

  const selectedPathRef = useRef<string | null>(null);
  const browserPathRef = useRef<string>("/projects");

  useEffect(() => {
    selectedPathRef.current = selectedPath;
  }, [selectedPath]);

  useEffect(() => {
    browserPathRef.current = browserPath;
  }, [browserPath]);

  const registry = useMemo(() => new ModelContextRegistry(), []);

  useEffect(() => {
    const emptySchema: JSONSchema7 = {
      type: "object",
      additionalProperties: false,
      properties: {},
    };

    const pathSchema: JSONSchema7 = {
      type: "object",
      additionalProperties: false,
      required: ["path"],
      properties: {
        path: { type: "string" },
      },
    };

    const readTextSchema: JSONSchema7 = {
      type: "object",
      additionalProperties: false,
      required: ["path"],
      properties: {
        path: { type: "string" },
        maxBytes: { type: "number", minimum: 1, maximum: 200000 },
      },
    };

    const viewerTextSchema: JSONSchema7 = {
      type: "object",
      additionalProperties: false,
      properties: {
        maxBytes: { type: "number", minimum: 1, maximum: 200000 },
      },
    };

    registry.addTool<Record<string, never>, { ok: true; path: string | null }>({
      toolName: "workbench.getActiveViewer",
      description: "Get the currently viewed file path in the document viewer (if any).",
      parameters: emptySchema,
      execute: async () => ({ ok: true, path: selectedPathRef.current }),
    });

    registry.addTool<Record<string, never>, { ok: true; path: string }>({
      toolName: "workbench.getFileBrowserPath",
      description: "Get the current folder being shown in the file browser.",
      parameters: emptySchema,
      execute: async () => ({ ok: true, path: browserPathRef.current }),
    });

    registry.addTool<
      { path: string },
      { ok: true; url: string; path: string }
    >({
      toolName: "workspace.getFileUrl",
      description:
        "Get a URL the user can open/download for a workspace file (served by the UI).",
      parameters: pathSchema,
      execute: async ({ path }) => ({
        ok: true,
        path,
        url: new URL(`/api/workspace/file?path=${encodeURIComponent(path)}`, window.location.href).href,
      }),
    });

    registry.addTool<
      { path: string },
      { ok: true; path: string; entries: unknown }
    >({
      toolName: "workspace.list",
      description: "List files/folders in a workspace directory.",
      parameters: pathSchema,
      execute: async ({ path }) => {
        const res = await fetch(
          `/api/workspace/list?path=${encodeURIComponent(path)}`,
          { cache: "no-store" },
        );
        const data = await res.json();
        if (!res.ok || !data?.ok) {
          throw new Error(data?.error || `Failed to list directory (${res.status})`);
        }
        return { ok: true, path: data.path, entries: data.entries };
      },
    });

    registry.addTool<
      { path: string; maxBytes?: number },
      { ok: true; path: string; contentType: string; text: string; truncated: boolean }
    >({
      toolName: "workspace.readText",
      description:
        "Read a text file from the workspace (best-effort). Use for .md/.txt/.json/.csv/.log. Returns truncated text if large.",
      parameters: readTextSchema,
      execute: async ({ path, maxBytes }) => {
        const url = `/api/workspace/file?path=${encodeURIComponent(path)}`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error(`Failed to read file (${res.status})`);
        const contentType = res.headers.get("content-type") || "application/octet-stream";
        const t = await res.text();
        const limit = Math.max(1, Math.min(200000, maxBytes ?? 20000));
        const truncated = t.length > limit;
        return {
          ok: true,
          path,
          contentType,
          text: truncated ? t.slice(0, limit) : t,
          truncated,
        };
      },
    });

    registry.addTool<
      { maxBytes?: number },
      { ok: true; path: string | null; text: string | null; truncated: boolean }
    >({
      toolName: "workbench.getViewerText",
      description:
        "If the viewer is showing a text file, return its text (possibly truncated).",
      parameters: viewerTextSchema,
      execute: async ({ maxBytes }) => {
        const path = selectedPathRef.current;
        if (!path) return { ok: true, path: null, text: null, truncated: false };
        const url = `/api/workspace/file?path=${encodeURIComponent(path)}`;
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) throw new Error(`Failed to read viewer file (${res.status})`);
        const t = await res.text();
        const limit = Math.max(1, Math.min(200000, maxBytes ?? 20000));
        const truncated = t.length > limit;
        return {
          ok: true,
          path,
          text: truncated ? t.slice(0, limit) : t,
          truncated,
        };
      },
    });

    const unsubscribe = runtime.registerModelContextProvider(registry);
    return () => {
      unsubscribe?.();
    };
  }, [registry, runtime]);

  return null;
}

export function Workbench() {
  const runtime = useLangGraphRuntime({
    stream: async function* (messages, { initialize, command }) {
      const { externalId } = await initialize();
      // Assistant UI's built-in thread list selection can be absent depending on runtime config.
      // When `externalId` is missing, we fall back to a locally persisted LangGraph thread_id.
      // This ensures all turns are sent to the same LangGraph thread (and history is preserved),
      // instead of creating "temporary" threadless runs.
      let threadId = externalId ?? getStoredThreadId();
      if (!threadId) {
        const { thread_id } = await createThread();
        threadId = thread_id;
      }
      setStoredThreadId(threadId);

      const generator = await sendMessage({
        threadId,
        messages,
        command,
      });

      yield* generator;
    },
    create: async () => {
      const { thread_id } = await createThread();
      return { externalId: thread_id };
    },
    load: async (externalId) => {
      try {
        const state = await getThreadState(externalId);
        const interrupts =
          state.tasks?.flatMap((t) => t.interrupts ?? [])?.filter(Boolean) ?? [];
        return {
          messages: state.values.messages,
          interrupts: interrupts.length ? interrupts : undefined,
        };
      } catch (err) {
        // If the browser has a stale thread id persisted locally, treat it as a new chat.
        // We'll let `sendMessage()` recreate the thread on first message via `if_not_exists: "create"`.
        return { messages: [] };
      }
    },
  });

  const centerView = useWorkbenchStore((s) => s.centerView);
  const setCenterView = useWorkbenchStore((s) => s.setCenterView);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  const [iframeEl, setIframeEl] = useState<HTMLIFrameElement | null>(null);
  const [calendarIframeEl, setCalendarIframeEl] =
    useState<HTMLIFrameElement | null>(null);

  const pendingMonacoOpenPath = useWorkbenchStore((s) => s.pendingMonacoOpenPath);
  const clearPendingMonacoOpen = useWorkbenchStore((s) => s.clearPendingMonacoOpen);
  const calendarEvents = useWorkbenchStore((s) => s.calendarEvents);

  // Keep the iframe mounted so its tools are always available, but only show it when selected.
  const iframeStyle = useMemo(() => {
    return centerView === "monaco" ? "block" : "hidden";
  }, [centerView]);

  const calendarStyle = useMemo(() => {
    return centerView === "calendar" ? "block" : "hidden";
  }, [centerView]);

  const viewerStyle = useMemo(() => {
    return centerView === "viewer" ? "block" : "hidden";
  }, [centerView]);

  // Bridge "Open in Monaco" requests into the Monaco iframe via postMessage.
  useEffect(() => {
    if (!pendingMonacoOpenPath) return;
    if (!iframeEl?.contentWindow) return;
    iframeEl.contentWindow.postMessage(
      { type: "monaco.openDocument", path: pendingMonacoOpenPath },
      "*",
    );
    clearPendingMonacoOpen();
  }, [pendingMonacoOpenPath, iframeEl, clearPendingMonacoOpen]);

  // Bridge calendar events into the Calendar iframe via postMessage.
  useEffect(() => {
    if (!calendarIframeEl?.contentWindow) return;
    if (!calendarEvents) return;
    calendarIframeEl.contentWindow.postMessage(
      { type: "calendar.setCalendarEvents", events: calendarEvents },
      "*",
    );
  }, [calendarEvents, calendarIframeEl]);

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      <WorkbenchContextTools />
      <div className="flex h-full min-w-0">
        <aside className="w-72 shrink-0 border-r bg-background">
          <FileBrowser />
        </aside>

        <section className="min-w-0 flex-1">
          <div className="flex items-center gap-2 border-b px-3 py-2">
            <Button
              size="sm"
              variant={centerView === "viewer" ? "default" : "outline"}
              onClick={() => setCenterView("viewer")}
            >
              Viewer
            </Button>
            <Button
              size="sm"
              variant={centerView === "monaco" ? "default" : "outline"}
              onClick={() => setCenterView("monaco")}
            >
              Monaco
            </Button>
            <Button
              size="sm"
              variant={centerView === "calendar" ? "default" : "outline"}
              onClick={() => setCenterView("calendar")}
            >
              Calendar
            </Button>
            <div className="flex-1" />
            <Button
              size="sm"
              variant="outline"
              onClick={() => setCenterView("monaco")}
              title="Open Monaco tool container"
            >
              Open editor
            </Button>
          </div>

          <div className={viewerStyle + " h-[calc(100vh-44px)]"}>
            <DocumentViewer />
          </div>

          <div className={iframeStyle + " h-[calc(100vh-44px)]"}>
            <iframe
              ref={(el) => {
                iframeRef.current = el;
                setIframeEl(el);
              }}
              src="/monaco-frame"
              className="h-full w-full"
              title="Monaco editor frame"
            />
          </div>

          <div className={calendarStyle + " h-[calc(100vh-44px)]"}>
            <iframe
              ref={(el) => {
                setCalendarIframeEl(el);
              }}
              src="/calendar-frame"
              className="h-full w-full"
              title="Calendar frame"
            />
          </div>
        </section>

        <aside className="w-[420px] shrink-0 border-l bg-background">
          <div className="h-full">
            <Thread />
          </div>
        </aside>
      </div>

      <FrameHost iframe={iframeEl} />
      <FrameHost iframe={calendarIframeEl} />
    </AssistantRuntimeProvider>
  );
}

