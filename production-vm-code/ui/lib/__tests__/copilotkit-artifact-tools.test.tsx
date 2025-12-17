/**
 * Test file for copilotkit-artifact-tools
 * Verifies that the tools are properly structured and will work with CopilotKit
 */

import { artifactRegistry } from "@/components/artifacts/registry";
import "@/components/artifacts/contact-card";
import "@/components/artifacts/medical-provider-card";
import "@/components/artifacts/insurance-card";

describe("CopilotKit Artifact Tools", () => {
  test("artifact registry has registered components", () => {
    const components = artifactRegistry.list();
    expect(components.length).toBeGreaterThan(0);

    const componentIds = components.map((c) => c.id);
    expect(componentIds).toContain("contact-card");
    expect(componentIds).toContain("medical-provider-card");
    expect(componentIds).toContain("insurance-card");
  });

  test("each component has required properties", () => {
    const components = artifactRegistry.list();

    components.forEach((component) => {
      expect(component.id).toBeDefined();
      expect(component.name).toBeDefined();
      expect(component.description).toBeDefined();
      expect(component.component).toBeDefined();
      expect(component.schema).toBeDefined();
      expect(component.category).toBeDefined();
    });
  });

  test("contact-card schema validates correct data", () => {
    const contactCard = artifactRegistry.get("contact-card");
    expect(contactCard).toBeDefined();

    const validData = {
      name: "John Doe",
      email: "john@example.com",
      phone: "555-1234",
    };

    expect(() => contactCard!.schema.parse(validData)).not.toThrow();
  });

  test("contact-card schema rejects invalid data", () => {
    const contactCard = artifactRegistry.get("contact-card");
    expect(contactCard).toBeDefined();

    const invalidData = {
      name: "", // Empty name should fail
      email: "not-an-email", // Invalid email
    };

    expect(() => contactCard!.schema.parse(invalidData)).toThrow();
  });
});
