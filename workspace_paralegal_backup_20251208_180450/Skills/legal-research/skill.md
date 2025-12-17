**IMPORTANT: Before proceeding with this skill, you MUST announce to the user that you are using the "Legal Research" skill.**

Example announcement: "I'm activating the Legal Research skill to help find relevant information using internet search capabilities."

---

# Legal Research Skill

## When to Use
Use this skill when researching legal topics, statutes, case law, expert witnesses, medical literature, or general information. Ideal for gathering current information from the internet.

## Overview
This skill delegates research tasks to the general-purpose sub-agent equipped with internet search capabilities. The sub-agent performs comprehensive web searches and synthesizes findings into organized summaries with citations.

## Workflow

### 1. Identify Research Topics
Break down the user's request into specific, focused research questions:
- **Legal Research**: Statutes, case law, legal precedents, court procedures
- **Expert Witnesses**: Qualifications, publications, testimony history
- **Medical Literature**: Current research, treatment standards, causation studies
- **General Information**: Facts, definitions, current events, news

### 2. Delegate to General-Purpose Sub-Agent
For each research topic, spawn the general-purpose sub-agent with specific instructions:

```
task(
  name="general-purpose",
  task="Research [specific topic] using the internet search tool.

  Tool location: /Tools/internet_search.py

  Execute: python /Tools/internet_search.py \"your search query\" --pretty

  Conduct thorough research:
  1. Start with a broad query to understand the topic
  2. Follow up with 2-3 focused queries for depth
  3. Search for recent (2024-2025) information when relevant
  4. Gather specific details: names, dates, numbers, quotes

  Synthesize findings into a comprehensive summary with:
  - Key findings (bullet points)
  - Important details and specifics
  - Source citations (URLs)
  - Relevant dates and context

  Keep your final response concise (under 500 words) to maintain clean context."
)
```

### 3. Tool Execution Pattern

The sub-agent should execute internet search like this:

```bash
# Basic search
python /Tools/internet_search.py "Kentucky personal injury statute of limitations"

# With more results
python /Tools/internet_search.py "whiplash medical causation research" --max-results 10

# News-focused search
python /Tools/internet_search.py "recent expert witness standards 2025" --topic news --pretty

# With full content for detailed analysis
python /Tools/internet_search.py "medical malpractice case law" --include-content --pretty
```

### 4. For Multiple Independent Topics

If user requests research on multiple independent topics, spawn multiple sub-agents **in parallel**:

```python
# DON'T do sequentially - spawn all at once
task(name="general-purpose", task="Research Kentucky PI statute...")
task(name="general-purpose", task="Research whiplash causation...")
task(name="general-purpose", task="Research expert witness qualifications...")
```

This is much faster than sequential research.

### 5. Synthesis

After sub-agent(s) complete:
1. Read their research summaries
2. Compile findings if multiple topics researched
3. Present organized results to user with:
   - Summary of key findings
   - Specific details and data points
   - All source citations
   - Actionable recommendations if applicable

## Tools Required

**Primary Tool:**
- `/Tools/internet_search.py` - Standalone Tavily internet search script

**Tool Usage:**
```bash
python /Tools/internet_search.py "query" [options]

Options:
  --max-results N         Number of results (default: 5)
  --topic TYPE           Search category: general, news, finance
  --include-content      Include full page content
  --pretty              Pretty-print JSON output
```

## Sub-Agent Instructions

The general-purpose sub-agent should be instructed to:
1. **Use the tool directly** via bash: `python /Tools/internet_search.py "query"`
2. **Search iteratively**: Start broad, then focus on specifics
3. **Gather details**: Names, dates, numbers, quotes, specific facts
4. **Cite sources**: Always include URLs for all claims
5. **Stay concise**: Final summary under 500 words
6. **Return only summary**: Don't include raw search results, just synthesized findings

## Model Required

**sonnet** (Claude Sonnet 4.5)
- Complex synthesis of multiple sources
- Judgment about relevance and credibility
- Legal/medical domain knowledge for context
- Clear writing for attorney-ready summaries

## Output Format

```markdown
# Research Summary: [Topic]

## Key Findings
- Finding 1 with specific details
- Finding 2 with numbers/dates/names
- Finding 3 with relevant context

## Detailed Analysis
[2-3 paragraphs synthesizing the research]

## Sources
1. [Title] - [URL]
2. [Title] - [URL]
3. [Title] - [URL]

## Recommendations
- Actionable next steps based on findings
- Areas requiring additional research
- Strategic considerations
```

## Common Use Cases

**Legal Research:**
- "Research Kentucky statute of limitations for personal injury claims"
- "Find recent case law on medical malpractice in auto accidents"
- "What are the requirements for expert witness testimony in Ohio?"

**Expert Witness Research:**
- "Research Dr. John Smith's qualifications as orthopedic expert witness"
- "Find publications by Dr. Jane Doe on whiplash causation"
- "What is Dr. Smith's testimony history and success rate?"

**Medical Literature:**
- "Current medical research on chronic pain from rear-end collisions"
- "Standard treatment protocols for lumbar strain injuries"
- "Evidence for causation of PTSD from traumatic accidents"

**General Information:**
- "Average settlement amounts for soft tissue injuries in 2024"
- "Current medical costs for spinal fusion surgery"
- "Vehicle safety ratings and crash test data for 2023 Honda Accord"

## Best Practices

1. **Be Specific**: Focused queries get better results than vague requests
2. **Use Multiple Searches**: 3-5 targeted searches better than one broad search
3. **Recent Information**: Add "2024" or "2025" when currency matters
4. **Verify Critical Facts**: Cross-reference important claims across sources
5. **Maintain Citations**: Every factual claim needs a source URL
6. **Context Efficiency**: Sub-agent returns summary only, not raw data
7. **Parallel Processing**: Multiple independent topics = multiple parallel sub-agents

## Notes

- Sub-agent has access to the internet search tool via bash execution
- Tool outputs JSON - sub-agent should parse and synthesize, not return raw JSON
- For huge result sets, sub-agent can grep/filter before reading
- Keep sub-agent's final response concise to avoid context bloat
- Main agent compiles results if multiple sub-agents used
