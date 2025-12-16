"use client";

import { useEffect } from "react";
import { makeAssistantToolUI } from "@assistant-ui/react";
import { CalendarIcon } from "lucide-react";
import { useWorkbenchStore } from "@/lib/workbench-store";

type ListEventsArgs = {
  days?: number;
  max_results?: number;
  calendar_id?: string;
  query?: string | null;
};

type ParsedEvent = {
  date: string;
  time: string;
  summary: string;
  location?: string;
};

type CalendarEvent = {
  id?: string;
  summary?: string;
  start?: string;
  end?: string;
  location?: string;
  description?: string;
};

function parseListEventsMarkdown(text: string): ParsedEvent[] {
  // Best-effort parse of calendar_tools.list_events() output
  // Example lines:
  // 📅 **2025-12-16**
  //   • 09:00: Some Event @ Location
  const lines = (text || "").split("\n");
  let currentDate: string | null = null;
  const events: ParsedEvent[] = [];

  for (const raw of lines) {
    const line = raw.trim();
    const dateMatch = line.match(/^📅\s+\*\*(\d{4}-\d{2}-\d{2})\*\*$/);
    if (dateMatch) {
      currentDate = dateMatch[1];
      continue;
    }

    const bulletMatch = line.match(/^•\s+([^:]+):\s+(.*)$/);
    if (bulletMatch && currentDate) {
      const time = bulletMatch[1].trim();
      const rest = bulletMatch[2].trim();
      const [summaryPart, locationPart] = rest.split(" @ ");
      events.push({
        date: currentDate,
        time,
        summary: (summaryPart || "").trim(),
        location: locationPart ? locationPart.trim() : undefined,
      });
    }
  }

  return events;
}

export const ListEventsTool = makeAssistantToolUI<ListEventsArgs, string>({
  toolName: "list_events",
  render: ({ args, result, status }) => {
    const setCalendarEvents = useWorkbenchStore((s) => s.setCalendarEvents);
    const setCenterView = useWorkbenchStore((s) => s.setCenterView);
    const events = result ? parseListEventsMarkdown(result) : [];

    useEffect(() => {
      if (!result) return;
      if (status.type === "running") return;
      if (!events.length) return;

      // Push parsed events into the Calendar pane so it reflects what the agent returned.
      const toIso = (date: string, time: string) => {
        // Accept "09:00" or "9:00" etc. Best-effort local time.
        const m = time.match(/^(\d{1,2}):(\d{2})/);
        if (!m) return null;
        const hh = m[1].padStart(2, "0");
        const mm = m[2];
        const d = new Date(`${date}T${hh}:${mm}:00`);
        return Number.isNaN(d.getTime()) ? null : d.toISOString();
      };

      const mapped: CalendarEvent[] = events.map((e, idx) => {
        const startIso = toIso(e.date, e.time);
        let endIso: string | null = null;
        if (startIso) {
          const end = new Date(startIso);
          end.setHours(end.getHours() + 1);
          endIso = end.toISOString();
        }
        return {
          id: `${e.date}-${e.time}-${idx}`,
          summary: e.summary,
          start: startIso ?? undefined,
          end: endIso ?? undefined,
          location: e.location,
        };
      });

      setCalendarEvents(mapped);
      setCenterView("calendar");
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [result]);

    return (
      <div className="mb-4 w-full rounded-lg border p-3">
        <div className="flex items-center gap-2">
          <CalendarIcon className="size-4 text-muted-foreground" />
          <div className="text-sm font-semibold">Calendar events</div>
          <div className="flex-1" />
          <div className="text-xs text-muted-foreground">
            {status.type === "running" ? "Loading…" : `${events.length} parsed`}
          </div>
        </div>

        <div className="mt-2 text-xs text-muted-foreground">
          list_events({JSON.stringify(args)})
        </div>

        {result && (
          <>
            {events.length > 0 ? (
              <div className="mt-3 flex flex-col gap-2">
                {events.slice(0, 20).map((e, idx) => (
                  <div key={idx} className="rounded-md border bg-card p-2 text-sm">
                    <div className="font-medium">
                      {e.date} · {e.time}
                    </div>
                    <div>{e.summary}</div>
                    {e.location && (
                      <div className="text-xs text-muted-foreground">
                        {e.location}
                      </div>
                    )}
                  </div>
                ))}
                {events.length > 20 && (
                  <div className="text-xs text-muted-foreground">
                    Showing first 20 parsed events.
                  </div>
                )}
              </div>
            ) : (
              <div className="mt-3 whitespace-pre-wrap text-sm">{result}</div>
            )}
          </>
        )}
      </div>
    );
  },
});

