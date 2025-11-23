"""
Skill selection and model switching middleware for Roscoe agent.

This module implements dynamic skill discovery and model optimization:

1. SkillSelectorMiddleware: Semantically matches user requests to relevant skills
   - Embeds skill descriptions using sentence-transformers
   - Computes cosine similarity between user query and skills
   - Injects top-matching skills into system prompt
   - Sets skill metadata in request state for model selector

2. model_selector_middleware: Dynamically switches models based on skill requirements
   - Reads skill metadata from request state
   - Overrides model to match skill's optimal model (Gemini/Sonnet/Haiku)
   - Ensures general-purpose sub-agent inherits the correct model

This architecture enables:
- Zero hardcoded sub-agents (uses only built-in general-purpose)
- Unlimited skills without code changes
- Token-efficient context loading
- Automatic model optimization per task
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
import json
from sentence_transformers import SentenceTransformer, util
from langchain.agents.middleware import Middleware, wrap_model_call


class SkillSelectorMiddleware(Middleware):
    """
    Semantic skill selection middleware.

    Runs before model call to inject relevant skills into the system prompt.
    Uses sentence-transformers for local, fast semantic search.

    Args:
        skills_dir: Path to Skills directory containing skills_manifest.json
        max_skills: Maximum number of skills to load per request (default: 1)
        similarity_threshold: Minimum cosine similarity score (0-1) to load skill (default: 0.3)
    """

    def __init__(
        self,
        skills_dir: str,
        max_skills: int = 1,
        similarity_threshold: float = 0.3
    ):
        self.skills_dir = Path(skills_dir)
        self.max_skills = max_skills
        self.threshold = similarity_threshold

        # Initialize lightweight embedding model (runs locally, no API calls)
        # all-MiniLM-L6-v2: 384 dimensions, 80MB, optimized for semantic search
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load skills manifest and pre-compute embeddings
        self.manifest = self._load_manifest()
        self.skill_embeddings = self._embed_skills()

    def _load_manifest(self) -> Dict:
        """Load skills manifest from JSON file"""
        manifest_path = self.skills_dir / "skills_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"Skills manifest not found at {manifest_path}. "
                f"Create {self.skills_dir}/skills_manifest.json with skill definitions."
            )

        with open(manifest_path) as f:
            return json.load(f)

    def _embed_skills(self):
        """
        Pre-compute embeddings for all skill descriptions.

        Combines description + triggers for richer semantic matching.
        Embeddings are cached to avoid recomputation on each request.
        """
        skill_texts = []
        for skill in self.manifest['skills']:
            # Combine description and triggers for better matching
            desc = skill['description']
            triggers = ' '.join(skill.get('triggers', []))
            text = f"{desc} {triggers}"
            skill_texts.append(text)

        return self.model.encode(skill_texts, convert_to_tensor=True)

    def modify_model_request(self, model_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Before model call: Select relevant skills and inject into prompt.

        1. Extract latest user message
        2. Compute semantic similarity with all skills
        3. Select top-k skills above threshold
        4. Load skill content from markdown files
        5. Inject into system message
        6. Store skill metadata in state for model selector

        Args:
            model_request: Request dict with messages, state, etc.

        Returns:
            Modified request with skills injected into system prompt
        """
        messages = model_request.get('messages', [])
        if not messages:
            return model_request

        # Get latest user message
        user_query = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                # Handle string or list content
                if isinstance(content, str):
                    user_query = content
                elif isinstance(content, list):
                    # Extract text from content blocks
                    user_query = ' '.join(
                        block.get('text', '') for block in content
                        if isinstance(block, dict) and block.get('type') == 'text'
                    )
                break

        if not user_query:
            return model_request

        # Semantic search: encode query and compute cosine similarity
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, self.skill_embeddings)[0]

        # Get top-k skills above threshold
        top_indices = scores.argsort(descending=True)[:self.max_skills]

        selected_skills = []
        for idx in top_indices:
            score = scores[idx].item()
            if score > self.threshold:
                skill = self.manifest['skills'][idx]
                skill_content = self._load_skill_file(skill['file'])
                selected_skills.append({
                    'name': skill['name'],
                    'content': skill_content,
                    'score': score,
                    'model_required': skill.get('model_required'),
                    'sub_skills': skill.get('sub_skills', {}),
                    'tools_required': skill.get('tools_required', [])
                })

        # Inject skills into system message if any selected
        if selected_skills:
            skill_text = self._format_skills_for_injection(selected_skills)

            # Add or append to system message
            if messages and messages[0].get('role') == 'system':
                messages[0]['content'] += "\n\n" + skill_text
            else:
                messages.insert(0, {
                    'role': 'system',
                    'content': skill_text
                })

            model_request['messages'] = messages

            # Store skill metadata in state for model selector middleware
            if 'state' not in model_request:
                model_request['state'] = {}
            model_request['state']['selected_skills'] = selected_skills

        return model_request

    def _load_skill_file(self, file_path: str) -> str:
        """
        Load skill markdown content from file.

        Args:
            file_path: Relative path from skills_dir (e.g., "medical-records-analysis/skill.md")

        Returns:
            Skill content as string
        """
        full_path = self.skills_dir / file_path
        if not full_path.exists():
            return f"ERROR: Skill file not found at {full_path}"

        with open(full_path) as f:
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


@wrap_model_call
def model_selector_middleware(request, handler):
    """
    Dynamically switch model based on skill requirements.

    This middleware runs AFTER SkillSelectorMiddleware, reading skill metadata
    from request.state and overriding the model if the skill specifies a
    model requirement.

    Model Strategy (Accuracy > Cost for POC):
    - gemini-3-pro: Multimodal analysis, code execution, PDF processing
    - sonnet: Complex reasoning, medical analysis, synthesis (DEFAULT)
    - haiku: Only simple, high-volume tasks (listing, categorizing)

    The general-purpose sub-agent inherits whatever model is set here.

    Args:
        request: Model request with state containing selected_skills
        handler: Model invocation handler

    Returns:
        Response from handler with potentially overridden model
    """
    from .models import agent_llm, fact_investigator_llm, medical_sub_agent_llm

    # Check if skills were selected by SkillSelectorMiddleware
    selected_skills = request.state.get('selected_skills', [])

    if not selected_skills:
        # No skill selected, use default model (Sonnet)
        return handler(request)

    # Get model requirement from first selected skill
    skill = selected_skills[0]
    model_required = skill.get('model_required')

    # Map model requirements to actual LangChain model instances
    model_map = {
        'gemini-3-pro': fact_investigator_llm,  # Gemini 3 Pro with code execution
        'sonnet': agent_llm,                    # Claude Sonnet 4.5 (default)
        'haiku': medical_sub_agent_llm          # Claude Haiku 4.5 (simple tasks only)
    }

    if model_required and model_required in model_map:
        model = model_map[model_required]
        # Override model for this request
        # This affects BOTH main agent AND any spawned general-purpose sub-agents
        return handler(request.override(model=model))

    # Default: use agent_llm (Sonnet 4.5)
    return handler(request)
