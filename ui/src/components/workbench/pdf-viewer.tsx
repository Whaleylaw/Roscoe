"use client";

import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, ExternalLink } from "lucide-react";

interface PdfViewerProps {
  path: string;
}

export function PdfViewer({ path }: PdfViewerProps) {
  // Just use the browser's native PDF viewer via iframe
  const pdfUrl = `/api/workspace/file?path=${encodeURIComponent(path)}`;

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Simple toolbar */}
      <div className="flex items-center justify-between border-b border-[#d4c5a9] px-4 py-3 bg-[#f8f7f4]">
        <span className="text-[13px] text-[#1e3a5f] font-medium truncate max-w-[300px]">
          {path.split("/").pop()}
        </span>
        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-lg text-[#1e3a5f] hover:bg-[#f5f3ed] border border-[#d4c5a9] transition-colors"
          title="Open in new tab"
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>

      {/* Native browser PDF viewer */}
      <iframe
        src={pdfUrl}
        className="flex-1 w-full border-0"
        title={path}
      />
    </div>
  );
}
