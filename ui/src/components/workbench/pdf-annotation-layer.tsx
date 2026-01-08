"use client";

import { DocumentAnnotation } from "@/types";
import { cn } from "@/lib/utils";

interface PdfAnnotationLayerProps {
  annotations: DocumentAnnotation[];
  currentPage: number;
  scale: number;
  onAnnotationClick: (id: string) => void;
  selectedAnnotationId: string | null;
}

export function PdfAnnotationLayer({
  annotations,
  currentPage,
  scale,
  onAnnotationClick,
  selectedAnnotationId,
}: PdfAnnotationLayerProps) {
  const pageAnnotations = annotations.filter(a => a.page === currentPage);

  return (
    <div className="absolute inset-0 pointer-events-none">
      {pageAnnotations.map((annotation) => (
        <div
          key={annotation.id}
          className={cn(
            "absolute pointer-events-auto cursor-pointer transition-opacity",
            selectedAnnotationId === annotation.id && "ring-2 ring-blue-500"
          )}
          style={{
            left: `${annotation.position.x}%`,
            top: `${annotation.position.y}%`,
            width: `${annotation.position.width}%`,
            height: `${annotation.position.height}%`,
            backgroundColor:
              annotation.type === "highlight"
                ? `${annotation.color}40` // 40 = 25% opacity
                : "transparent",
            borderBottom:
              annotation.type === "underline"
                ? `2px solid ${annotation.color}`
                : "none",
            transform: `scale(${scale})`,
            transformOrigin: "top left",
          }}
          onClick={() => onAnnotationClick(annotation.id)}
          title={annotation.content}
        />
      ))}
    </div>
  );
}
