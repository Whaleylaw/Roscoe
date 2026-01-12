---
name: MorningBrief
description: "Generate attorney's morning briefing with calendar, tasks, relationships, and case priorities"
triggers:
  - "morning brief"
  - "what's on my calendar"
  - "what should i focus on"
  - "daily digest"
tools_required:
  - list_events
  - graph_query
  - get_case_workflow_status
---

# Morning Brief Skill

Generate < 150 word morning briefing (Second Brain principle #6).

## Query Sources

1. **Calendar (Google Calendar API):**
   ```python
   today_events = list_events(
       time_min=today_start,
       time_max=today_end,
       max_results=10
   )
   ```

2. **Tasks (Graph):**
   ```cypher
   MATCH (t:PersonalAssistant_Task)
   WHERE t.status != 'complete'
     AND (t.due_date = date() OR t.due_date < date())
   RETURN t
   ORDER BY t.priority DESC, t.due_date ASC
   LIMIT 10
   ```

3. **Follow-Ups (Graph):**
   ```cypher
   MATCH (p)
   WHERE (p:PersonalAssistant_Attorney OR p:PersonalAssistant_Judge OR p:PersonalAssistant_OpposingCounsel)
     AND p.follow_ups IS NOT NULL
     AND p.follow_ups <> ''
   RETURN p.name, p.follow_ups, p.last_contacted
   ORDER BY p.last_contacted ASC
   LIMIT 5
   ```

4. **Case Priorities (Graph):**
   ```cypher
   MATCH (c:Case)-[:IN_PHASE]->(phase:Phase)
   MATCH (c)-[:HAS_STATUS]->(status:LandmarkStatus)-[:FOR_LANDMARK]->(lm:Landmark)
   WHERE lm.hard_blocker = true
     AND status.status != 'complete'
   RETURN c.name, lm.display_name
   ```

## Output Format

```
🌅 MORNING BRIEF - {date}

TOP 3 ACTIONS:
1. File motion in Martinez case (due today)
2. Call Judge Smith re: Wilson hearing time
3. Follow up with State Farm adjuster on Johnson settlement

📅 CALENDAR:
• 10 AM: Client meeting - Martinez case
• 2 PM: Deposition - Wilson MVA
• 4 PM: Settlement conference call - Thompson case

⚠️ MIGHT BE STUCK:
Medical records request for Garcia case (waiting 3 weeks)

✨ SMALL WIN:
Successfully negotiated $45K increase in Martinez settlement offer
```

## Workflow

1. Use `list_events()` to get today's calendar
2. Use `graph_query()` with custom_cypher to get tasks
3. Use `graph_query()` with custom_cypher to get follow-ups
4. Use `graph_query()` with custom_cypher to get case blockers
5. Format output (< 150 words total)
6. Return formatted brief
