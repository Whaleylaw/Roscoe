# CourtListener API v4 Analysis

## Date: 2025-11-23

## Summary

CourtListener REST API v4 provides extensive access to legal data, including **oral arguments with automatic speech-to-text transcription** - a powerful feature for paralegal research.

## Available Endpoints (48 total)

### Core Search & Opinions (FREE - No API Key Required)

1. **search** - `/api/rest/v4/search/`
   - Full-text search across millions of court opinions
   - Filter by court, date, case name, citation
   - Returns case details, citations, judges, snippets
   - Supports pagination with cursor
   - **Status**: Currently using v3 API - should upgrade to v4

2. **courts** - `/api/rest/v4/courts/`
   - List all federal and state courts
   - 127 federal courts, comprehensive state coverage
   - Metadata: jurisdiction, citation format, URL, date range
   - Useful for validating court codes

3. **audio** - `/api/rest/v4/audio/` ⭐ **DISCOVERY**
   - Oral arguments from appellate courts
   - **Automatic speech-to-text transcription included!**
   - Searchable by court, date, case name
   - Download URLs for MP3 files
   - Duration, judges panel, docket links
   - **High Value**: Transcripts save hours of manual listening

4. **opinions** - `/api/rest/v4/opinions/`
   - Individual opinion access
   - PDF download URLs
   - Citation tracking (who cites this opinion)
   - Full opinion text (HTML/PDF)

5. **clusters** - `/api/rest/v4/clusters/`
   - Opinion clusters (related opinions)
   - Case metadata aggregation

6. **opinions-cited** - `/api/rest/v4/opinions-cited/`
   - Citation network analysis
   - Track how cases cite each other

### Case Details (Requires Authentication)

7. **dockets** - `/api/rest/v4/dockets/`
   - Full docket information
   - Filing history, parties, attorneys
   - **Requires**: API key

8. **docket-entries** - `/api/rest/v4/docket-entries/`
   - Individual docket entries
   - **Requires**: API key

9. **recap-documents** - `/api/rest/v4/recap-documents/`
   - PACER documents via RECAP
   - Court filings, motions, briefs
   - **Requires**: API key

### Judicial Information (FREE)

10. **people** - `/api/rest/v4/people/`
    - Judge biographical information
    - Appointment details, political affiliation
    - Useful for understanding bench composition

11. **positions** - `/api/rest/v4/positions/`
    - Judicial positions and appointments

12. **educations** - `/api/rest/v4/educations/`
    - Judge educational background

13. **political-affiliations** - `/api/rest/v4/political-affiliations/`
    - Political party affiliations

### Party & Attorney Information

14. **parties** - `/api/rest/v4/parties/`
    - Party information from cases

15. **attorneys** - `/api/rest/v4/attorneys/`
    - Attorney information from cases

### Other Endpoints (38 more)

Including: tags, visualizations, financial disclosures, citation lookup, FJC database, etc.

## Current Tool Status

**court_case_search.py** (created 2025-11-23):
- Uses v3 API: `https://www.courtlistener.com/api/rest/v3/search/`
- Returns HTTP 403 error (likely needs API key for production)
- **Recommendation**: Update to v4 API endpoint

## Recommended New Tools

### 1. **oral_arguments_search.py** ⭐ HIGH PRIORITY

**Why**: Automatic transcription of oral arguments is EXTREMELY valuable for:
- Analyzing attorney performance and argumentation
- Reviewing appellate strategy
- Finding precedent on specific legal arguments
- Preparation for oral arguments

**Usage Example**:
```bash
python /Tools/oral_arguments_search.py "personal injury Kentucky" --court ca6 --max-results 10
```

**Output**:
- Case name, docket, court, date
- Audio duration, panel judges
- **Full speech-to-text transcript**
- MP3 download URL
- Absolute URL to CourtListener page

**Token Savings**: Agent doesn't need audio analysis tools for oral arguments - gets transcript directly

**Cost**: 100% FREE

### 2. **court_list.py** (Utility)

**Why**: List available courts and their codes for use with other tools

**Usage Example**:
```bash
python /Tools/court_list.py --jurisdiction F  # Federal courts
python /Tools/court_list.py --jurisdiction S --state KY  # Kentucky state courts
```

**Output**: Court ID, full name, citation format, jurisdiction, URL

**Cost**: 100% FREE

### 3. **citation_lookup.py**

**Why**: Look up cases by citation (e.g., "342 F. Supp. 3d 773")

**Usage Example**:
```bash
python /Tools/citation_lookup.py "342 F. Supp. 3d 773"
```

**Cost**: 100% FREE

### 4. **judge_lookup.py**

**Why**: Research judges for case assignment, recusal motions, or understanding bench

**Usage Example**:
```bash
python /Tools/judge_lookup.py "Sargus" --court ohsd
```

**Cost**: 100% FREE

## Improvements to Existing Tool

### Update court_case_search.py to v4

**Changes needed**:
1. Update base URL: `https://www.courtlistener.com/api/rest/v4/search/`
2. Update query parameters (v4 format)
3. Test without API key
4. Add optional COURTLISTENER_API_KEY for higher rate limits

**Benefits**:
- Better structured responses
- Improved filtering options
- More reliable (v4 is actively maintained)

## Implementation Priority

1. **oral_arguments_search.py** - HIGHEST VALUE (automatic transcription!)
2. **Update court_case_search.py to v4** - FIX EXISTING TOOL
3. **court_list.py** - UTILITY (helps users find court codes)
4. **citation_lookup.py** - MEDIUM VALUE
5. **judge_lookup.py** - LOWER PRIORITY (nice-to-have)

## API Rate Limits

- **Without API key**: 5,000 requests/hour
- **With API key**: Higher limits (exact limit not documented)
- **Recommendation**: Start without API key, add if needed

## Environment Variables

```bash
# Optional - for higher rate limits and docket access
COURTLISTENER_API_KEY=your_api_key_here
```

## Next Steps

1. Create `oral_arguments_search.py` - capture oral argument transcripts
2. Fix `court_case_search.py` - update to v4 API
3. Update `tools_manifest.json` - add new tools, update existing
4. Test all tools with real queries

## Example Use Case: Personal Injury Research

**Agent workflow**:
1. Search opinions: `court_case_search.py "whiplash motor vehicle Kentucky"`
2. Find oral arguments: `oral_arguments_search.py "personal injury damages" --court ca6`
3. Analyze attorney arguments from transcripts (no audio processing needed!)
4. Build case strategy based on successful appellate arguments
