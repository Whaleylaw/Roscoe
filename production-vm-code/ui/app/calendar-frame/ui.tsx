"use client";

import { useEffect, useMemo, useState } from "react";
import type { JSONSchema7 } from "json-schema";
import { CalendarIcon, Trash2Icon } from "lucide-react";

import {
  AssistantFrameProvider,
  ModelContextRegistry,
} from "@assistant-ui/react";

import { Button } from "@/components/ui/button";

type CalendarEvent = {
  id?: string;
  summary?: string;
  start?: string;
  end?: string;
  location?: string;
  description?: string;
};

type SetCalendarEventsArgs = { events: CalendarEvent[] };
type SetCalendarEventsResult = { ok: true; count: number };

type ClearCalendarArgs = Record<string, never>;
type ClearCalendarResult = { ok: true };

const setEventsSchema: JSONSchema7 = {
  type: "object",
  additionalProperties: false,
  required: ["events"],
  properties: {
    events: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: true,
        properties: {
          id: { type: "string" },
          summary: { type: "string" },
          start: { type: "string" },
          end: { type: "string" },
          location: { type: "string" },
          description: { type: "string" },
        },
      },
    },
  },
};

const emptySchema: JSONSchema7 = {
  type: "object",
  additionalProperties: false,
  properties: {},
};

function formatWhen(e: CalendarEvent) {
  const start = e.start ? new Date(e.start) : null;
  const end = e.end ? new Date(e.end) : null;
  if (!start) return "Unknown time";
  const d = start.toLocaleDateString();
  const t1 = start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const t2 = end
    ? end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : null;
  return t2 ? `${d} ${t1}–${t2}` : `${d} ${t1}`;
}

export function CalendarFrameClient() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);

  const registry = useMemo(() => new ModelContextRegistry(), []);

  useEffect(() => {
    // Allow the parent workbench to control the calendar pane via postMessage.
    const onMessage = (ev: MessageEvent) => {
      const data = ev.data as any;
      if (!data || typeof data !== "object") return;
      if (data.type === "calendar.setCalendarEvents" && Array.isArray(data.events)) {
        setEvents(data.events);
      }
      if (data.type === "calendar.clearCalendar") {
        setEvents([]);
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  useEffect(() => {
    registry.addTool<SetCalendarEventsArgs, SetCalendarEventsResult>({
      toolName: "setCalendarEvents",
      description: "Display calendar events in the calendar pane",
      parameters: setEventsSchema,
      execute: async ({ events }) => {
        setEvents(events ?? []);
        return { ok: true, count: (events ?? []).length };
      },
    });

    registry.addTool<ClearCalendarArgs, ClearCalendarResult>({
      toolName: "clearCalendar",
      description: "Clear calendar events from the calendar pane",
      parameters: emptySchema,
      execute: async () => {
        setEvents([]);
        return { ok: true };
      },
    });

    const unsubscribe = AssistantFrameProvider.addModelContextProvider(registry);
    return () => unsubscribe();
  }, [registry]);

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b px-3 py-2 text-sm">
        <CalendarIcon className="size-4 text-muted-foreground" />
        <span className="font-semibold">Calendar</span>
        <span className="ml-2 text-muted-foreground">
          {events.length ? `${events.length} event(s)` : "No events loaded"}
        </span>
        <div className="flex-1" />
        <Button
          size="sm"
          variant="outline"
          onClick={() => setEvents([])}
          disabled={!events.length}
          aria-label="Clear events"
        >
          <Trash2Icon className="mr-2 size-4" />
          Clear
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-auto p-3">
        {!events.length && (
          <div className="text-sm text-muted-foreground">
            Waiting for events. (The assistant can call <code>setCalendarEvents</code>
            .)
          </div>
        )}

        <div className="flex flex-col gap-2">
          {events.map((e, idx) => (
            <div
              key={e.id ?? `${idx}`}
              className="rounded-md border bg-card p-3 text-sm"
            >
              <div className="font-semibold">
                {e.summary || "(untitled event)"}
              </div>
              <div className="mt-1 text-xs text-muted-foreground">
                {formatWhen(e)}
                {e.location ? ` · ${e.location}` : ""}
              </div>
              {e.description && (
                <div className="mt-2 whitespace-pre-wrap text-xs text-muted-foreground">
                  {e.description}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

