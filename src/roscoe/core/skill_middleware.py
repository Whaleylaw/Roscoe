"""
Skill selection middleware for Roscoe agent.

This module implements dynamic skill discovery:

SkillSelectorMiddleware: Semantically matches user requests to relevant skills
- Scans skills directory for SKILL.md files (Anthropic Agent Skills Spec)
- Parses YAML frontmatter to extract name and description
- Embeds skill descriptions using sentence-transformers
- Computes cosine similarity between user query and skills
- Injects top-matching skills into system prompt
- Sets skill metadata in request state

This architecture enables:
- Zero hardcoded sub-agents (uses only built-in general-purpose)
- Unlimited skills without code changes
- Token-efficient context loading
- Self-contained skill folders (per Anthropic spec)
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
import logging
import asyncio
import re
import yaml
from sentence_transformers import SentenceTransformer, util
from langchain.agents.middleware import AgentMiddleware, wrap_model_call

# Configure logger
logger = logging.getLogger(__name__)


def parse_yaml_frontmatter(content: str) -> tuple[Dict, str]:
    """
    Parse YAML frontmatter from a markdown file.
    
    Args:
        content: Full file content
        
    Returns:
        Tuple of (frontmatter_dict, remaining_content)
    """
    # Match YAML frontmatter between --- markers
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2)
            return frontmatter or {}, body
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
            return {}, content
    
    return {}, content


class SkillSelectorMiddleware(AgentMiddleware):
    """
    Semantic skill selection middleware.

    Runs before model call to inject relevant skills into the system prompt.
    Uses sentence-transformers for local, fast semantic search.

    Skills are discovered by scanning the skills directory for SKILL.md files
    following the Anthropic Agent Skills Spec:
    - Each skill is a folder containing SKILL.md
    - SKILL.md has YAML frontmatter with 'name' and 'description'
    - The 'description' is used for semantic matching

    Args:
        skills_dir: Path to Skills directory containing skill folders
        max_skills: Maximum number of skills to load per request (default: 1)
        similarity_threshold: Minimum cosine similarity score (0-1) to load skill (default: 0.3)
    """

    name: str = "skill_selector"  # Unique name required by LangChain middleware framework
    tools: list = []  # Required by AgentMiddleware base class

    def __init__(
        self,
        skills_dir: str,
        manifest_path: Optional[str] = None,  # Deprecated, kept for backward compatibility
        max_skills: int = 1,
        similarity_threshold: float = 0.3
    ):
        self.skills_dir = Path(skills_dir)
        self.max_skills = max_skills
        self.threshold = similarity_threshold

        # Initialize lightweight embedding model (runs locally, no API calls)
        # all-MiniLM-L6-v2: 384 dimensions, 80MB, optimized for semantic search
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Scan skills directory and build manifest from SKILL.md files
        self.manifest = self._scan_and_build_manifest()
        self.skill_embeddings = self._embed_skills()

    def _scan_and_build_manifest(self) -> Dict:
        """
        Scan skills directory for SKILL.md files and build manifest from YAML frontmatter.
        
        This follows the Anthropic Agent Skills Spec:
        - Each skill is a folder containing SKILL.md
        - SKILL.md has YAML frontmatter with 'name' (required) and 'description' (required)
        - Folder name should match the 'name' in frontmatter
        
        Returns:
            Manifest dict with 'skills' list
        """
        skills = []
        
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return {"skills": []}
        
        # Scan for SKILL.md files in subdirectories
        for skill_folder in self.skills_dir.iterdir():
            if not skill_folder.is_dir():
                continue
            
            # Check for SKILL.md (case-insensitive for flexibility)
            skill_file = None
            for candidate in ['SKILL.md', 'skill.md', 'Skill.md']:
                candidate_path = skill_folder / candidate
                if candidate_path.exists():
                    skill_file = candidate_path
                    break
            
            if not skill_file:
                # Skip folders without SKILL.md
                continue
            
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = parse_yaml_frontmatter(content)
                
                # Extract required fields
                name = frontmatter.get('name', skill_folder.name)
                description = frontmatter.get('description', '')
                
                if not description:
                    logger.warning(f"Skill {name} has no description in YAML frontmatter")
                    continue
                
                # Warn if folder name doesn't match YAML name
                if name != skill_folder.name:
                    logger.warning(
                        f"Skill folder name '{skill_folder.name}' doesn't match "
                        f"YAML name '{name}'. Per spec, these should match."
                    )
                
                # Build skill entry
                skill_entry = {
                    'name': name,
                    'description': description,
                    'file': f"{skill_folder.name}/SKILL.md",
                    'folder': skill_folder.name,
                    # Optional fields from frontmatter
                    'license': frontmatter.get('license'),
                    'allowed_tools': frontmatter.get('allowed-tools', []),
                    'metadata': frontmatter.get('metadata', {}),
                    # Legacy fields (for backward compatibility with existing skills)
                    'triggers': frontmatter.get('triggers', []),
                    'model_required': frontmatter.get('model_required'),
                    'tools_required': frontmatter.get('tools_required', []),
                    'sub_skills': frontmatter.get('sub_skills', {}),
                }
                
                skills.append(skill_entry)
                logger.info(f"Loaded skill: {name} from {skill_folder.name}/SKILL.md")
                
            except Exception as e:
                logger.error(f"Error loading skill from {skill_folder}: {e}")
                continue
        
        logger.info(f"Loaded {len(skills)} skills from {self.skills_dir}")
        return {"skills": skills}

    def refresh_skills(self) -> int:
        """
        Rescan skills directory and rebuild manifest.
        
        Call this to pick up newly added skills mid-session.
        
        Returns:
            Number of skills loaded
        """
        logger.info("Refreshing skills manifest...")
        self.manifest = self._scan_and_build_manifest()
        self.skill_embeddings = self._embed_skills()
        return len(self.manifest['skills'])

    def get_skills_summary(self) -> str:
        """
        Get a summary of all available skills with their YAML descriptions.
        
        This is used by the list_skills tool to show what's available.
        
        Returns:
            Formatted string with all skills and descriptions
        """
        if not self.manifest['skills']:
            return "No skills available."
        
        lines = ["# Available Skills\n"]
        
        for skill in self.manifest['skills']:
            lines.append(f"## {skill['name']}")
            lines.append(f"**Description:** {skill['description']}")
            
            if skill.get('triggers'):
                lines.append(f"**Triggers:** {', '.join(skill['triggers'])}")
            
            if skill.get('model_required'):
                lines.append(f"**Model:** {skill['model_required']}")
            
            if skill.get('tools_required'):
                lines.append(f"**Tools:** {', '.join(skill['tools_required'])}")
            
            lines.append("")  # Blank line between skills
        
        return "\n".join(lines)

    def get_skill_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a skill by name.
        
        Args:
            name: Skill name to look up
            
        Returns:
            Skill dict or None if not found
        """
        for skill in self.manifest['skills']:
            if skill['name'] == name:
                return skill
        return None

    def _embed_skills(self):
        """
        Pre-compute embeddings for all skill descriptions.

        Combines description + triggers for richer semantic matching.
        Embeddings are cached to avoid recomputation on each request.
        """
        if not self.manifest['skills']:
            return None
            
        skill_texts = []
        for skill in self.manifest['skills']:
            # Combine description and triggers for better matching
            desc = skill['description']
            triggers = ' '.join(skill.get('triggers', []))
            text = f"{desc} {triggers}"
            skill_texts.append(text)

        return self.model.encode(skill_texts, convert_to_tensor=True)

    def _select_and_inject_skills(self, request):
        """
        Helper method: Select relevant skills and inject into prompt.

        1. Extract latest user message
        2. Compute semantic similarity with all skills
        3. Select top-k skills above threshold
        4. Load skill content from markdown files
        5. Inject into system message
        6. Store skill metadata in request state

        Args:
            request: AgentMiddleware request object

        Returns:
            Modified request with skills injected into system prompt
        """
        messages = list(request.messages)  # Create mutable copy
        if not messages:
            logger.error("[SKILL SELECTOR] No messages in request")
            return request

        if not self.manifest['skills'] or self.skill_embeddings is None:
            logger.warning("[SKILL SELECTOR] No skills loaded")
            return request

        logger.info(f"[SKILL SELECTOR] Processing {len(messages)} messages")

        # Get latest user message
        from langchain_core.messages import HumanMessage

        user_query = ""
        for i, msg in enumerate(reversed(messages)):
            # Check if this is a HumanMessage (user message)
            if isinstance(msg, HumanMessage):
                content = msg.content

                # Handle string or list content
                if isinstance(content, str):
                    user_query = content
                elif isinstance(content, list):
                    # Extract text from content blocks
                    user_query = ' '.join(
                        block.get('text', '') if isinstance(block, dict) else str(block)
                        for block in content
                        if block  # Skip empty blocks
                    )
                break

        if not user_query:
            logger.warning("[SKILL SELECTOR] No user query found - skipping skill selection")
            return request

        # Semantic search: encode query and compute cosine similarity
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.skill_embeddings)[0]

        # Log all scores for debugging
        logger.debug(f"[SKILL SELECTOR] Similarity scores:")
        for idx, skill in enumerate(self.manifest['skills']):
            score = scores[idx].item()
            logger.debug(f"  - {skill['name']}: {score:.3f} (threshold: {self.threshold})")

        # Get top-k skills above threshold
        top_indices = scores.argsort(descending=True)[:self.max_skills]

        selected_skills = []
        for idx in top_indices:
            score = scores[idx].item()
            if score > self.threshold:
                skill = self.manifest['skills'][idx]
                skill_content = self._load_skill_file(skill['file'])
                logger.info(f"[SKILL SELECTOR] ✅ Selected skill: {skill['name']} (score: {score:.3f})")
                selected_skills.append({
                    'name': skill['name'],
                    'content': skill_content,
                    'score': score,
                    'model_required': skill.get('model_required'),
                    'sub_skills': skill.get('sub_skills', {}),
                    'tools_required': skill.get('tools_required', [])
                })
            else:
                logger.debug(f"[SKILL SELECTOR] ❌ Skill below threshold: {self.manifest['skills'][idx]['name']} ({score:.3f} <= {self.threshold})")

        # Inject skills into system message if any selected
        if selected_skills:
            skill_text = self._format_skills_for_injection(selected_skills)

            # Add or append to system message
            from langchain_core.messages import SystemMessage
            if messages and getattr(messages[0], 'role', messages[0].get('role') if isinstance(messages[0], dict) else None) == 'system':
                # Append to existing system message
                existing_content = getattr(messages[0], 'content', messages[0].get('content', ''))
                messages[0] = SystemMessage(content=existing_content + "\n\n" + skill_text)
            else:
                # Insert new system message at beginning
                messages.insert(0, SystemMessage(content=skill_text))

            # Store skill metadata in request state
            state = dict(request.state) if request.state else {}
            state['selected_skills'] = selected_skills

            return request.override(messages=messages, state=state)

        return request

    def wrap_model_call(self, request, handler):
        """Synchronous model call wrapper - injects skills before calling model."""
        logger.info("="*60)
        logger.info("⚡ SKILL SELECTOR MIDDLEWARE EXECUTING (SYNC) ⚡")
        logger.info("="*60)
        modified_request = self._select_and_inject_skills(request)
        selected_skills = modified_request.state.get('selected_skills', []) if modified_request.state else []
        logger.info(f"Selected skills: {[s['name'] for s in selected_skills]}")
        return handler(modified_request)

    async def awrap_model_call(self, request, handler):
        """Asynchronous model call wrapper - injects skills before calling model."""
        logger.info("="*60)
        logger.info("⚡ SKILL SELECTOR MIDDLEWARE EXECUTING (ASYNC) ⚡")
        logger.info("="*60)
        # Run blocking file I/O in a thread to avoid blocking the event loop
        modified_request = await asyncio.to_thread(self._select_and_inject_skills, request)
        selected_skills = modified_request.state.get('selected_skills', []) if modified_request.state else []
        logger.info(f"Selected skills: {[s['name'] for s in selected_skills]}")
        return await handler(modified_request)

    def _load_skill_file(self, file_path: str) -> str:
        """
        Load skill markdown content from file.

        Args:
            file_path: Relative path from skills_dir (e.g., "pdf/SKILL.md")

        Returns:
            Skill content as string
        """
        full_path = self.skills_dir / file_path
        if not full_path.exists():
            # Try case-insensitive match
            folder = file_path.split('/')[0]
            for candidate in ['SKILL.md', 'skill.md', 'Skill.md']:
                alt_path = self.skills_dir / folder / candidate
                if alt_path.exists():
                    full_path = alt_path
                    break
            else:
                return f"ERROR: Skill file not found at {full_path}"

        with open(full_path, encoding='utf-8') as f:
            return f.read()

    def _format_skills_for_injection(self, skills: List[Dict]) -> str:
        """
        Format selected skills for system prompt injection.

        Args:
            skills: List of selected skill dicts with name, content, score, etc.

        Returns:
            Formatted markdown string for system prompt
        """
        formatted = "# Available Skills\n\n"
        formatted += "The following skills have been loaded for this task:\n\n"

        for skill in skills:
            formatted += f"## {skill['name']} (relevance: {skill['score']:.2f})\n\n"
            formatted += skill['content']
            formatted += "\n\n---\n\n"

        return formatted


# Singleton instance for tools to access
_middleware_instance: Optional[SkillSelectorMiddleware] = None


def get_middleware_instance() -> Optional[SkillSelectorMiddleware]:
    """Get the current middleware instance (set by agent at startup)."""
    return _middleware_instance


def set_middleware_instance(instance: SkillSelectorMiddleware):
    """Set the middleware instance (called by agent at startup)."""
    global _middleware_instance
    _middleware_instance = instance
