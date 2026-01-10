"use client";

import { useState, useEffect } from "react";
import { LeftSidebar } from "./left-sidebar";
import { RightPanel } from "./right-panel";
import { ChatPanel } from "@/components/chat/chat-panel";
import { useWorkbenchStore } from "@/stores/workbench-store";
import { Menu, X, PanelRightClose, PanelRight } from "lucide-react";
import { cn } from "@/lib/utils";

export function Workbench() {
  const {
    leftSidebarOpen,
    rightPanelOpen,
    panelsSwapped,
    toggleLeftSidebar,
    toggleRightPanel,
    openDocument
  } = useWorkbenchStore();

  return (
    <div className="flex h-screen overflow-hidden bg-[#f8f7f4]">
      {/* Left Sidebar - Always visible (removed collapsible behavior) */}
      <aside
        className={cn(
          "shrink-0 border-r border-[#d4c5a9] bg-white shadow-[2px_0_8px_rgba(30,58,95,0.08)]",
          "w-80 min-w-[320px]" // Always 320px, can't collapse
        )}
      >
        <div className="h-full w-full">
          <LeftSidebar />
        </div>
      </aside>

      {/* Main Content Area - Conditionally Chat or Artifact */}
      <main className="flex-1 min-w-0 max-w-full flex flex-col relative overflow-hidden">
        {/* Top Bar */}
        <div className="shrink-0 flex items-center justify-between px-4 py-2 border-b border-[#d4c5a9] bg-white">
          {/* Title - centered */}
          <div className="flex-1 flex items-center justify-center gap-2">
            <h1 className="text-[#1e3a5f] font-serif text-sm font-semibold tracking-wide">
              Roscoe AI Paralegal
            </h1>
            <span className="text-[#c9a227] text-xs italic">• Whaley Law Firm</span>
          </div>

          {/* Right panel toggle */}
          <button
            onClick={toggleRightPanel}
            className={cn(
              "p-2 rounded-lg transition-colors",
              rightPanelOpen
                ? "bg-[#1e3a5f] text-white"
                : "hover:bg-[#f5f3ed] text-[#1e3a5f]",
              !openDocument && !panelsSwapped && "opacity-50 cursor-not-allowed"
            )}
            title={rightPanelOpen ? "Close panel" : "Open panel"}
            disabled={!openDocument && !rightPanelOpen && !panelsSwapped}
          >
            {rightPanelOpen ? (
              <PanelRightClose className="h-5 w-5" />
            ) : (
              <PanelRight className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Content - Chat or Artifact based on swap state */}
        <div className="flex-1 min-h-0 overflow-hidden">
          {panelsSwapped ? <RightPanel /> : <ChatPanel />}
        </div>
      </main>

      {/* Right Panel - Artifact or Chat based on swap state */}
      <aside
        className={cn(
          "shrink-0 border-l border-[#d4c5a9] bg-white shadow-[-2px_0_8px_rgba(30,58,95,0.08)]",
          "transition-all duration-300 ease-in-out",
          rightPanelOpen ? (panelsSwapped ? "w-[400px]" : "w-[500px]") : "w-0"
        )}
      >
        <div className={cn(
          "h-full transition-opacity duration-200",
          rightPanelOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}>
          {panelsSwapped ? <ChatPanel /> : <RightPanel />}
        </div>
      </aside>
    </div>
  );
}
