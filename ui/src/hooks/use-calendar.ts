"use client";

import { useEffect, useState } from "react";

export interface CalendarEvent {
  id: string;
  title: string;
  start: string; // ISO datetime
  end: string;
  description?: string;
  location?: string;
  attendees?: string[];
}

export function useCalendar() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  const loadEvents = async (start: Date, end: Date) => {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/calendar?start=${start.toISOString()}&end=${end.toISOString()}`
      );
      const data = await response.json();
      setEvents(data.events || []);
    } catch (error) {
      console.error("Failed to load calendar events:", error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const createEvent = async (event: Omit<CalendarEvent, "id">) => {
    try {
      const response = await fetch("/api/calendar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(event),
      });
      const data = await response.json();

      // Reload events after creation
      const monthStart = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
      const monthEnd = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0);
      await loadEvents(monthStart, monthEnd);

      return data;
    } catch (error) {
      console.error("Failed to create event:", error);
      throw error;
    }
  };

  // Load current month on mount and when selectedDate changes
  useEffect(() => {
    const monthStart = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1);
    const monthEnd = new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 0);
    loadEvents(monthStart, monthEnd);
  }, [selectedDate]);

  return {
    events,
    loading,
    selectedDate,
    setSelectedDate,
    createEvent,
    reloadEvents: loadEvents,
  };
}
