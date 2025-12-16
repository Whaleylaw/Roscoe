import { NextRequest, NextResponse } from "next/server";
import fs from "node:fs/promises";
import path from "node:path";

export const runtime = "nodejs";

const WORKSPACE_ROOT = process.env["WORKSPACE_ROOT"] || "/mnt/workspace";

function resolveWorkspacePath(inputPath: string) {
  const rel = (inputPath || "/").trim() || "/";
  const normalized = path.posix.normalize(rel.startsWith("/") ? rel : `/${rel}`);

  const abs = path.join(WORKSPACE_ROOT, normalized);
  const absNormalized = path.normalize(abs);
  const rootNormalized = path.normalize(WORKSPACE_ROOT);
  if (!absNormalized.startsWith(rootNormalized)) throw new Error("Invalid path");
  return { normalized, abs: absNormalized };
}

function guessContentType(p: string): string {
  const ext = path.extname(p).toLowerCase();
  switch (ext) {
    case ".pdf":
      return "application/pdf";
    case ".md":
      return "text/markdown; charset=utf-8";
    case ".txt":
    case ".json":
    case ".csv":
    case ".log":
      return "text/plain; charset=utf-8";
    case ".png":
      return "image/png";
    case ".jpg":
    case ".jpeg":
      return "image/jpeg";
    case ".gif":
      return "image/gif";
    case ".webp":
      return "image/webp";
    case ".svg":
      return "image/svg+xml";
    case ".docx":
      return "application/vnd.openxmlformats-officedocument.wordprocessingml.document";
    default:
      return "application/octet-stream";
  }
}

export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url);
    const inputPath = url.searchParams.get("path");
    if (!inputPath) return NextResponse.json({ ok: false, error: "Missing path" }, { status: 400 });

    const { normalized, abs } = resolveWorkspacePath(inputPath);
    const st = await fs.stat(abs);
    if (st.isDirectory()) {
      return NextResponse.json(
        { ok: false, error: "Path is a directory", path: normalized },
        { status: 400 },
      );
    }

    const buf = await fs.readFile(abs);
    return new NextResponse(buf, {
      status: 200,
      headers: {
        "Content-Type": guessContentType(normalized),
        "Content-Length": String(buf.byteLength),
        // Allow the PDF viewer / react-pdf to range-request if needed
        "Accept-Ranges": "bytes",
        "Cache-Control": "no-store",
      },
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json({ ok: false, error: message }, { status: 400 });
  }
}

