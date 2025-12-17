"use client";

import { useEffect, useMemo } from "react";
import { makeAssistantToolUI } from "@assistant-ui/react";
import { CalendarIcon } from "lucide-react";

import { useWorkbenchStore, type CalendarEvent } from "@/lib/workbench-store";

type RenderCalendarArgs = {
  date: string;
  days?: number;
  include_google?: boolean;
  include_roscoe?: boolean;
};

type UiCommand =
  | { type: "workbench.setCenterView"; view: "viewer" | "monaco" | "calendar" }
  | { type: "calendar.setEvents"; events: CalendarEvent[]; date?: string; days?: number }
  | { type: "calendar.clear" };

type RenderCalendarResult =
  | {
      success: true;
      commands: UiCommand[];
      title?: string;
    }
  | {
      success: false;
      error: string;
    }
  | unknown;

function isObject(v: unknown): v is Record<string, any> {
  return !!v && typeof v === "object" && !Array.isArray(v);
}

function coerceCommands(result: unknown): UiCommand[] | null {
  // Tool results come as JSON strings from LangGraph - parse them first
  let parsed = result;
  if (typeof result === "string") {
    try {
      parsed = JSON.parse(result);
    } catch {
      return null;
    }
  }

  if (!isObject(parsed)) return null;
  const cmds = (parsed as any).commands;
  if (!Array.isArray(cmds)) return null;
  return cmds as UiCommand[];
}

export const RenderCalendarTool = makeAssistantToolUI<
  RenderCalendarArgs,
  RenderCalendarResult
>({
  toolName: "render_calendar",
  render: ({ args, result, status }) => {
    const setCenterView = useWorkbenchStore((s) => s.setCenterView);
    const setCalendarEvents = useWorkbenchStore((s) => s.setCalendarEvents);

    const commands = useMemo(() => coerceCommands(result), [result]);

    useEffect(() => {
      if (!commands?.length) return;
      if (status.type === "running") return;

      for (const c of commands) {
        switch (c.type) {
          case "workbench.setCenterView":
            setCenterView(c.view);
            break;
          case "calendar.setEvents":
            setCalendarEvents(c.events ?? []);
            setCenterView("calendar");
            break;
          case "calendar.clear":
            setCalendarEvents([]);
            break;
        }
      }
      // We intentionally don't re-run for store setters.
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [commands, status.type]);

    // Parse title from result (handle JSON string from LangGraph)
    const getTitle = () => {
      let parsed = result;
      if (typeof result === "string") {
        try {
          parsed = JSON.parse(result);
        } catch {
          return "Calendar";
        }
      }
      return isObject(parsed) && typeof (parsed as any).title === "string"
        ? ((parsed as any).title as string)
        : "Calendar";
    };
    const title = getTitle();

    return (
      <div className="mb-4 w-full rounded-lg border p-3">
        <div className="flex items-center gap-2">
          <CalendarIcon className="size-4 text-muted-foreground" />
          <div className="text-sm font-semibold">{title}</div>
          <div className="flex-1" />
          <div className="text-xs text-muted-foreground">
            {status.type === "running"
              ? "Loading…"
              : commands?.length
                ? `${commands.length} action(s)`
                : "No actions"}
          </div>
        </div>

        <div className="mt-2 text-xs text-muted-foreground">
          render_calendar({args.date}{args.days && args.days > 1 ? `, ${args.days} days` : ""})
        </div>

        {(() => {
          // Parse error from result (handle JSON string from LangGraph)
          let parsed = result;
          if (typeof result === "string") {
            try {
              parsed = JSON.parse(result);
            } catch {
              return null;
            }
          }
          if (isObject(parsed) && (parsed as any).success === false) {
            return (
              <div className="mt-3 whitespace-pre-wrap rounded-md border border-destructive bg-destructive/10 p-2 text-sm text-destructive">
                {(parsed as any).error ?? "render_calendar failed"}
              </div>
            );
          }
          return null;
        })()}
      </div>
    );
  },
});
