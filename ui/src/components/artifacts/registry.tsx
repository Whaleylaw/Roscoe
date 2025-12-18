"use client";

import { ArtifactComponent } from "./types";

/**
 * Central registry for all artifact components
 * Follows "build once, use many" philosophy
 */
class ArtifactRegistry {
  private components = new Map<string, ArtifactComponent>();

  register(component: ArtifactComponent) {
    if (this.components.has(component.id)) {
      console.warn(`Artifact component ${component.id} already registered, overwriting`);
    }
    this.components.set(component.id, component);
  }

  get(id: string): ArtifactComponent | undefined {
    return this.components.get(id);
  }

  list(): ArtifactComponent[] {
    return Array.from(this.components.values());
  }

  listByCategory(category: ArtifactComponent["category"]): ArtifactComponent[] {
    return this.list().filter((c) => c.category === category);
  }
}

export const artifactRegistry = new ArtifactRegistry();
