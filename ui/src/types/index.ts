export type CenterView = "viewer" | "calendar" | "artifacts";
export type LeftView = "files" | "threads";

export interface WorkspaceFile {
  name: string;
  path: string;
  type: "file" | "directory";
  size?: number;
  modified?: string;
}

export interface Thread {
  id: string;
  title: string;
  status: "active" | "complete" | "error";
  created: string;
  updated: string;
  messageCount: number;
}

export interface DocumentAnnotation {
  id: string;
  page: number;
  type: "highlight" | "comment" | "underline" | "strikethrough";
  content: string; // Comment text or highlighted text
  color: string; // Hex color
  position: {
    x: number; // Percentage of page width
    y: number; // Percentage of page height
    width: number; // Percentage
    height: number; // Percentage
  };
  created: string; // ISO timestamp
  author: string; // User identifier
}

export interface OpenDocument {
  path: string;
  type: "pdf" | "docx" | "md" | "edit" | "html"; // Add "html" mode
  annotations?: DocumentAnnotation[];
  annotationMode?: "highlight" | "comment" | "underline" | null;
  editable?: boolean; // Can this document be edited?
}
