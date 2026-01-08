# Episode Files Review Helper

## How to Mark Individual Episodes to Skip

To exclude specific episodes from ingestion, add `"skip": true` to any episode object.

### Manual Editing

Open a case file and add the skip field to unwanted episodes:

```json
[
  {
    "case_name": "James-Kiper-MVA-12-5-2022",
    "episode_name": "Justin - 2022-12-08",
    "episode_body": "sent intake docs",
    "skip": true  ← Add this to exclude
  },
  {
    "case_name": "James-Kiper-MVA-12-5-2022",
    "episode_name": "Jessa - 2022-12-10",
    "episode_body": "Called client to confirm treatment",
    ← No skip field = will be ingested
  }
]
```

### Using jq (Command Line)

Mark episodes matching a pattern:

```bash
# Skip all episodes with "test" in the body
jq '.[].skip = (if .episode_body | contains("test") then true else . end)' Case.json > temp.json && mv temp.json Case.json

# Skip episodes by author
jq '.[].skip = (if .author == "Integration" then true else . end)' Case.json > temp.json && mv temp.json Case.json

# Skip short episodes (< 50 chars)
jq '.[].skip = (if (.episode_body | length) < 50 then true else . end)' Case.json > temp.json && mv temp.json Case.json
```

### Finding Skipped Episodes

Count how many you've marked to skip:

```bash
jq '[.[] | select(.skip == true)] | length' Case.json
```

View all skipped episodes in a case:

```bash
jq '.[] | select(.skip == true) | {name: .episode_name, reason: .episode_body[:50]}' Case.json
```

---

## Quick Stats

**Total Cases:** 140 files
**Total Episodes:** 17,097

**Top 10 Cases by Episode Count:**
1. Amy-Mills-Premise-04-26-2019: 765 episodes
2. Muhammad-Alif-MVA-11-08-2022: 682 episodes
3. James-Sadler-MVA-4-07-2023: 487 episodes
4. Juanita-Nicole-Downs-MVA-4-16-2021: 479 episodes
5. Robin-Wilder-Hamilton-MVA-6-15-2023: 437 episodes
6. Greg-Neltner-MVA-4-1-2023: 410 episodes
7. Debra-Marshall-MVA-12-3-2022: 390 episodes
8. Estate-of-Betty-Prince-Premise-7-14-2020: 383 episodes
9. Kimberly-Brasher-Premise-2-25-2023: 369 episodes
10. Estate-of-Keith-Graser-WC-12-07-2020: 360 episodes

---

## Review Checklist

For each episode, consider skipping if:
- [ ] Empty or very short (< 20 chars) - **Auto-skip these**
- [ ] Test data or placeholders
- [ ] Duplicates
- [ ] Not relevant to case history
- [ ] Contains sensitive data that shouldn't be searchable
- [ ] Integration artifacts (empty messages, system logs)

For each case file, verify:
- [ ] Case name is correct
- [ ] Client name extracted properly
- [ ] Episode dates make sense
- [ ] Content is not truncated
- [ ] Mark unwanted episodes with `"skip": true`

---

## Ingestion Plan

Once you've reviewed and excluded unwanted cases:

1. **Test ingestion** - Pick 1-2 small cases first
2. **Verify search** - Test `query_case_graph()` on those cases
3. **Batch ingestion** - Process remaining approved cases

The ingestion script will:
- Skip any file in `_excluded/` folder
- Skip any file starting with `_`
- Skip any case listed in `_skiplist.txt`
- Process all other JSON files in `by_case/`
