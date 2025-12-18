"use client";

import { useEffect, useMemo, useState } from "react";
import { ChevronLeftIcon, FolderIcon, FileIcon, RefreshCwIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useWorkbenchStore } from "@/lib/workbench-store";

type Entry = {
  name: string;
  path: string;
  type: "dir" | "file";
  size: number;
  mtimeMs: number;
};

type ListResponse =
  | { ok: true; path: string; entries: Entry[] }
  | { ok: false; error: string };

function parentPath(p: string) {
  const normalized = p === "" ? "/" : p;
  if (normalized === "/") return "/";
  const parts = normalized.split("/").filter(Boolean);
  parts.pop();
  return "/" + parts.join("/");
}

export function FileBrowser() {
  const currentPath = useWorkbenchStore((s) => s.browserPath);
  const setBrowserPath = useWorkbenchStore((s) => s.setBrowserPath);
  const [entries, setEntries] = useState<Entry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setSelectedPath = useWorkbenchStore((s) => s.setSelectedPath);

  const breadcrumb = useMemo(() => {
    const parts = currentPath.split("/").filter(Boolean);
    return ["/", ...parts];
  }, [currentPath]);

  const load = async (p: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `/api/workspace/list?path=${encodeURIComponent(p)}`,
        { cache: "no-store" },
      );
      const data = (await res.json()) as ListResponse;
      if (!data.ok) throw new Error(data.error);
      setBrowserPath(data.path);
      setEntries(data.entries);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to load directory";
      setError(msg);
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load(currentPath);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b px-2 py-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => load(parentPath(currentPath))}
          disabled={loading || currentPath === "/"}
          aria-label="Up one folder"
        >
          <ChevronLeftIcon className="size-4" />
        </Button>
        <div className="min-w-0 flex-1 truncate text-sm font-semibold">
          {breadcrumb.join(" / ").replace("//", "/")}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => load(currentPath)}
          disabled={loading}
          aria-label="Refresh"
        >
          <RefreshCwIcon className={cn("size-4", loading && "animate-spin")} />
        </Button>
      </div>

      <div className="flex-1 overflow-auto p-2">
        {error && (
          <div className="rounded-md border border-destructive/30 bg-destructive/10 p-2 text-xs text-destructive">
            {error}
          </div>
        )}

        <div className="mt-2 flex flex-col">
          {entries.map((e) => {
            const Icon = e.type === "dir" ? FolderIcon : FileIcon;
            return (
              <button
                key={e.path}
                className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-accent"
                onClick={() => {
                  if (e.type === "dir") {
                    void load(e.path);
                    setSelectedPath(null);
                    return;
                  }
                  setSelectedPath(e.path);
                }}
              >
                <Icon className="size-4 text-muted-foreground" />
                <span className="min-w-0 flex-1 truncate">{e.name}</span>
              </button>
            );
          })}
          {!loading && !error && entries.length === 0 && (
            <div className="px-2 py-3 text-xs text-muted-foreground">
              No files.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

