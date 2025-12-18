"use client";

import { useEffect, useMemo, useState } from "react";
import "@assistant-ui/react-markdown/styles/dot.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { useWorkbenchStore } from "@/lib/workbench-store";
import { Button } from "@/components/ui/button";

export function DocumentViewer() {
  const selectedPath = useWorkbenchStore((s) => s.selectedPath);
  const setCenterView = useWorkbenchStore((s) => s.setCenterView);
  const requestOpenInMonaco = useWorkbenchStore((s) => s.requestOpenInMonaco);
  const [text, setText] = useState<string | null>(null);
  const [textError, setTextError] = useState<string | null>(null);
  const [openInMonacoError, setOpenInMonacoError] = useState<string | null>(
    null,
  );

  const extname = (p: string) => {
    const i = p.lastIndexOf(".");
    const j = p.lastIndexOf("/");
    if (i === -1 || i < j) return "";
    return p.slice(i).toLowerCase();
  };

  const ext = useMemo(() => {
    if (!selectedPath) return "";
    return extname(selectedPath);
  }, [selectedPath]);

  const fileUrl = useMemo(() => {
    if (!selectedPath) return null;
    return `/api/workspace/file?path=${encodeURIComponent(selectedPath)}`;
  }, [selectedPath]);

  useEffect(() => {
    setText(null);
    setTextError(null);
    if (!selectedPath) return;

    const isText = [".md", ".txt", ".json", ".csv", ".log"].includes(ext);
    if (!isText || !fileUrl) return;

    const run = async () => {
      try {
        const res = await fetch(fileUrl, { cache: "no-store" });
        if (!res.ok) throw new Error(`Failed to load (${res.status})`);
        const t = await res.text();
        setText(t);
      } catch (e) {
        setTextError(e instanceof Error ? e.message : "Failed to load text");
      }
    };
    void run();
  }, [selectedPath, ext, fileUrl]);

  return (
    <div className="flex h-full flex-col">
      <div className="border-b px-3 py-2 text-sm font-semibold">
        Document Viewer
      </div>
      {!selectedPath && (
        <div className="flex-1 overflow-auto p-6 text-sm text-muted-foreground">
          Select a file from the left to preview it here.
        </div>
      )}

      {selectedPath && (
        <div className="flex min-h-0 flex-1 flex-col">
          <div className="flex items-center gap-2 border-b px-3 py-2 text-xs text-muted-foreground">
            <div className="min-w-0 flex-1 truncate">{selectedPath}</div>
            <Button
              size="sm"
              variant="outline"
              onClick={async () => {
                if (!selectedPath) return;
                setOpenInMonacoError(null);
                try {
                  requestOpenInMonaco(selectedPath);
                  setCenterView("monaco");
                } catch (e) {
                  setOpenInMonacoError(
                    e instanceof Error ? e.message : "Failed to open in Monaco",
                  );
                }
              }}
            >
              Open in Monaco
            </Button>
            {fileUrl && (
              <Button asChild size="sm" variant="outline">
                <a href={fileUrl} target="_blank" rel="noreferrer">
                  Open
                </a>
              </Button>
            )}
          </div>

          <div className="min-h-0 flex-1 overflow-auto p-4">
            {openInMonacoError && (
              <div className="mb-3 rounded-md border border-destructive/30 bg-destructive/10 p-2 text-xs text-destructive">
                {openInMonacoError}
              </div>
            )}

            {ext === ".pdf" && fileUrl && (
              <iframe
                title={selectedPath}
                src={fileUrl}
                className="h-[calc(100vh-140px)] w-full rounded-md border bg-background"
              />
            )}

            {fileUrl &&
              [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"].includes(ext) && (
                <div className="mx-auto w-full max-w-5xl">
                  <img
                    src={fileUrl}
                    alt={selectedPath}
                    className="h-auto w-full rounded-md border"
                  />
                </div>
              )}

            {textError && (
              <div className="text-sm text-destructive">{textError}</div>
            )}

            {text !== null && ext === ".md" && (
              <div className="aui-md">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
              </div>
            )}

            {text !== null &&
              [".txt", ".json", ".csv", ".log"].includes(ext) && (
                <pre className="whitespace-pre-wrap rounded-md border bg-muted p-3 text-xs">
                  {text}
                </pre>
              )}

            {text === null &&
              !textError &&
              ![".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"].includes(
                ext,
              ) &&
              ![".md", ".txt", ".json", ".csv", ".log"].includes(ext) && (
                <div className="text-sm text-muted-foreground">
                  No inline preview for this file type. Use “Open” to download /
                  view.
                </div>
              )}
          </div>
        </div>
      )}
    </div>
  );
}

