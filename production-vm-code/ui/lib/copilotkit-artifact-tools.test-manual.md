# Manual Test Plan for CopilotKit Artifact Tools

## Implementation Complete ✓

The `useCopilotArtifactTools()` hook has been created with the following features:

### 1. create_artifact ✓
- **Purpose**: Create a new UI artifact and display it to the user
- **Parameters**:
  - `componentId` (string, required): Type of artifact to create (e.g., "contact-card", "medical-provider-card", "insurance-card")
  - `data` (object, required): Data for the artifact component
- **Validation**:
  - Checks if artifact canvas is mounted
  - Validates component exists in registry
  - Validates data against Zod schema
- **Returns**: `{ success: true, artifactId: string, message: string }`
- **Error Handling**: Throws descriptive errors for missing canvas, unknown components, or invalid data

### 2. update_artifact ✓
- **Purpose**: Update an existing artifact with new data
- **Parameters**:
  - `artifactId` (string, required): ID of the artifact to update
  - `data` (object, required): New data for the artifact
- **Validation**:
  - Checks if artifact canvas is mounted
- **Returns**: `{ success: true, message: string }`
- **Error Handling**: Throws error if canvas not mounted

### 3. remove_artifact ✓
- **Purpose**: Remove an artifact from the canvas
- **Parameters**:
  - `artifactId` (string, required): ID of the artifact to remove
- **Validation**:
  - Checks if artifact canvas is mounted
- **Returns**: `{ success: true, message: string }`
- **Error Handling**: Throws error if canvas not mounted

### 4. list_artifact_types ✓
- **Purpose**: Get a list of all available artifact component types
- **Parameters**: None
- **Returns**: `{ success: true, artifacts: Array<{ id, name, description, category }> }`
- **No validation needed**: Simply returns registry contents

## Integration with window.__artifactCanvas ✓

All tools interact with `window.__artifactCanvas` which is set by the ArtifactCanvas component:
- `canvas.add(componentId, data)` - Creates and returns artifact ID
- `canvas.update(artifactId, data)` - Updates existing artifact
- `canvas.remove(artifactId)` - Removes artifact from canvas

## Type Safety ✓

- Uses TypeScript for all parameters
- Zod schema validation for component data
- Proper error messages with context

## Error Handling ✓

Each tool includes proper error handling:
1. Check if canvas is mounted (for all tools)
2. Check if component exists (for create_artifact)
3. Validate data against schema (for create_artifact)
4. Descriptive error messages with actionable information

## Testing Strategy

### Unit Testing
Run the test file: `ui/lib/__tests__/copilotkit-artifact-tools.test.tsx`
- Verifies artifact registry has components
- Validates schema properties
- Tests schema validation with valid/invalid data

### Integration Testing
1. Start the UI with CopilotKit enabled
2. Open the Artifacts view in the workbench
3. Use the CopilotKit sidebar to test each tool:

#### Test create_artifact
```
Agent prompt: "Create a contact card for John Doe, attorney, email john@law.com"
Expected: ContactCard appears in Artifacts view
```

#### Test update_artifact
```
Agent prompt: "Update the contact card to add phone number 555-1234"
Expected: Existing card updates with phone number
```

#### Test remove_artifact
```
Agent prompt: "Remove the contact card"
Expected: Card disappears from Artifacts view
```

#### Test list_artifact_types
```
Agent prompt: "What types of artifacts can you create?"
Expected: Returns list with contact-card, medical-provider-card, insurance-card
```

## File Created
- `/Volumes/X10 Pro/Roscoe/production-vm-code/ui/lib/copilotkit-artifact-tools.tsx` ✓

## Changes Made
- Created new file with all four CopilotKit actions
- Fixed TypeScript error in artifact-canvas.tsx (added types to onAction callback)
- Created test file for automated testing

## Dependencies Verified
- ✓ @copilotkit/react-core installed (v1.50.0)
- ✓ artifactRegistry available
- ✓ Zod schemas in artifact components
- ✓ window.__artifactCanvas exposed by ArtifactCanvas component
