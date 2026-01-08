"use client";

import { useState, useEffect } from "react";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Button } from "@/components/ui/button";
import { DocumentViewer } from "./document-viewer";
import { CalendarView } from "./calendar-view";
import { ArtifactCanvas } from "@/components/artifacts/artifact-canvas";
import { HTMLSandbox } from "@/components/artifacts/html-sandbox";
import { useArtifactListener } from "@/hooks/use-artifact-listener";

export function CenterView() {
  const { centerView, setCenterView, openDocument } = useWorkbenchStore();
  const [agentArtifact, setAgentArtifact] = useState<{
    html: string;
    title: string;
    path?: string;
  } | null>(null);

  // Listen for agent-created HTML
  useArtifactListener((html, title, path) => {
    setAgentArtifact({ html, title, path });
    setCenterView("artifacts"); // Auto-switch to artifacts tab
  });

  // Load HTML from openDocument if it's HTML type
  const [manualHTML, setManualHTML] = useState<string | null>(null);

  useEffect(() => {
    if (openDocument?.type === "html") {
      // User clicked HTML file in file browser
      fetch(`/api/workspace/file?path=${encodeURIComponent(openDocument.path)}`)
        .then(res => res.json())
        .then(data => setManualHTML(data.content))
        .catch(err => {
          console.error("Error loading HTML:", err);
          setManualHTML("<h1>Error loading HTML file</h1>");
        });
    } else {
      setManualHTML(null);
    }
  }, [openDocument]);

  const TabButton = ({ view, label }: { view: "viewer" | "calendar" | "artifacts"; label: string }) => (
    <button
      onClick={() => setCenterView(view)}
      className={`px-4 py-2 text-[13px] font-medium rounded-lg transition-all ${
        centerView === view
          ? "bg-[#1e3a5f] text-white shadow-sm"
          : "bg-white text-[#1e3a5f] border border-[#d4c5a9] hover:bg-[#f5f3ed]"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="flex h-full flex-col">
      {/* View Switcher */}
      <div className="flex items-center gap-2 border-b border-[#d4c5a9] px-4 py-3 bg-white">
        <TabButton view="viewer" label="Viewer" />
        <TabButton view="calendar" label="Calendar" />
        <TabButton view="artifacts" label="Artifacts" />
      </div>

      {/* View Content */}
      <div className="flex-1 overflow-hidden bg-[#f8f7f4]">
        {centerView === "viewer" && <DocumentViewer />}
        {centerView === "calendar" && <CalendarView />}
        {centerView === "artifacts" && (
          // Show manual HTML, or agent artifact, or empty state
          manualHTML ? (
            <HTMLSandbox
              html={manualHTML}
              title={openDocument?.path.split("/").pop()?.replace(".html", "") || "HTML File"}
              filePath={openDocument?.path}
            />
          ) : agentArtifact ? (
            <HTMLSandbox
              html={agentArtifact.html}
              title={agentArtifact.title}
              filePath={agentArtifact.path}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-center px-8">
              <div>
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5f3ed] border border-[#d4c5a9] flex items-center justify-center">
                  <span className="text-2xl">📄</span>
                </div>
                <p className="text-[#8b7355] text-sm max-w-md">
                  Artifacts will appear here when the agent creates them,
                  or click an HTML file in the file browser to display it.
                </p>
              </div>
            </div>
          )
        )}
      </div>
    </div>
  );
}
