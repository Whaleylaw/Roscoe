# Skill Review Analysis

## Skills Created Today

### 1. complaint-drafting-skill.md (420 lines)

**Status**: ⚠️ Needs trimming

**Good**:
- ✅ Under 500 lines
- ✅ Clear decision tree for template selection
- ✅ Focuses on execution (template selection + application)

**Issues**:
- ⚠️ Step 4 "Gather Required Information" is overly detailed (50 lines listing obvious fields)
- ⚠️ Step 5 "Draft Complaint" walks through every complaint section (Claude knows this)
- ⚠️ "Kentucky-Specific Considerations" explains basic legal concepts
- ⚠️ "Common Pitfalls" section is education content

**Should be** (~250 lines):
```markdown
# Skill: Complaint Drafting

## Purpose
Analyze case and select/apply complaint template.

## Step 1: Analyze Case Type
[Decision criteria - keep this, it's good]

## Step 2: Select Template
[Template mapping table - keep this, it's specific to our forms]

## Step 3: Populate Template
Required fields: {{PLAINTIFF_NAME}}, {{INCIDENT_DATE}}, etc.

## Step 4: Verify Elements (KY Fact Pleading)
- [ ] Specific facts (not conclusions)
- [ ] All elements alleged
- [ ] Jury demand included

## Output
/Litigation/Pleadings/complaint_draft.docx

## Related
- Workflow: /workflow_engine/workflows/phase_6_litigation/file_complaint.md
- Templates: /forms/complaints/
```

**Recommendation**: Trim to ~250 lines, move Kentucky rules/pitfalls to references/

---

### 2. The 18 Education Skills (233-556 lines each)

**Location**: `Skills/litigation-discovery/`, `litigation-depositions/`, `litigation-trial/`

**Status**: ❌ NOT proper skills - These are comprehensive training materials

**Issues**:
- ❌ Too large (233-556 lines, some over 500)
- ❌ Extensive education content (Kentucky rules, examples, tables)
- ❌ Training appendices (Form Objection Cheat Sheets, Rule Citations)
- ❌ Detailed legal explanations Claude doesn't need
- ❌ Focus on HOW TO TRAIN, not HOW TO EXECUTE

**Example** - defend-client-skill.md (383 lines):
- Has "Form Objection Cheat Sheet" table (education)
- Has "Kentucky Rules Quick Reference" appendix (education)
- Has "Prompt Template for AI Paralegal" section (meta-documentation)
- Has detailed rule citations (CR 26.02, CR 30.03, KRE 503)

**These are reference materials, not execution skills.**

---

## Recommendations

### Option 1: Move to References (Recommended)

**Keep as reference/training materials**:
```
Skills/litigation-{category}/
├── {skill-name}-skill.md       # NEW: Concise execution skill
└── references/
    └── {original-name}.md      # MOVE: Education material
```

**Example**:
```
Skills/litigation-depositions/
├── defend-client-skill.md      # NEW: 150 lines, execution-focused
└── references/
    └── client-deposition-defense-guide.md  # MOVED: 383 lines, comprehensive
```

**New concise skill**:
```markdown
# Skill: Defend Client Deposition

## Purpose
Prepare client and attorney for deposition defense.

## Step 1: Review Deposition Notice
Extract date, time, location, scope.

## Step 2: Compile Case Documents
**Tool**: /Tools/document_processing/organize.py

Gather:
- Medical records
- Prior discovery
- Incident reports

## Step 3: Identify Privilege Issues
Flag attorney-client communications for protection.

## Step 4: Prepare Objection Framework
Create quick-reference for common objections.
See references/deposition-objections.md for full list.

## Step 5: Client Preparation
Brief client on deposition process.

## Output
- Document index
- Privilege memo
- Objection quick-reference
- Client prep packet

## Reference
For comprehensive guidance: references/client-deposition-defense-guide.md
```

### Option 2: Condense Drastically (Not Recommended)

Try to trim each 300-500 line education document to 150-250 lines by removing:
- Rule citations
- Detailed examples
- Explanation of legal concepts
- Appendices

**Problem**: Loses valuable reference content

---

## Action Plan

### Immediate: Fix complaint-drafting-skill.md

1. Trim Step 4 "Gather Required Information" (just list field names, not explanations)
2. Remove Step 5 "Draft Complaint" section-by-section guidance (Claude knows complaint structure)
3. Move "Kentucky-Specific Considerations" to references/kentucky_pleading_rules.md
4. Move "Common Pitfalls" to references/complaint_pitfalls.md
5. Keep core: Analyze → Select Template → Apply Template

**Target**: ~250 lines

### Phase 2: Handle 18 Education Skills

**For each of the 18 education skills**:

1. **Create references/ subdirectory**:
```bash
mkdir -p Skills/litigation-discovery/references
mkdir -p Skills/litigation-depositions/references
mkdir -p Skills/litigation-trial/references
```

2. **Move current files to references/**:
```bash
mv Skills/litigation-discovery/propound-discovery-skill.md \
   Skills/litigation-discovery/references/propound-discovery-guide.md
```

3. **Create new concise execution skills**:
```bash
# New file: Skills/litigation-discovery/propound-discovery-skill.md
# ~150-200 lines, execution-focused
```

4. **Reference the guides**:
```markdown
## Detailed Guidance
See: references/propound-discovery-guide.md
```

---

## Skill-by-Skill Assessment

### Discovery Skills (5 files, 382-556 lines each)

| File | Lines | Status | Action |
|------|-------|--------|--------|
| propound-discovery-skill.md | 556 | ❌ Over limit, education content | Move to references/, create concise version |
| respond-to-discovery-skill.md | 475 | ⚠️ Near limit, education content | Move to references/, create concise version |
| resolve-discovery-disputes-skill.md | 495 | ⚠️ Near limit | Move to references/, create concise version |
| identify-obstruction-skill.md | 382 | ⚠️ Education content | Move to references/, create concise version |
| ediscovery-skill.md | 482 | ⚠️ Near limit | Move to references/, create concise version |

### Deposition Skills (5 files, 359-490 lines each)

| File | Lines | Status | Action |
|------|-------|--------|--------|
| defend-client-skill.md | 383 | ⚠️ Has appendices, rules | Move to references/, create concise version |
| corporate-deposition-skill.md | 359 | ⚠️ Education content | Move to references/, create concise version |
| depose-expert-skill.md | 424 | ⚠️ Near limit | Move to references/, create concise version |
| examination-framework-skill.md | 466 | ⚠️ Near limit | Move to references/, create concise version |
| corporate-defendant-skill.md | 490 | ⚠️ Near limit | Move to references/, create concise version |

### Trial Skills (8 files, 233-489 lines each)

| File | Lines | Status | Action |
|------|-------|--------|--------|
| cross-examine-dme-skill.md | 379 | ⚠️ Education content | Move to references/, create concise version |
| cross-exam-tools-skill.md | 421 | ⚠️ Near limit | Move to references/, create concise version |
| cross-exam-fundamentals-skill.md | 489 | ⚠️ Near limit | Move to references/, create concise version |
| develop-case-theory-skill.md | 439 | ⚠️ Near limit | Move to references/, create concise version |
| prepare-expert-skill.md | 374 | ⚠️ Education content | Move to references/, create concise version |
| voir-dire-skill.md | 372 | ⚠️ Education content | Move to references/, create concise version |
| trial-advocacy-skill.md | 233 | ✅ Size OK, but education content | Move to references/, create concise version |
| trial-support-skill.md | 462 | ⚠️ Near limit | Move to references/, create concise version |

---

## Summary

**All 19 skills need revision**:
- 1 skill (complaint-drafting) needs trimming
- 18 skills are education materials that should be references

**Recommended approach**:
1. Create references/ subdirectories in each litigation skill category
2. Move all current files to references/ as training/reference materials
3. Create new concise execution skills (150-250 lines each)
4. Reference the comprehensive guides when needed

**Benefit**:
- Keeps valuable training content
- Creates proper execution skills
- Follows Anthropic best practices
- Enables progressive disclosure

**Next**: Do you want me to:
A) Execute this reorganization automatically?
B) Do it manually for a few examples first?
C) Something else?
