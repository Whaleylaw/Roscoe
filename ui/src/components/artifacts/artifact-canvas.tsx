"use client";

import { useState, useEffect } from "react";
import { artifactRegistry } from "./registry";
import { ScrollArea } from "@/components/ui/scroll-area";

// Import artifact components to ensure they register themselves
import "./contact-card";
import "./medical-provider-card";
import "./insurance-card";

export interface ArtifactInstance {
  id: string;
  componentId: string;
  data: any;
  created: string;
}

export function ArtifactCanvas() {
  const [artifacts, setArtifacts] = useState<ArtifactInstance[]>([]);

  // Expose canvas API globally for agent tools
  useEffect(() => {
    (window as any).__artifactCanvas = {
      add: (componentId: string, data: any) => {
        const id = `artifact-${Date.now()}`;
        const newArtifact: ArtifactInstance = {
          id,
          componentId,
          data,
          created: new Date().toISOString(),
        };
        setArtifacts((prev) => [...prev, newArtifact]);
        return id;
      },
      update: (id: string, data: any) => {
        setArtifacts((prev) =>
          prev.map((a) => (a.id === id ? { ...a, data } : a))
        );
      },
      remove: (id: string) => {
        setArtifacts((prev) => prev.filter((a) => a.id !== id));
      },
      clear: () => {
        setArtifacts([]);
      },
    };

    return () => {
      delete (window as any).__artifactCanvas;
    };
  }, []);

  if (artifacts.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">
          Artifacts will appear here when the agent creates them
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-4 space-y-4">
        {artifacts.map((artifact) => {
          const component = artifactRegistry.get(artifact.componentId);
          if (!component) {
            return (
              <div key={artifact.id} className="text-red-500">
                Unknown component: {artifact.componentId}
              </div>
            );
          }

          const Component = component.component;
          return (
            <div key={artifact.id}>
              <Component artifactId={artifact.id} data={artifact.data} />
            </div>
          );
        })}
      </div>
    </ScrollArea>
  );
}
