"use client";

import { File, Folder, ChevronRight, ChevronDown } from "lucide-react";
import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useWorkspace } from "@/hooks/use-workspace";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { WorkspaceFile } from "@/types";
import { cn } from "@/lib/utils";

export function FileBrowser() {
  const { files, currentPath, loadDirectory, readFile } = useWorkspace();
  const { setOpenDocument, setCenterView } = useWorkbenchStore();
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(new Set());

  const toggleDirectory = (path: string) => {
    const newExpanded = new Set(expandedDirs);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
      loadDirectory(path);
    }
    setExpandedDirs(newExpanded);
  };

  const handleFileClick = async (file: WorkspaceFile) => {
    if (file.type === "directory") {
      toggleDirectory(file.path);
    } else {
      // Determine file type and open in viewer
      const ext = file.name.split(".").pop()?.toLowerCase();
      if (ext === "pdf") {
        setOpenDocument({ path: file.path, type: "pdf" });
        setCenterView("viewer");
      } else if (ext === "html" || ext === "htm") {
        // Open HTML in artifacts panel
        setOpenDocument({ path: file.path, type: "html" });
        setCenterView("artifacts");
      } else {
        // All other files treated as text/markdown
        setOpenDocument({ path: file.path, type: "md" });
        setCenterView("viewer");
      }
    }
  };

  const navigateUp = () => {
    const parts = currentPath.split("/").filter(Boolean);
    parts.pop();
    const parentPath = "/" + parts.join("/");
    loadDirectory(parentPath);
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="border-b border-[#e5e1d8] p-3 bg-[#f8f7f4]">
        <div className="flex items-center gap-2">
          <Folder className="h-4 w-4 text-[#c9a227]" />
          <span className="text-[13px] font-medium text-[#1e3a5f] truncate">{currentPath || "/"}</span>
        </div>
        {currentPath !== "/" && (
          <button
            onClick={navigateUp}
            className="mt-2 text-[11px] text-[#8b7355] hover:text-[#1e3a5f] transition-colors"
          >
            ← Parent directory
          </button>
        )}
      </div>

      {/* File list */}
      <ScrollArea className="flex-1">
        <div className="flex flex-col gap-0.5 p-2">
          {files.map((file) => (
            <FileItem
              key={file.path}
              file={file}
              isExpanded={expandedDirs.has(file.path)}
              onToggle={() => toggleDirectory(file.path)}
              onClick={() => handleFileClick(file)}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

interface FileItemProps {
  file: WorkspaceFile;
  isExpanded: boolean;
  onToggle: () => void;
  onClick: () => void;
}

function FileItem({ file, isExpanded, onToggle, onClick }: FileItemProps) {
  const isDirectory = file.type === "directory";

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-[13px] text-[#1e3a5f]",
        "text-left transition-colors",
        "hover:bg-[#f5f3ed] border border-transparent hover:border-[#e5e1d8]"
      )}
    >
      {isDirectory ? (
        <>
          {isExpanded ? (
            <ChevronDown className="h-3 w-3 shrink-0 text-[#8b7355]" />
          ) : (
            <ChevronRight className="h-3 w-3 shrink-0 text-[#8b7355]" />
          )}
          <Folder className="h-4 w-4 shrink-0 text-[#c9a227]" />
        </>
      ) : (
        <>
          <div className="w-3 shrink-0" /> {/* Spacer */}
          <File className="h-4 w-4 shrink-0 text-[#1e3a5f]/60" />
        </>
      )}
      <span className="truncate">{file.name}</span>
    </button>
  );
}
