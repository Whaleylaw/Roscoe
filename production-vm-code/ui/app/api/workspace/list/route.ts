import { NextRequest, NextResponse } from "next/server";
import fs from "node:fs/promises";
import path from "node:path";

export const runtime = "nodejs";

const WORKSPACE_ROOT = process.env["WORKSPACE_ROOT"] || "/mnt/workspace";

function jsonError(status: number, message: string) {
  return NextResponse.json({ ok: false, error: message }, { status });
}

function resolveWorkspacePath(inputPath: string) {
  // Expect workspace-relative paths like "/", "/projects", "/projects/case/..."
  const rel = (inputPath || "/").trim() || "/";
  const normalized = path.posix.normalize(rel.startsWith("/") ? rel : `/${rel}`);

  // Prevent escaping the workspace root via ".."
  const abs = path.join(WORKSPACE_ROOT, normalized);
  const absNormalized = path.normalize(abs);
  const rootNormalized = path.normalize(WORKSPACE_ROOT);
  if (!absNormalized.startsWith(rootNormalized)) {
    throw new Error("Invalid path");
  }
  return { normalized, abs: absNormalized };
}

export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url);
    const inputPath = url.searchParams.get("path") || "/";

    const { normalized, abs } = resolveWorkspacePath(inputPath);

    const dirents = await fs.readdir(abs, { withFileTypes: true });
    const entries = await Promise.all(
      dirents
        .filter((d) => d.name !== "." && d.name !== "..")
        .map(async (d) => {
          const absChild = path.join(abs, d.name);
          const st = await fs.stat(absChild);
          const childPath = path.posix.join(normalized, d.name);
          return {
            name: d.name,
            path: childPath,
            type: d.isDirectory() ? "dir" : "file",
            size: st.size,
            mtimeMs: st.mtimeMs,
          } as const;
        }),
    );

    // dirs first, then alpha
    entries.sort((a, b) => {
      if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

    return NextResponse.json({
      ok: true,
      root: WORKSPACE_ROOT,
      path: normalized,
      entries,
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return jsonError(400, message);
  }
}

