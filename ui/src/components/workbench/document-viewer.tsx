"use client";

import { useWorkbenchStore } from "@/stores/workbench-store";
import dynamic from "next/dynamic";
import { MarkdownViewer } from "./markdown-viewer";
import { DocumentEditor } from "./document-editor";
import { Button } from "@/components/ui/button";
import { Edit, Eye } from "lucide-react";
import { useState } from "react";

// Dynamic import to prevent SSR issues with PDF.js
const PdfViewer = dynamic(
  () => import("./pdf-viewer").then((mod) => ({ default: mod.PdfViewer })),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        Loading PDF viewer...
      </div>
    ),
  }
);

export function DocumentViewer() {
  const { openDocument } = useWorkbenchStore();
  const [editMode, setEditMode] = useState(false);
  const [fileContent, setFileContent] = useState("");

  if (!openDocument) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">Select a document from the file browser</p>
      </div>
    );
  }

  if (openDocument.type === "pdf") {
    return <PdfViewer path={openDocument.path} />;
  }

  if (openDocument.type === "md") {
    return (
      <div className="flex h-full flex-col">
        {/* Toggle edit/view mode */}
        <div className="flex items-center gap-2 border-b p-2">
          <Button
            size="sm"
            variant={editMode ? "outline" : "default"}
            onClick={() => setEditMode(false)}
          >
            <Eye className="h-4 w-4 mr-1" />
            View
          </Button>
          <Button
            size="sm"
            variant={editMode ? "default" : "outline"}
            onClick={() => setEditMode(true)}
          >
            <Edit className="h-4 w-4 mr-1" />
            Edit
          </Button>
        </div>

        {/* Show editor or viewer based on mode */}
        {editMode ? (
          <DocumentEditor
            initialContent={fileContent}
            onSave={(content) => {
              // TODO: Save to backend
              console.log("Saving:", content);
              setFileContent(content);
            }}
            path={openDocument.path}
          />
        ) : (
          <MarkdownViewer path={openDocument.path} />
        )}
      </div>
    );
  }

  return (
    <div className="flex h-full items-center justify-center">
      <p className="text-muted-foreground">Unsupported file type</p>
    </div>
  );
}
