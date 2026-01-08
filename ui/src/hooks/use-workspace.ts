import { useEffect } from "react";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { WorkspaceFile } from "@/types";

export function useWorkspace() {
  const { workspaceFiles, setWorkspaceFiles, currentPath, setCurrentPath } = useWorkbenchStore();

  const loadDirectory = async (path: string) => {
    try {
      const response = await fetch(`/api/workspace/list?path=${encodeURIComponent(path)}`);
      if (!response.ok) throw new Error("Failed to load directory");

      const data = await response.json();
      setWorkspaceFiles(data.files);
      setCurrentPath(data.path);
    } catch (error) {
      console.error("Error loading directory:", error);
      setWorkspaceFiles([]);
    }
  };

  const readFile = async (path: string): Promise<string | null> => {
    try {
      const response = await fetch(`/api/workspace/file?path=${encodeURIComponent(path)}`);
      if (!response.ok) throw new Error("Failed to read file");

      const data = await response.json();
      return data.content;
    } catch (error) {
      console.error("Error reading file:", error);
      return null;
    }
  };

  useEffect(() => {
    loadDirectory("/");
  }, []);

  return {
    files: workspaceFiles,
    currentPath,
    loadDirectory,
    readFile,
  };
}
