"use client";

import { LeftSidebar } from "./left-sidebar";
import { CenterView } from "./center-view";
import { ChatPanel } from "@/components/chat/chat-panel";

export function Workbench() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#f8f7f4]">
      {/* Left Sidebar: File Browser + Threads */}
      <aside className="w-72 shrink-0 border-r border-[#d4c5a9] bg-white shadow-[2px_0_8px_rgba(30,58,95,0.08)]">
        <LeftSidebar />
      </aside>

      {/* Center View: Document Viewer / Calendar / Artifacts */}
      <section className="flex-1 min-w-0 bg-[#f8f7f4]">
        <CenterView />
      </section>

      {/* Right Sidebar: Custom Chat Panel */}
      <aside className="w-[420px] shrink-0 border-l border-[#d4c5a9] bg-white shadow-[-2px_0_8px_rgba(30,58,95,0.08)]">
        <ChatPanel />
      </aside>
    </div>
  );
}
