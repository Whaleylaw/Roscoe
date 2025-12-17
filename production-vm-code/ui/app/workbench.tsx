"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

import { FileBrowser } from "@/components/workbench/file-browser";
import { DocumentViewer } from "@/components/workbench/document-viewer";
import { Button } from "@/components/ui/button";
import { useWorkbenchStore } from "@/lib/workbench-store";
import { ArtifactCanvas } from "@/components/artifacts/artifact-canvas";
import { useCopilotArtifactTools } from "@/lib/copilotkit-artifact-tools";

// Import all artifact components to register them
import "@/components/artifacts/contact-card";
import "@/components/artifacts/medical-provider-card";
import "@/components/artifacts/insurance-card";

export function Workbench() {
  const copilotRuntimeUrl = typeof window !== 'undefined'
    ? new URL("/api/copilotkit", window.location.href).href
    : "/api/copilotkit";

  // Enable artifact tools
  useCopilotArtifactTools();

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

  const artifactsStyle = useMemo(() => {
    return centerView === "artifacts" ? "block" : "hidden";
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
    <CopilotKit runtimeUrl={copilotRuntimeUrl} agent="roscoe_paralegal">
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
            <Button
              size="sm"
              variant={centerView === "artifacts" ? "default" : "outline"}
              onClick={() => setCenterView("artifacts")}
            >
              Artifacts
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

          <div className={artifactsStyle + " h-[calc(100vh-44px)] overflow-auto"}>
            <ArtifactCanvas />
          </div>
        </section>

        <aside className="w-[420px] shrink-0 border-l bg-background">
          <CopilotSidebar
            defaultOpen
            labels={{
              title: "Roscoe AI Paralegal",
              initial: "How can I help you today?",
            }}
          />
        </aside>
      </div>
    </CopilotKit>
  );
}

