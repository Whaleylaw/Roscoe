# CourtListener Legal Research Skill

## When to Use This Skill

Use when conducting legal research for:
- **Motion & Brief Writing**: Finding precedent and legal support for arguments
- **Case Law Research**: Searching opinions by keywords, statutes, or legal issues
- **Citation Network Analysis**: Finding cases that cite key precedents (Shepardizing)
- **Docket Monitoring**: Tracking your cases, filings, and upcoming court dates
- **Comprehensive Legal Research**: Building thorough research around specific legal issues

## Available Tools

You have access to 6 CourtListener tools in `/Tools/`:

### Research Tools
1. **search_case_law.py** - Search opinions by keyword, court, date, precedential status
2. **explore_citations.py** - Navigate citation networks (citing/cited cases)
3. **get_opinion_full_text.py** - Retrieve complete opinion text

### Docket Monitoring Tools
4. **find_my_cases.py** - Find all cases where attorney is listed
5. **get_docket_details.py** - Get full docket sheet with all filings
6. **monitor_upcoming_dates.py** - Track upcoming hearings and deadlines

## Kentucky Court IDs

When searching, use these court codes:
- **ky** - Kentucky Supreme Court
- **kyctapp** - Kentucky Court of Appeals
- **ked** - U.S. District Court, Eastern District of Kentucky
- **kwd** - U.S. District Court, Western District of Kentucky
- **ca6** - U.S. Court of Appeals, Sixth Circuit

## Typical Research Workflows

### Workflow 1: Motion/Brief Research

When user asks: *"I need to research [legal issue] for a brief"*

**Step 1: Initial Search**
```bash
python /Tools/search_case_law.py "[legal issue keywords]" --courts ky,kyctapp,ked,kwd,ca6 --precedential --limit 20 --json
```

**Step 2: Analyze Results**
- Review case names, courts, dates, citations
- Identify most relevant opinions
- Note opinion IDs for further analysis

**Step 3: Get Full Text of Key Cases**
```bash
python /Tools/get_opinion_full_text.py [OPINION_ID] --format plain --save /Reports/opinion_[case_name].txt
```

**Step 4: Explore Citation Network**
```bash
python /Tools/explore_citations.py [CLUSTER_ID] --depth 2 --limit 50 --json
```

**Step 5: Synthesize Research**
- Read full opinions saved to `/Reports/`
- Create comprehensive research memo
- List all relevant cases with citations
- Summarize holdings and applications

**Output Location**: Save research memo to `/Reports/legal_research_[topic].md`

### Workflow 2: Case Law Precedent Research

When user asks: *"Find cases on [legal doctrine] in Kentucky"*

**Step 1: Targeted Search**
```bash
python /Tools/search_case_law.py "[legal doctrine]" --courts ky,kyctapp --after 2010-01-01 --precedential --order citeCount --json
```

**Step 2: Sort by Authority**
- Prioritize KY Supreme Court over Court of Appeals
- Consider citation count (highly cited = influential)
- Check date (more recent = current law)

**Step 3: Deep Dive on Lead Case**
```bash
# Get full text of most authoritative case
python /Tools/get_opinion_full_text.py [OPINION_ID] --json

# Find cases citing this precedent
python /Tools/explore_citations.py [CLUSTER_ID] --depth 1 --limit 100 --json
```

**Step 4: Analysis**
- How has precedent been applied?
- Any distinguishing cases?
- Current validity and scope?

### Workflow 3: Citation Network Analysis (Shepardizing)

When user asks: *"What cases cite [case name]?"*

**Step 1: Find the Case**
```bash
python /Tools/explore_citations.py --citation "[123 S.W.3d 456]" --json
```

**Step 2: Analyze Citing Cases**
- Review all cases citing this precedent
- Identify positive vs. negative treatment
- Check if cited for relevant holding

**Step 3: Build Citation Tree**
```bash
# Explore second-level citations
python /Tools/explore_citations.py [CLUSTER_ID] --depth 2 --limit 100 --json
```

**Step 4: Document Findings**
- Create citation network diagram (text/markdown)
- Note key cases in the network
- Identify trends in how precedent is used

### Workflow 4: Docket Monitoring for Attorney

When user asks: *"Show me all my cases in federal court"*

**Step 1: Find All Cases**
```bash
python /Tools/find_my_cases.py "[Attorney Name]" --federal --status Open --json
```

**Step 2: Get Upcoming Dates**
```bash
python /Tools/monitor_upcoming_dates.py --attorney "[Attorney Name]" --courts ked,kwd --days 30 --calendar
```

**Step 3: Review Specific Dockets**
```bash
# For each important case:
python /Tools/get_docket_details.py [DOCKET_ID] --json
```

**Step 4: Create Calendar Report**
- List all upcoming hearings
- Note filing deadlines
- Flag urgent matters
- Save to `/Reports/court_calendar_[date].md`

### Workflow 5: Case-Specific Docket Review

When user asks: *"Get me the docket sheet for case [X]"*

**Step 1: Get Full Docket**
```bash
python /Tools/get_docket_details.py [DOCKET_ID] --json
```

**Step 2: Extract Key Information**
- All parties and attorneys
- Judge assignments
- All filings with dates
- Upcoming dates

**Step 3: Timeline Analysis**
- Create chronological timeline of filings
- Identify significant events
- Note any procedural issues

**Output**: Save complete docket summary to `/Reports/docket_[case_name].md`

## Best Practices

### Court Selection Strategy

For Kentucky personal injury research:
1. **Always search KY Supreme Court first** (ky) - binding authority
2. **Then KY Court of Appeals** (kyctapp) - persuasive authority
3. **Include federal if relevant** (ked, kwd, ca6) - especially for federal questions

### Precedential Status

- Use `--precedential` flag for published opinions (binding)
- Unpublished opinions are persuasive only (use sparingly)

### Date Ranges

- Recent cases: `--after 2020-01-01`
- Historical research: No date limit
- Check if older cases still valid (explore citations to see if overruled)

### Citation Depth

- **Depth 1**: Immediate citations (faster, usually sufficient)
- **Depth 2**: Second-level network (comprehensive but slower)

### Saving Research

- **Full opinions**: Save to `/Reports/opinion_[case_name].txt`
- **Research memos**: Save to `/Reports/legal_research_[topic].md`
- **Docket sheets**: Save to `/Reports/docket_[case_name].md`
- **Citation networks**: Save JSON to `/Reports/citations_[case_name].json`

## Output Format Requirements

When completing legal research, provide:

1. **Executive Summary**
   - Key holdings and takeaways
   - Most authoritative cases found
   - Recommended citations for brief

2. **Detailed Findings**
   - Full case citations (e.g., *Smith v. Jones*, 123 S.W.3d 456 (Ky. 2020))
   - Relevant quotes from opinions
   - Court and date for each case

3. **Citation Network** (if applicable)
   - Cases citing the key precedent
   - Cases cited by the key precedent
   - Treatment analysis

4. **Saved Files**
   - List all files saved to `/Reports/`
   - Provide file paths for user reference

## Tool Limitations to Note

1. **State Circuit Court Coverage**: CourtListener has excellent coverage of KY Supreme Court and Court of Appeals, but **limited coverage of circuit courts** (trial level). Most circuit court opinions are not published.

2. **Real-Time Calendars**: Docket monitoring extracts dates from filed docket entries. May not capture all court calendar events if not formally docketed.

3. **Federal Focus**: Best docket coverage for federal courts (PACER integration). State court dockets are more limited.

4. **Attorney Search**: Finding cases by attorney works best in federal court (RECAP database). State court attorney search is less reliable.

## Error Handling

If tool returns error:
- Check API key is set in environment
- Verify court code is correct
- Try broader search terms
- Check if opinion/docket ID is valid
- Fall back to alternative search methods

## Example Research Session

**User**: "I need to research the statute of limitations for personal injury in Kentucky"

**Your Response**:

I'll research Kentucky statute of limitations for personal injury cases using CourtListener.

**Step 1**: Searching Kentucky case law...
```bash
python /Tools/search_case_law.py "statute of limitations personal injury" --courts ky,kyctapp --precedential --order -dateFiled --limit 30 --json
```

Found 28 relevant cases. Key cases:
- *[Case Name]*, [Citation] (Ky. [Year]) - [Brief description]
- *[Case Name]*, [Citation] (Ky. Ct. App. [Year]) - [Brief description]

**Step 2**: Getting full text of most relevant case...
```bash
python /Tools/get_opinion_full_text.py [OPINION_ID] --save /Reports/opinion_statute_limitations.txt
```

**Step 3**: Exploring citation network...
```bash
python /Tools/explore_citations.py [CLUSTER_ID] --depth 1 --limit 50 --json
```

Found 15 cases citing this precedent in the last 5 years, all applying the same rule.

**Research Summary**:

[Your comprehensive analysis with citations, quotes, and holdings]

**Files Saved**:
- `/Reports/opinion_statute_limitations.txt` - Full text of lead case
- `/Reports/legal_research_statute_limitations.md` - This research memo

Ready to discuss or refine the research further.

---

## Integration with Other Skills

This skill works well with:
- **Internet search** (`/Tools/internet_search.py`) - For secondary sources, law review articles
- **Document processing** - Saving and organizing research findings
- **Case management** - Linking research to specific case files

## Model Requirements

**Recommended Model**: Claude Sonnet 4.5 (default)
- Complex legal reasoning required
- Multi-step research workflows
- Citation analysis and synthesis

This skill does NOT require Gemini (no multimedia) or Haiku (too complex).
