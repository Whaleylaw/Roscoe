"use client";

import { useCalendar } from "@/hooks/use-calendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Plus } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

export function CalendarView() {
  const { events, loading, selectedDate, setSelectedDate } = useCalendar();

  const goToPrevMonth = () => {
    const prev = new Date(selectedDate);
    prev.setMonth(prev.getMonth() - 1);
    setSelectedDate(prev);
  };

  const goToNextMonth = () => {
    const next = new Date(selectedDate);
    next.setMonth(next.getMonth() + 1);
    setSelectedDate(next);
  };

  const monthName = selectedDate.toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
  });

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">Loading calendar...</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center gap-2 border-b p-3">
        <Button size="sm" variant="outline" onClick={goToPrevMonth}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <h2 className="text-lg font-semibold flex-1 text-center">{monthName}</h2>
        <Button size="sm" variant="outline" onClick={goToNextMonth}>
          <ChevronRight className="h-4 w-4" />
        </Button>
        <Button size="sm" variant="default">
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {/* Event List */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {events.length === 0 ? (
            <p className="text-sm text-muted-foreground">No events this month</p>
          ) : (
            events.map((event) => (
              <Card key={event.id}>
                <CardHeader>
                  <CardTitle className="text-base">{event.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {new Date(event.start).toLocaleString()}
                  </p>
                  {event.description && (
                    <p className="text-sm mt-2">{event.description}</p>
                  )}
                  {event.location && (
                    <p className="text-xs text-muted-foreground mt-1">
                      📍 {event.location}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
