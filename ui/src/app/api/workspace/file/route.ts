import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";

const WORKSPACE_ROOT = process.env.NEXT_PUBLIC_WORKSPACE_ROOT || "/mnt/workspace";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestedPath = searchParams.get("path");

    if (!requestedPath) {
      return NextResponse.json({ error: "Path required" }, { status: 400 });
    }

    // Security: Prevent directory traversal
    const safePath = path.join(WORKSPACE_ROOT, requestedPath);
    if (!safePath.startsWith(WORKSPACE_ROOT)) {
      return NextResponse.json({ error: "Invalid path" }, { status: 403 });
    }

    const ext = path.extname(safePath).toLowerCase();
    const stats = await fs.stat(safePath);

    // Handle binary files (PDFs)
    if (ext === ".pdf") {
      const buffer = await fs.readFile(safePath);
      return new NextResponse(buffer, {
        headers: {
          "Content-Type": "application/pdf",
          "Content-Length": stats.size.toString(),
        },
      });
    }

    // Handle text files
    const content = await fs.readFile(safePath, "utf-8");
    return NextResponse.json({
      content,
      path: requestedPath,
      size: stats.size,
      modified: stats.mtime.toISOString(),
    });
  } catch (error) {
    console.error("Workspace file error:", error);
    return NextResponse.json(
      { error: "Failed to read file" },
      { status: 500 }
    );
  }
}
