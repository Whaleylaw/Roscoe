# Slash Command Middleware Implementation Design

**Status:** Design Document - Not Yet Implemented
**Created:** 2025-11-22
**Purpose:** Explicit skill invocation via slash commands (e.g., `/medical-records`, `/research`)

## Concept

Add a `@before_model` middleware that intercepts slash commands in user messages and directly loads specified skills, bypassing semantic search. This provides explicit control when users know exactly which skill they want.

## Architecture

### Middleware Execution Order

```python
middleware=[
    slash_command_middleware,      # 1. Check for explicit /commands (NEW)
    SkillSelectorMiddleware(...),  # 2. Semantic search (skipped if slash used)
    model_selector_middleware,      # 3. Model switching (unchanged)
]
```

**Flow:**
1. **Slash Command Middleware** checks if message starts with `/`
2. If yes: Directly load skill by name, set flag to skip semantic search
3. If no: Continue to semantic search middleware
4. **Model Selector** reads skill metadata and switches model (same as before)

## Implementation

### 1. Create `roscoe/slash_command_middleware.py`

```python
"""
Slash Command Middleware for Explicit Skill Invocation

Allows users to directly invoke skills using slash commands like:
- /medical-records
- /research Kentucky statute limitations
- /fact-investigation case=mo_alif

Bypasses semantic search when explicit command is used.
"""

from typing import Any, Dict, Optional
from pathlib import Path
import json
import re
from langchain.agents.middleware import before_model


class SlashCommandMiddleware:
    """
    Middleware for explicit skill invocation via slash commands.

    Syntax: /skill-name [arguments] [prompt text]

    Examples:
        /medical-records
        /research Kentucky statute limitations
        /fact-investigation case=mo_alif
        /medical-records case=mo_alif phases=1,2,3
    """

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.manifest = self._load_manifest()
        self.skill_index = self._build_skill_index()
        self.aliases = self._build_aliases()

    def _load_manifest(self) -> Dict:
        """Load skills manifest"""
        manifest_path = self.skills_dir / "skills_manifest.json"
        with open(manifest_path) as f:
            return json.load(f)

    def _build_skill_index(self) -> Dict[str, Dict]:
        """Build lookup index of skill name -> skill metadata"""
        index = {}
        for skill in self.manifest['skills']:
            index[skill['name']] = skill

            # Also index sub-skills
            for sub_name, sub_skill in skill.get('sub_skills', {}).items():
                index[sub_name] = {
                    'name': sub_name,
                    'description': sub_skill['description'],
                    'file': sub_skill['file'],
                    'model_required': sub_skill.get('model'),
                    'is_sub_skill': True,
                    'parent_skill': skill['name']
                }

        return index

    def _build_aliases(self) -> Dict[str, str]:
        """Build command aliases for shorter commands"""
        return {
            'med': 'medical-records-analysis',
            'r': 'legal-research',
            'research': 'legal-research',
            'fact': 'fact-investigation',
            'extract': 'record-extraction',
            'causation': 'causation-analysis',
            'summary': 'summary-writing',
        }

    def _parse_command(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Parse slash command from message.

        Syntax: /command [key=value] [key=value] [remaining text as prompt]

        Returns:
            {
                'command': str,           # Skill name
                'arguments': dict,        # Parsed key=value pairs
                'prompt': str,           # Remaining text after command/args
                'original': str          # Original message
            }
        """
        if not message.strip().startswith('/'):
            return None

        # Remove leading slash and split
        parts = message[1:].split(maxsplit=1)
        if not parts:
            return None

        command = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        # Resolve aliases
        command = self.aliases.get(command, command)

        # Parse arguments (key=value pairs)
        arguments = {}
        remaining_text = rest

        # Extract key=value patterns
        arg_pattern = r'(\w+)=([^\s]+)'
        matches = re.findall(arg_pattern, rest)

        for key, value in matches:
            arguments[key] = value
            # Remove from remaining text
            remaining_text = remaining_text.replace(f'{key}={value}', '', 1)

        # Clean up remaining text
        prompt = remaining_text.strip()

        return {
            'command': command,
            'arguments': arguments,
            'prompt': prompt,
            'original': message
        }

    def _load_skill_content(self, file_path: str) -> str:
        """Load skill markdown content"""
        full_path = self.skills_dir / file_path
        if not full_path.exists():
            return f"ERROR: Skill file not found at {full_path}"

        with open(full_path) as f:
            return f.read()

    @before_model
    def __call__(self, request, handler):
        """
        Before model call: Check for slash commands.

        If slash command found:
        1. Parse command and arguments
        2. Load specified skill directly
        3. Inject skill into system prompt
        4. Set metadata for model selector
        5. Set flag to skip semantic search
        6. Replace user message with prompt (minus command)
        """
        messages = request.get('messages', [])
        if not messages:
            return handler(request)

        # Get latest user message
        user_msg = messages[-1]
        if user_msg.get('role') != 'user':
            return handler(request)

        content = user_msg.get('content', '')
        if isinstance(content, list):
            # Handle complex content format
            content = ' '.join(
                block.get('text', '') for block in content
                if isinstance(block, dict) and block.get('type') == 'text'
            )

        # Parse command
        parsed = self._parse_command(content)
        if not parsed:
            # No slash command, continue to semantic search
            return handler(request)

        # Look up skill
        skill_name = parsed['command']
        if skill_name not in self.skill_index:
            # Unknown command - add error message and continue
            error_msg = f"Unknown command: /{skill_name}. Available: {', '.join(self.skill_index.keys())}"
            messages[-1]['content'] = f"{parsed['original']}\n\n[System: {error_msg}]"
            return handler(request)

        # Load skill
        skill = self.skill_index[skill_name]
        skill_content = self._load_skill_content(skill['file'])

        # Build skill metadata
        selected_skill = {
            'name': skill['name'],
            'content': skill_content,
            'score': 1.0,  # Perfect match (explicit)
            'model_required': skill.get('model_required'),
            'sub_skills': skill.get('sub_skills', {}),
            'tools_required': skill.get('tools_required', []),
            'explicit': True,  # Explicitly invoked
            'arguments': parsed['arguments'],  # Pass arguments
        }

        # Inject arguments into skill content if provided
        if parsed['arguments']:
            args_text = "\n\n## Command Arguments\n\n"
            for key, value in parsed['arguments'].items():
                args_text += f"- **{key}**: {value}\n"
            skill_content = args_text + skill_content
            selected_skill['content'] = skill_content

        # Inject skill into system prompt
        skill_injection = f"# Explicitly Invoked Skill: {skill['name']}\n\n"
        skill_injection += f"(Invoked via /{skill_name} command)\n\n"
        skill_injection += skill_content

        if messages and messages[0].get('role') == 'system':
            messages[0]['content'] += "\n\n" + skill_injection
        else:
            messages.insert(0, {
                'role': 'system',
                'content': skill_injection
            })

        # Replace user message content (remove command, keep prompt)
        if parsed['prompt']:
            messages[-1]['content'] = parsed['prompt']
        else:
            messages[-1]['content'] = f"Execute the {skill['name']} skill."

        request['messages'] = messages

        # Set metadata for model selector and to skip semantic search
        if 'state' not in request:
            request['state'] = {}

        request['state']['selected_skills'] = [selected_skill]
        request['state']['explicit_command'] = True  # Flag to skip semantic search
        request['state']['command_arguments'] = parsed['arguments']

        return handler(request)
```

### 2. Update `SkillSelectorMiddleware` to Skip on Explicit Commands

In `roscoe/skill_middleware.py`, modify `modify_model_request`:

```python
def modify_model_request(self, model_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Before model call: Select relevant skills and inject into prompt.

    SKIPS if slash command already loaded skill explicitly.
    """
    # Check if slash command middleware already loaded a skill
    if model_request.get('state', {}).get('explicit_command'):
        # Skill already loaded explicitly, skip semantic search
        return model_request

    # Otherwise, proceed with semantic search
    messages = model_request.get('messages', [])
    if not messages:
        return model_request

    # ... rest of existing code ...
```

### 3. Update `agent.py` Middleware List

```python
from slash_command_middleware import SlashCommandMiddleware

personal_assistant_agent = create_deep_agent(
    system_prompt=minimal_personal_assistant_prompt,
    subagents=[],
    model=agent_llm,
    backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),
    tools=[shell_tool],
    middleware=[
        # 1. Slash commands - explicit skill invocation (runs first)
        SlashCommandMiddleware(skills_dir=f"{workspace_dir}/skills"),

        # 2. Skill selector - semantic search (skipped if explicit command)
        SkillSelectorMiddleware(
            skills_dir=f"{workspace_dir}/skills",
            max_skills=1,
            similarity_threshold=0.3
        ),

        # 3. Model selector - dynamic model switching (always runs)
        model_selector_middleware,
    ]
).with_config({"recursion_limit": 1000})
```

## Usage Examples

### Basic Skill Invocation

```
User: /medical-records
→ Directly loads medical-records-analysis skill
→ Skips semantic search
→ Uses skill's model requirement (sonnet)
```

### With Natural Language Prompt

```
User: /research Kentucky statute of limitations for personal injury claims
→ Loads legal-research skill
→ Passes "Kentucky statute of limitations..." as prompt
→ Uses sonnet model
```

### With Arguments

```
User: /medical-records case=mo_alif phases=1,2,3
→ Loads medical-records-analysis skill
→ Injects arguments into skill context
→ Skill sees: case=mo_alif, phases=1,2,3
```

### Sub-Skill Direct Invocation

```
User: /fact-investigation
→ Loads fact-investigation sub-skill directly
→ Uses gemini-3-pro model (per sub-skill requirement)
→ Bypasses parent skill orchestration
```

### Aliases

```
User: /med → /medical-records
User: /r Kentucky statutes → /research Kentucky statutes
User: /fact → /fact-investigation
```

## Advanced Features

### Help Command

Add special `/help` command handling:

```python
if parsed['command'] == 'help':
    if parsed['prompt']:
        # /help skill-name - show skill details
        skill_name = parsed['prompt'].strip()
        if skill_name in self.skill_index:
            skill = self.skill_index[skill_name]
            help_text = f"# {skill['name']}\n\n{skill['description']}\n\n"
            help_text += f"**Model:** {skill.get('model_required', 'default')}\n"
            help_text += f"**File:** {skill['file']}\n"
            # Inject as system message
        else:
            help_text = f"Unknown skill: {skill_name}"
    else:
        # /help - list all skills
        help_text = "## Available Skills\n\n"
        for name, skill in self.skill_index.items():
            help_text += f"- **/{name}**: {skill.get('description', '')}\n"

    # Inject help text, don't call actual skill
```

### Model Override

Allow temporary model override:

```
User: /medical-records model=haiku
→ Loads skill but overrides model requirement to haiku
```

Implementation:
```python
if 'model' in parsed['arguments']:
    selected_skill['model_required'] = parsed['arguments']['model']
```

### Skill Composition (Future)

Chain multiple skills:

```
User: /research topic | /summary-writing format=bullets
→ Execute research skill
→ Pass output to summary-writing skill
→ Return formatted summary
```

## Benefits

### 1. Explicit Control
- No ambiguity when you know what you want
- Deterministic skill selection
- Faster execution (no semantic search)

### 2. Power User Experience
- Familiar slash command interface (Discord, Slack, etc.)
- Quick access to frequently-used skills
- Autocomplete-friendly syntax

### 3. Debugging & Testing
- Test specific skills easily
- Isolate skill behavior
- Pass test parameters via arguments

### 4. Argument Passing
- Direct parameter passing to skills
- Override default behavior
- Conditional skill execution

### 5. Composable
- Foundation for skill chaining
- Skill pipelines
- Macro commands

## Testing Strategy

### Unit Tests

```python
# Test command parsing
def test_parse_basic_command():
    middleware = SlashCommandMiddleware(skills_dir)
    parsed = middleware._parse_command("/medical-records")
    assert parsed['command'] == 'medical-records-analysis'
    assert parsed['arguments'] == {}
    assert parsed['prompt'] == ""

def test_parse_command_with_args():
    parsed = middleware._parse_command("/med case=mo_alif phases=1,2,3")
    assert parsed['command'] == 'medical-records-analysis'
    assert parsed['arguments'] == {'case': 'mo_alif', 'phases': '1,2,3'}

def test_parse_command_with_prompt():
    parsed = middleware._parse_command("/research Kentucky statutes")
    assert parsed['command'] == 'legal-research'
    assert parsed['prompt'] == "Kentucky statutes"
```

### Integration Tests

```python
# Test with agent
def test_slash_command_loads_skill():
    response = agent.invoke("/medical-records")
    # Verify skill was loaded
    # Verify semantic search was skipped
    # Verify correct model was used

def test_slash_command_with_args():
    response = agent.invoke("/medical-records case=mo_alif")
    # Verify arguments were passed to skill
```

### Manual Tests

1. **Basic invocation**: `/medical-records`
2. **With prompt**: `/research Kentucky statute limitations`
3. **With args**: `/medical-records case=mo_alif`
4. **Sub-skill**: `/fact-investigation`
5. **Alias**: `/med` (should work like `/medical-records`)
6. **Unknown command**: `/unknown-skill` (should error gracefully)
7. **Help**: `/help` and `/help medical-records`

## Edge Cases to Handle

### 1. Unknown Commands

```python
if skill_name not in self.skill_index:
    error_msg = f"Unknown command: /{skill_name}. Use /help for available commands."
    # Inject error, continue to semantic search as fallback
```

### 2. Malformed Arguments

```python
# Validate argument format
for key, value in parsed['arguments'].items():
    if not key.isidentifier():
        # Invalid argument name
        warnings.append(f"Invalid argument name: {key}")
```

### 3. Conflicting Models

```python
# User specifies model=haiku but skill requires gemini-3-pro
if 'model' in arguments and arguments['model'] != skill['model_required']:
    # Log warning or error
    logger.warning(f"Model override: {arguments['model']} (skill requires {skill['model_required']})")
```

### 4. Empty Commands

```python
if not parsed['command']:
    # Just "/" with nothing after - ignore
    return handler(request)
```

## Integration with Existing System

### No Breaking Changes

- Existing semantic search still works
- Users can choose: slash commands OR natural language
- Both methods coexist

### Graceful Fallback

```python
if skill_name not in self.skill_index:
    # Add error to message but DON'T block
    # Let semantic search try to handle it
    messages[-1]['content'] = f"{original_message}\n\n(Note: Unknown command /{skill_name})"
    # Skip setting explicit_command flag
    return handler(request)
```

### Skills Manifest Compatibility

No changes needed to `skills_manifest.json`. Middleware reads existing structure.

## Future Enhancements

### Skill Parameters in Manifest

Add `parameters` field to skills:

```json
{
  "name": "medical-records-analysis",
  "parameters": {
    "case": {"type": "string", "required": false},
    "phases": {"type": "array", "default": [1,2,3,4,5]},
    "output": {"type": "enum", "values": ["full", "brief"], "default": "full"}
  }
}
```

Validate arguments against parameters.

### Skill Chaining

```
/research topic | /summarize format=bullets | /save file=research.md
```

Parse pipe-separated commands, execute sequentially.

### Skill Macros

Define custom command sequences:

```json
{
  "macros": {
    "quick-med": "/medical-records phases=1,2,3 output=brief",
    "full-analysis": "/fact-investigation && /medical-records && /summary-writing"
  }
}
```

### Autocomplete Support

Export skill list for IDE/CLI autocomplete:

```bash
roscoe skills list --format=bash-completion > ~/.roscoe-completion
```

## Dependencies

**New:**
- None (uses standard library only)

**Existing:**
- `langchain.agents.middleware.before_model`
- Skills manifest structure (unchanged)

## Backward Compatibility

✅ **Fully backward compatible**
- Existing natural language prompts work unchanged
- Semantic search unaffected for non-slash messages
- No changes to skills manifest required
- Optional feature - can be disabled by removing from middleware list

## Performance Impact

- **Slash commands**: Faster (skip semantic search ~50-100ms)
- **Natural language**: Same as before
- **Memory**: Negligible (skill index loaded once at startup)

## Security Considerations

### Command Injection

```python
# Sanitize command name
if not re.match(r'^[a-z0-9-]+$', command):
    return None  # Invalid command format
```

### Argument Injection

```python
# Validate argument values
for key, value in arguments.items():
    if len(value) > 1000:  # Reasonable limit
        value = value[:1000]
```

### Path Traversal

```python
# Ensure skill file is within skills directory
skill_path = self.skills_dir / skill['file']
if not skill_path.resolve().is_relative_to(self.skills_dir.resolve()):
    raise SecurityError("Skill file outside skills directory")
```

## Documentation Updates Needed

### CLAUDE.md

Add section:

```markdown
## Slash Commands (Optional)

For explicit skill invocation, use slash commands:

`/skill-name [arguments] [prompt]`

Examples:
- `/medical-records` - Invoke medical records analysis
- `/research Kentucky statutes` - Research with prompt
- `/med case=mo_alif` - With arguments

See `documents/SLASH_COMMAND_MIDDLEWARE_DESIGN.md` for details.
```

### User Guide

Create `docs/SLASH_COMMANDS.md` with:
- Available commands list
- Syntax guide
- Examples
- Aliases reference

## Implementation Checklist

When ready to implement:

- [ ] Create `roscoe/slash_command_middleware.py`
- [ ] Implement `SlashCommandMiddleware` class
- [ ] Add `_parse_command()` method
- [ ] Add `_build_aliases()` method
- [ ] Implement `@before_model` decorator
- [ ] Update `SkillSelectorMiddleware.modify_model_request()` to check flag
- [ ] Add `SlashCommandMiddleware` to `agent.py` middleware list
- [ ] Write unit tests for command parsing
- [ ] Write integration tests with agent
- [ ] Manual testing with real skills
- [ ] Update CLAUDE.md documentation
- [ ] Create user guide
- [ ] Commit and deploy

---

## Status

**Design Complete**: Ready for implementation
**Testing Required**: After implementation
**Priority**: Low (enhancement, not critical)

**Dependencies**: Current dynamic skills architecture must be tested and working first.

**Estimated Implementation Time**: 1-2 hours
**Estimated Testing Time**: 30-60 minutes
