"use client";

import { ExternalLink, Download } from "lucide-react";

interface HTMLSandboxProps {
  html: string;
  title: string;
  filePath?: string;
}

export function HTMLSandbox({ html, title, filePath }: HTMLSandboxProps) {
  const downloadHTML = () => {
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#d4c5a9] px-4 py-3 bg-[#f8f7f4]">
        <div>
          <h3 className="font-serif font-semibold text-[#1e3a5f]">{title}</h3>
          {filePath && (
            <p className="text-[11px] text-[#8b7355] mt-0.5">{filePath}</p>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => {
              const blob = new Blob([html], { type: "text/html" });
              const url = URL.createObjectURL(blob);
              window.open(url, "_blank");
            }}
            title="Open in new tab"
            className="p-2 rounded-lg text-[#1e3a5f] hover:bg-[#f5f3ed] border border-transparent hover:border-[#d4c5a9] transition-colors"
          >
            <ExternalLink className="h-4 w-4" />
          </button>
          <button
            onClick={downloadHTML}
            title="Download HTML"
            className="p-2 rounded-lg text-[#1e3a5f] hover:bg-[#f5f3ed] border border-transparent hover:border-[#d4c5a9] transition-colors"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Iframe Sandbox */}
      <iframe
        srcDoc={html}
        className="flex-1 w-full border-0 bg-[#f8f7f4]"
        sandbox="allow-scripts allow-same-origin allow-forms"
        title={title}
      />
    </div>
  );
}
