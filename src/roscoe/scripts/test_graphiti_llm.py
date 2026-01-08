#!/usr/bin/env python3
"""Test Graphiti LLM client for entity extraction."""

import asyncio
import sys
sys.path.insert(0, "/deps/Roscoe/src")

async def test_llm():
    from roscoe.core.graphiti_client import get_graphiti
    
    print("Getting graphiti instance...")
    g = await get_graphiti()
    
    llm_type = type(g.llm_client).__name__
    print(f"LLM Client: {llm_type}")
    
    if hasattr(g.llm_client, 'config'):
        print(f"Model: {g.llm_client.config.model}")
    
    # Test a simple extraction
    from graphiti_core.prompts import prompt_library
    
    context = {
        "episode_content": "Alice called Bob at 555-1234. They discussed the project.",
        "episode_timestamp": "2024-01-01T12:00:00",
        "previous_episodes": [],
        "custom_prompt": "",
        "entity_types": [{"entity_type_id": 0, "entity_type_name": "Entity", "entity_type_description": "Default entity"}],
        "source_description": "test",
    }
    
    prompt = prompt_library.extract_nodes.extract_text(context)
    print(f"\nPrompt length: {len(prompt)} chars")
    print(f"Prompt preview:\n{prompt[:800]}...")
    
    # Try to generate response
    print("\n\nCalling LLM for entity extraction...")
    try:
        from graphiti_core.prompts.extract_nodes import ExtractedEntities
        response = await g.llm_client.generate_response(
            prompt,
            response_model=ExtractedEntities,
            group_id="test",
            prompt_name="test",
        )
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        
        # Parse the response
        if isinstance(response, dict):
            entities = response.get("extracted_entities", [])
            print(f"\nExtracted {len(entities)} entities:")
            for e in entities:
                print(f"  - {e}")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm())
