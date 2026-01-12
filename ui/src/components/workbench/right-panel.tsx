"use client";

import { useState, useEffect } from "react";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { DocumentViewer } from "./document-viewer";
import { HTMLSandbox } from "@/components/artifacts/html-sandbox";
import { useArtifactListener } from "@/hooks/use-artifact-listener";
import { X, FileText, Code, Calendar } from "lucide-react";
import { cn } from "@/lib/utils";

type ViewTab = "document" | "artifact";

export function RightPanel() {
  const { openDocument, setOpenDocument, setRightPanelOpen, panelsSwapped, setPanelsSwapped } = useWorkbenchStore();
  const [activeTab, setActiveTab] = useState<ViewTab>("document");
  const [agentArtifact, setAgentArtifact] = useState<{
    html: string;
    title: string;
    path?: string;
  } | null>(null);

  // Listen for agent-created HTML artifacts
  useArtifactListener((html, title, path) => {
    setAgentArtifact({ html, title, path });
    setActiveTab("artifact"); // Auto-switch to artifact tab
    setRightPanelOpen(true); // Auto-open panel
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
      setActiveTab("artifact");
    } else if (openDocument) {
      setManualHTML(null);
      setActiveTab("document");
    }
  }, [openDocument]);

  // Listen for postMessage from directory browser iframe
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // SECURITY: Only accept messages from same origin
      if (event.origin !== window.location.origin) {
        console.warn('[RightPanel] Rejected postMessage from unauthorized origin:', event.origin);
        return;
      }

      if (event.data.type === 'open_document') {
        const payload = event.data.payload;

        // Validate payload structure
        if (!payload || typeof payload !== 'object') {
          console.error('[RightPanel] Invalid payload structure');
          return;
        }

        const { path, type, source } = payload;

        // Validate required fields
        if (!path || typeof path !== 'string') {
          console.error('[RightPanel] Missing or invalid path');
          return;
        }

        if (!type || typeof type !== 'string') {
          console.error('[RightPanel] Missing or invalid type');
          return;
        }

        console.log('[RightPanel] Received open_document message:', {
          path,
          type,
          source,
        });

        // Validate type
        const validTypes = ['pdf', 'docx', 'md', 'html'];
        if (!validTypes.includes(type)) {
          console.error('[RightPanel] Invalid document type:', type);
          return;
        }

        // Open the document
        setOpenDocument({
          path,
          type: type as 'pdf' | 'docx' | 'md' | 'html',
        });
      }
    };

    window.addEventListener('message', handleMessage);

    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [setOpenDocument]);

  const handleClose = () => {
    setRightPanelOpen(false);
  };

  const handleCloseDocument = () => {
    setOpenDocument(null);
    setAgentArtifact(null);
    setManualHTML(null);
    // Revert swap when closing artifact
    if (panelsSwapped) {
      setPanelsSwapped(false);
    }
  };

  // Determine what to show
  const hasDocument = openDocument && openDocument.type !== "html";
  const hasArtifact = manualHTML || agentArtifact;

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#d4c5a9] px-4 py-3 bg-[#f8f7f4]">
        <div className="flex items-center gap-2">
          {/* Tab buttons if both document and artifact exist */}
          {hasDocument && hasArtifact ? (
            <div className="flex items-center gap-1 bg-white rounded-lg p-1 border border-[#d4c5a9]">
              <button
                onClick={() => setActiveTab("document")}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center gap-1.5",
                  activeTab === "document"
                    ? "bg-[#1e3a5f] text-white"
                    : "text-[#1e3a5f] hover:bg-[#f5f3ed]"
                )}
              >
                <FileText className="h-3.5 w-3.5" />
                Document
              </button>
              <button
                onClick={() => setActiveTab("artifact")}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center gap-1.5",
                  activeTab === "artifact"
                    ? "bg-[#1e3a5f] text-white"
                    : "text-[#1e3a5f] hover:bg-[#f5f3ed]"
                )}
              >
                <Code className="h-3.5 w-3.5" />
                Artifact
              </button>
            </div>
          ) : (
            <span className="text-sm font-medium text-[#1e3a5f]">
              {hasArtifact ? "Artifact" : hasDocument ? "Document" : "Panel"}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {(hasDocument || hasArtifact) && (
            <button
              onClick={handleCloseDocument}
              className="text-xs text-[#8b7355] hover:text-[#1e3a5f] transition-colors"
            >
              Clear
            </button>
          )}
          <button
            onClick={handleClose}
            className="p-1.5 rounded-md hover:bg-[#e5e1d8] transition-colors text-[#1e3a5f]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden bg-[#f8f7f4]">
        {/* Show document viewer */}
        {activeTab === "document" && hasDocument && (
          <DocumentViewer />
        )}

        {/* Show artifact */}
        {activeTab === "artifact" && (
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
          ) : null
        )}

        {/* Empty state */}
        {!hasDocument && !hasArtifact && (
          <div className="flex h-full items-center justify-center text-center px-8">
            <div>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white border border-[#d4c5a9] flex items-center justify-center">
                <FileText className="h-7 w-7 text-[#c9a227]" />
              </div>
              <p className="text-[#1e3a5f] font-medium text-sm mb-2">
                No document open
              </p>
              <p className="text-[#8b7355] text-xs max-w-[200px]">
                Open a file from the sidebar or ask Roscoe to create an artifact.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

