"use client";

import { useEffect } from "react";

// Extract path from various tool result formats
function extractHTMLPath(toolResult: any): string | null {
  if (!toolResult) return null;
  
  // Format 1: String like "Updated file /Reports/file.html"
  // This is the actual format from LangGraph/deepagents write_file tool
  if (typeof toolResult === "string") {
    const match = toolResult.match(/([\/\w\-\_\.]+\.html)/i);
    if (match) return match[1];
  }
  
  // Format 2: { path: "/Reports/file.html" }
  if (typeof toolResult === "object" && toolResult.path?.endsWith(".html")) {
    return toolResult.path;
  }
  
  // Format 3: { file_path: "..." } or { filepath: "..." }
  if (typeof toolResult === "object") {
    const path = toolResult.file_path || toolResult.filepath || toolResult.filename;
    if (path?.endsWith(".html")) return path;
  }
  
  return null;
}

export function useArtifactListener(
  onHTMLArtifact: (html: string, title: string, path?: string) => void
) {
  useEffect(() => {
    // Listen for agent HTML file creations
    const checkForHTMLFiles = (event: CustomEvent) => {
      const { tool_name, tool_result } = event.detail;
      
      console.log("[ArtifactListener] Tool result received:", tool_name, tool_result);

      // Check for HTML file creation from write_file or similar tools
      const htmlPath = extractHTMLPath(tool_result);
      
      if (htmlPath && (tool_name === "write_file" || tool_name === "create_file")) {
        console.log("[ArtifactListener] HTML artifact detected:", htmlPath);
        
        // Fetch the HTML content
        fetch(`/api/workspace/file?path=${encodeURIComponent(htmlPath)}`)
          .then(res => res.json())
          .then(data => {
            const title = htmlPath.split("/").pop()?.replace(".html", "") || "Artifact";
            onHTMLArtifact(data.content, title, htmlPath);
          })
          .catch(err => console.error("[ArtifactListener] Error loading HTML:", err));
      }

      // render_ui_script was called - could trigger component rendering
      if (tool_name === "render_ui_script" && tool_result?.component) {
        console.log("[ArtifactListener] render_ui_script:", tool_result);
      }
    };

    window.addEventListener("langgraph:tool_result" as any, checkForHTMLFiles);
    return () => {
      window.removeEventListener("langgraph:tool_result" as any, checkForHTMLFiles);
    };
  }, [onHTMLArtifact]);
}
