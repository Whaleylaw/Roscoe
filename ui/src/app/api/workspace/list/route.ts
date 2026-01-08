import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

const WORKSPACE_ROOT = process.env.NEXT_PUBLIC_WORKSPACE_ROOT || "/mnt/workspace";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestedPath = searchParams.get("path") || "/";

    // Security: Prevent directory traversal
    const safePath = path.join(WORKSPACE_ROOT, requestedPath);
    if (!safePath.startsWith(WORKSPACE_ROOT)) {
      return NextResponse.json({ error: "Invalid path" }, { status: 403 });
    }

    const entries = await fs.readdir(safePath, { withFileTypes: true });

    const files = await Promise.all(
      entries.map(async (entry) => {
        const fullPath = path.join(safePath, entry.name);
        const stats = await fs.stat(fullPath);
        const relativePath = path.relative(WORKSPACE_ROOT, fullPath);

        return {
          name: entry.name,
          path: "/" + relativePath.replace(/\\/g, "/"),
          type: entry.isDirectory() ? "directory" : "file",
          size: stats.size,
          modified: stats.mtime.toISOString(),
        };
      })
    );

    // Sort: directories first, then alphabetically
    files.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === "directory" ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });

    return NextResponse.json({ files, path: requestedPath });
  } catch (error) {
    console.error("Workspace list error:", error);
    return NextResponse.json(
      { error: "Failed to list directory" },
      { status: 500 }
    );
  }
}
