"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface DocumentViewerData {
  file_path: string;
  file_name: string;
  file_type: "pdf" | "markdown" | "text" | "json" | "html";
  file_size: number;
  file_size_formatted: string;
  content?: string | null;
  url?: string | null;
  content_note?: string | null;
}

interface DocumentViewerProps {
  data: DocumentViewerData;
}

// PDF Viewer - uses iframe with signed URL
function PDFViewer({ url, fileName }: { url: string; fileName: string }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  return (
    <div className="flex flex-col h-full">
      {loading && !error && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
          <span className="ml-3 text-zinc-400">Loading PDF...</span>
        </div>
      )}
      {error && (
        <div className="flex flex-col items-center justify-center py-8 text-red-400">
          <svg className="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p>Failed to load PDF</p>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 text-emerald-400 hover:text-emerald-300 underline"
          >
            Open in new tab →
          </a>
        </div>
      )}
      <iframe
        src={url}
        title={fileName}
        className={`w-full flex-1 min-h-[600px] rounded-lg border border-zinc-700 bg-zinc-900 ${loading ? 'hidden' : ''}`}
        onLoad={() => setLoading(false)}
        onError={() => {
          setLoading(false);
          setError(true);
        }}
      />
    </div>
  );
}

// Markdown Viewer - renders markdown with syntax highlighting
function MarkdownViewer({ content, fileName }: { content: string; fileName: string }) {
  return (
    <div className="prose prose-invert prose-emerald max-w-none">
      <ReactMarkdown
        components={{
          // Custom code block rendering with syntax highlighting
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || "");
            return !inline && match ? (
              <SyntaxHighlighter
                style={oneDark}
                language={match[1]}
                PreTag="div"
                className="rounded-lg !bg-zinc-900 !p-4"
                {...props}
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code className="bg-zinc-800 px-1.5 py-0.5 rounded text-emerald-300" {...props}>
                {children}
              </code>
            );
          },
          // Style headings
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-zinc-100 border-b border-zinc-700 pb-2 mb-4">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-zinc-200 mt-6 mb-3">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-medium text-zinc-300 mt-4 mb-2">{children}</h3>
          ),
          // Style links
          a: ({ href, children }) => (
            <a href={href} className="text-emerald-400 hover:text-emerald-300 underline" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
          // Style lists
          ul: ({ children }) => <ul className="list-disc list-inside space-y-1 text-zinc-300">{children}</ul>,
          ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 text-zinc-300">{children}</ol>,
          // Style paragraphs
          p: ({ children }) => <p className="text-zinc-300 leading-relaxed mb-4">{children}</p>,
          // Style blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-emerald-500 pl-4 py-2 my-4 bg-zinc-800/50 rounded-r-lg">
              {children}
            </blockquote>
          ),
          // Style tables
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border border-zinc-700 rounded-lg">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="bg-zinc-800 px-4 py-2 text-left text-zinc-200 font-medium border-b border-zinc-700">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2 text-zinc-300 border-b border-zinc-800">{children}</td>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

// Text/JSON Viewer - displays plain text with line numbers
function TextViewer({ content, fileName, fileType }: { content: string; fileName: string; fileType: string }) {
  const lines = content.split("\n");
  const lineNumberWidth = String(lines.length).length;

  // For JSON, try to format it nicely
  let displayContent = content;
  if (fileType === "json") {
    try {
      const parsed = JSON.parse(content);
      displayContent = JSON.stringify(parsed, null, 2);
    } catch {
      // Keep original if not valid JSON
    }
  }

  return (
    <div className="relative">
      <div className="overflow-x-auto rounded-lg border border-zinc-700 bg-zinc-900">
        <pre className="p-4 text-sm font-mono">
          {displayContent.split("\n").map((line, index) => (
            <div key={index} className="flex hover:bg-zinc-800/50">
              <span
                className="select-none text-zinc-600 pr-4 text-right"
                style={{ minWidth: `${lineNumberWidth + 2}ch` }}
              >
                {index + 1}
              </span>
              <span className="text-zinc-300 whitespace-pre-wrap break-all">{line || " "}</span>
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}

// Download button component
function DownloadButton({ url, fileName }: { url: string; fileName: string }) {
  return (
    <a
      href={url}
      download={fileName}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm text-zinc-300 transition-colors"
    >
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      Download
    </a>
  );
}

// File type icon component
function FileTypeIcon({ fileType }: { fileType: string }) {
  const iconClass = "w-6 h-6";
  
  switch (fileType) {
    case "pdf":
      return (
        <svg className={`${iconClass} text-red-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM8.5 13H10v4.5a.5.5 0 0 1-1 0V14H8.5a.5.5 0 0 1 0-1zm3 0h1.25c.689 0 1.25.561 1.25 1.25v.5c0 .689-.561 1.25-1.25 1.25H12v1.5a.5.5 0 0 1-1 0V13.5a.5.5 0 0 1 .5-.5zm1.25 2a.25.25 0 0 0 .25-.25v-.5a.25.25 0 0 0-.25-.25H12v1h.75zm2.25-2h1.5a.5.5 0 0 1 0 1h-1v1h1a.5.5 0 0 1 0 1h-1v1.5a.5.5 0 0 1-1 0v-4a.5.5 0 0 1 .5-.5z" />
        </svg>
      );
    case "markdown":
      return (
        <svg className={`${iconClass} text-blue-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.56 18H3.44C2.65 18 2 17.37 2 16.59V7.41C2 6.63 2.65 6 3.44 6h17.12c.79 0 1.44.63 1.44 1.41v9.18c0 .78-.65 1.41-1.44 1.41zM6.81 15.19v-3.66l1.92 2.35 1.92-2.35v3.66h1.93V8.81h-1.93l-1.92 2.35-1.92-2.35H4.89v6.38h1.92zm10.74-3.19l-2.56-2.56v1.92h-2.56v1.28h2.56v1.92l2.56-2.56z" />
        </svg>
      );
    case "json":
      return (
        <svg className={`${iconClass} text-yellow-400`} fill="currentColor" viewBox="0 0 24 24">
          <path d="M5 3h2v2H5v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5h2v2H5c-1.07-.27-2-.9-2-2v-4a2 2 0 0 0-2-2H0v-2h1a2 2 0 0 0 2-2V5a2 2 0 0 1 2-2m14 0a2 2 0 0 1 2 2v4a2 2 0 0 0 2 2h1v2h-1a2 2 0 0 0-2 2v4a2 2 0 0 1-2 2h-2v-2h2v-5a2 2 0 0 1 2-2 2 2 0 0 1-2-2V5h-2V3h2m-7 12a1 1 0 0 1 1 1 1 1 0 0 1-1 1 1 1 0 0 1-1-1 1 1 0 0 1 1-1m-4 0a1 1 0 0 1 1 1 1 1 0 0 1-1 1 1 1 0 0 1-1-1 1 1 0 0 1 1-1m8 0a1 1 0 0 1 1 1 1 1 0 0 1-1 1 1 1 0 0 1-1-1 1 1 0 0 1 1-1z" />
        </svg>
      );
    default:
      return (
        <svg className={`${iconClass} text-zinc-400`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
  }
}

export default function DocumentViewer({ data }: DocumentViewerProps) {
  const { file_path, file_name, file_type, file_size_formatted, content, url, content_note } = data;

  return (
    <div className="space-y-4">
      {/* Header with file info */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileTypeIcon fileType={file_type} />
          <div>
            <h2 className="text-lg font-semibold text-zinc-100">{file_name}</h2>
            <p className="text-sm text-zinc-500">
              {file_type.toUpperCase()} • {file_size_formatted}
            </p>
          </div>
        </div>
        {url && <DownloadButton url={url} fileName={file_name} />}
      </div>

      {/* File path breadcrumb */}
      <div className="text-xs text-zinc-600 font-mono bg-zinc-800/50 px-3 py-1.5 rounded-lg overflow-x-auto">
        {file_path}
      </div>

      {/* Content note if present */}
      {content_note && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-3 text-yellow-300 text-sm">
          {content_note}
        </div>
      )}

      {/* Document content */}
      <div className="mt-4">
        {file_type === "pdf" && url ? (
          <PDFViewer url={url} fileName={file_name} />
        ) : file_type === "markdown" && content ? (
          <MarkdownViewer content={content} fileName={file_name} />
        ) : content ? (
          <TextViewer content={content} fileName={file_name} fileType={file_type} />
        ) : url ? (
          <div className="text-center py-8">
            <p className="text-zinc-400 mb-4">Content preview not available</p>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 rounded-lg text-white transition-colors"
            >
              Open File →
            </a>
          </div>
        ) : (
          <div className="text-center py-8 text-zinc-500">
            No content available
          </div>
        )}
      </div>
    </div>
  );
}

