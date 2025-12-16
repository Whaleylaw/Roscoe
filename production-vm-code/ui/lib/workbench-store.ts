import { create } from "zustand";

export type CenterView = "viewer" | "monaco" | "calendar";

export type CalendarEvent = {
  id?: string;
  summary?: string;
  start?: string;
  end?: string;
  location?: string;
  description?: string;
};

type WorkbenchState = {
  selectedPath: string | null;
  setSelectedPath: (path: string | null) => void;

  browserPath: string;
  setBrowserPath: (path: string) => void;

  centerView: CenterView;
  setCenterView: (view: CenterView) => void;

  // Bridge actions into iframes (Monaco/Calendar) from other components.
  pendingMonacoOpenPath: string | null;
  requestOpenInMonaco: (path: string) => void;
  clearPendingMonacoOpen: () => void;

  calendarEvents: CalendarEvent[] | null;
  setCalendarEvents: (events: CalendarEvent[] | null) => void;
};

export const useWorkbenchStore = create<WorkbenchState>((set) => ({
  selectedPath: null,
  setSelectedPath: (path) => set({ selectedPath: path }),

  browserPath: "/projects",
  setBrowserPath: (path) => set({ browserPath: path }),

  centerView: "viewer",
  setCenterView: (centerView) => set({ centerView }),

  pendingMonacoOpenPath: null,
  requestOpenInMonaco: (path) => set({ pendingMonacoOpenPath: path }),
  clearPendingMonacoOpen: () => set({ pendingMonacoOpenPath: null }),

  calendarEvents: null,
  setCalendarEvents: (events) => set({ calendarEvents: events }),
}));

