# Generative UI Strategy: Roscoe Paralegal Agent

## 1. Executive Summary

The goal is to build a "Generative UI" for the Roscoe Paralegal Agent—an interface that doesn't just chat, but **constructs specialized tools on the fly**. When an attorney asks for a timeline, the agent renders an interactive timeline component. When they need to draft a demand letter, the agent spawns a collaborative editor with track changes.

**Recommended Stack:**
*   **Framework:** **Next.js (App Router)**
*   **AI Engine:** **Vercel AI SDK (`ai/rsc`)**
*   **Document Editor:** **TipTap** (with custom "AI Suggestion" extensions)
*   **UI Library:** **shadcn/ui** + **Tailwind CSS**

---

## 2. Comparison of Options

You requested a review of **Thesys**, **CopilotKit**, **Ag-UI**, and others. Here is the analysis:

### A. Thesys (Thesys.dev)
*   **What it is:** A UI generation SDK for LLMs.
*   **Verdict:** **Too Early / Niche.** While promising, it lacks the massive ecosystem support of the Vercel AI SDK. Documentation and community examples are sparse compared to the "standard" stack.
*   **Risk:** High dependency risk for a critical production app.

### B. CopilotKit (CopilotKit.ai)
*   **What it is:** A framework for embedding "Copilots" into existing apps (Sidebars, Textareas).
*   **Pros:** excellent `CopilotTextarea` and context-awareness out of the box.
*   **Cons:** It feels more like an "overlay" or "sidebar" solution. For Roscoe, we want the *entire interface* to be the agent (a "Canvas" approach), not just a sidebar helper.
*   **Verdict:** **Strong Alternative**, but less flexible than building raw with Vercel AI SDK.

### C. Ag-UI / Other
*   **Analysis:** Likely refers to newer or experimental "Agentic UI" frameworks.
*   **Verdict:** **Avoid.** In the fast-moving AI space, sticking to the "Gold Standard" infrastructure (Vercel/Next.js) is safer than adopting micro-frameworks that may be abandoned.

### D. Vercel AI SDK (The Winner)
*   **What it is:** The industry standard for React Server Components + AI.
*   **Why it wins:**
    *   **`streamUI` Function:** The killer feature. The LLM can call a tool that returns a **React Component** directly to the client.
    *   **Control:** You have 100% control over the component code (unlike "Widget" based builders).
    *   **Ecosystem:** Works natively with shadcn/ui, Tailwind, and TipTap.

---

## 3. The "Generative" Implementation Plan

We will build a **Generative Canvas** where the chat stream is the "Command Center," but it spawns rich, interactive artifacts.

### Phase 1: Core Infrastructure (The "Stream")
*   **Tech:** Next.js, Vercel AI SDK (`ai/rsc`), `zod` for schema validation.
*   **Mechanism:**
    1.  User asks: "Show me the accident timeline."
    2.  Agent calls `get_timeline_data()`.
    3.  Agent calls `streamUI` -> renders `<TimelineComponent data={...} />`.
    4.  User sees an interactive timeline in the chat stream, not text.

### Phase 2: The "Paralegal Editor" (Document Drafting)
This is the most complex and critical feature.
*   **Tech:** **TipTap** (Headless Editor).
*   **Feature: "AI Track Changes"**
    *   We will not just "rewrite" text. We will implement a "Suggestion Mode".
    *   When the AI edits a document, it creates **Decorations** (Red strike-through for deletions, Green underline for insertions).
    *   **Attorney Control:** The user must click "Accept" or "Reject" on each change. This is non-negotiable for legal liability.

### Phase 3: Multimedia Evidence (Video/Image)
*   **Tech:** Custom React Players + Canvas overlays.
*   **Feature: "Deep-Link Video"**
    *   Use the `analyze_video` tool's output (timestamps).
    *   Render a `<VideoPlayer>` where the timeline has **markers** for every event the AI found ("00:15 Impact", "00:45 Ambulance Arrives").
    *   Clicking a marker jumps the video instantly.

### Phase 4: Task & Case Management
*   **Tech:** `react-big-calendar` (or FullCalendar), `tanstack-table`.
*   **Components:**
    *   `<CalendarView />`: Interactive deadlines.
    *   `<ExhibitGrid />`: Draggable grid of generated trial exhibits.
    *   `<TaskKanban />`: "To Do / In Progress / Done" board for the case.

---

## 4. Component Catalog (The "Paralegal Toolkit")

These are the specialized components the Agent will be able to "summon":

| Component | Trigger Example | Description |
| :--- | :--- | :--- |
| **`DocumentEditor`** | "Draft a demand letter." | Full TipTap editor with Track Changes & Comments. |
| **`VideoEvidence`** | "Review the bodycam." | Video player with AI-generated timeline markers. |
| **`ExhibitGallery`** | "Create exhibits from these." | Grid view of images/docs with "Exhibit A" labels. |
| **`CaseTimeline`** | "What happened when?" | Vertical/Horizontal chronological view of facts. |
| **`CalendarWidget`** | "When is this due?" | Monthly/Weekly view of deadlines. |
| **`StatuteCard`** | "What is the law?" | Card showing statute text + relevance score. |

## 5. Next Steps

1.  **Initialize Next.js Project:** Set up the repo structure with `ai/rsc`.
2.  **Build the "Canvas" Layout:** A split-screen design (Chat on Left/Right, "Artifact" on Main Stage).
3.  **Implement `DocumentEditor`:** Integrate TipTap with a basic "Suggest" plugin.

