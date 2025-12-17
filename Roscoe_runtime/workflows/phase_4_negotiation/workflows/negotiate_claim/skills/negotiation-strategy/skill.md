---
name: negotiation-strategy
description: >
  Develop and execute negotiation tactics for settlement discussions with
  insurance adjusters. Use when preparing counter-offers, responding to
  lowball offers, planning negotiation approach, or coaching on negotiation
  communication. Covers anchoring, bracketing, concessions, and closing.
---

# Negotiation Strategy Skill

## Skill Metadata

- **ID**: negotiation-strategy
- **Category**: negotiation
- **Model Required**: claude-sonnet-4-20250514 or higher
- **Reference Material**: `references/tactics.md`, `references/counter-strategies.md`
- **Tools Required**: `generate_document.py` (for counter-offer letters)

---

## When to Use This Skill

Use this skill when:
- Planning response to insurance offer
- Developing counter-offer strategy
- Preparing negotiation talking points
- Adjuster is being difficult
- Need to break negotiation impasse
- Client wants advice on negotiation approach

**DO NOT use if:**
- No offer has been made (use `send_demand` first)
- Just calculating net (use `offer-evaluation`)
- Tracking offers (use `offer-tracking`)

---

## Workflow

### Step 1: Analyze Current Position

**Review:**
- Our demand amount
- Their current offer
- Number of rounds so far
- Movement patterns
- Time in negotiation

**Calculate Gap:**
```
Gap = Our Position - Their Position
Gap % = Gap / Our Demand × 100
```

### Step 2: Determine Strategy

**If First Offer:**
- Evaluate reasonableness
- Plan counter that leaves room
- Don't split difference immediately

**If Subsequent Offer:**
- Analyze their movement
- Match or reduce concession size
- Signal approaching final number

**See:** `references/tactics.md` for detailed tactics.

### Step 3: Set Counter Amount

**Principles:**
- Leave negotiating room
- Make justified movement
- Don't appear desperate
- Signal flexibility without weakness

**Counter Calculation:**
```
If Gap > 50%: Counter at 10-15% reduction from demand
If Gap 25-50%: Counter at 15-25% reduction
If Gap < 25%: Consider splitting or final number
```

### Step 4: Prepare Counter Communication

**Include:**
1. Acknowledge their offer
2. Explain why insufficient
3. State counter amount
4. Provide justification
5. Request response timeline

**Use:** Copy `counter_offer_letter.md` to `/{project}/Documents/Negotiation/` then run `generate_document.py`

### Step 5: Anticipate Response

Prepare for:
- Acceptance (have settlement process ready)
- Counter-counter (plan next move)
- Rejection (evaluate alternatives)
- No response (follow-up plan)

---

## Key Tactics

### Anchoring
- First number sets expectations
- Our demand anchors high
- Their first offer anchors low
- Work toward middle strategically

### Bracketing
- Note implied settlement range
- Their first offer + our demand = bracket
- Midpoint often becomes settlement zone

### Concession Patterns
- Start with larger concessions
- Reduce concession size over time
- Signals approaching final number

### Closing
- Recognize when deal is achievable
- Don't push past good offers
- Use "split the difference" strategically

**See:** `references/counter-strategies.md` for structuring counters.

---

## Difficult Situations

### Lowball First Offer
- Don't overreact
- Counter strongly but reasonably
- Request explanation
- Emphasize case value

### No Movement
- Change approach (new arguments)
- Consider direct attorney call
- Escalate to supervisor
- Evaluate litigation

### Adjuster Changed
- Request introduction
- Re-establish case value
- Be patient with learning curve

---

## Output Format

```markdown
## Negotiation Strategy Analysis

### Current Status
- Demand: $X
- Their Offer: $Y
- Gap: $Z (X%)
- Rounds: N

### Recommended Counter
**Amount:** $[counter]
**Reasoning:** [justification]

### Key Talking Points
1. [Point 1]
2. [Point 2]
3. [Point 3]

### Anticipated Responses
- If they accept: [action]
- If they counter at $X: [action]
- If they reject: [action]

### Timeline
- Send counter by: [date]
- Expect response by: [date]
- Follow-up if no response: [date]
```

---

## Related Skills

- `offer-evaluation` - For analyzing offer merits
- `calendar-scheduling` - For follow-up scheduling
- `offer-tracking` - For documenting negotiations

---

## Reference Material

For detailed strategies, load:
- `references/tactics.md` - Negotiation tactics and techniques
- `references/counter-strategies.md` - Structuring effective counters

