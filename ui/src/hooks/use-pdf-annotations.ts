"use client";

import { useWorkbenchStore } from "@/stores/workbench-store";
import { DocumentAnnotation } from "@/types";
import { useState } from "react";

export function usePdfAnnotations(documentPath: string) {
  const { openDocument, setOpenDocument } = useWorkbenchStore();
  const [selectedAnnotation, setSelectedAnnotation] = useState<string | null>(null);

  const addAnnotation = (annotation: Omit<DocumentAnnotation, "id" | "created" | "author">) => {
    const newAnnotation: DocumentAnnotation = {
      ...annotation,
      id: `annotation-${Date.now()}`,
      created: new Date().toISOString(),
      author: "user", // TODO: Get from auth context
    };

    const updatedDoc = {
      ...openDocument!,
      annotations: [...(openDocument?.annotations || []), newAnnotation],
    };

    setOpenDocument(updatedDoc);

    // TODO: Persist to backend
    return newAnnotation;
  };

  const updateAnnotation = (id: string, updates: Partial<DocumentAnnotation>) => {
    if (!openDocument?.annotations) return;

    const updated = openDocument.annotations.map(a =>
      a.id === id ? { ...a, ...updates } : a
    );

    setOpenDocument({
      ...openDocument,
      annotations: updated,
    });

    // TODO: Persist to backend
  };

  const deleteAnnotation = (id: string) => {
    if (!openDocument?.annotations) return;

    const filtered = openDocument.annotations.filter(a => a.id !== id);
    setOpenDocument({
      ...openDocument,
      annotations: filtered,
    });

    // TODO: Persist to backend
  };

  const setAnnotationMode = (mode: "highlight" | "comment" | "underline" | null) => {
    if (!openDocument) return;
    setOpenDocument({
      ...openDocument,
      annotationMode: mode,
    });
  };

  return {
    annotations: openDocument?.annotations || [],
    annotationMode: openDocument?.annotationMode || null,
    selectedAnnotation,
    setSelectedAnnotation,
    addAnnotation,
    updateAnnotation,
    deleteAnnotation,
    setAnnotationMode,
  };
}
