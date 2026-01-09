"use client";

import { useState } from "react";
import { FileBrowser } from "./file-browser";
import { ThreadManager } from "./thread-manager";
import { JobsKanban } from "./jobs-kanban";
import { cn } from "@/lib/utils";

type Tab = "files" | "threads" | "jobs";

export function LeftSidebar() {
  const [activeTab, setActiveTab] = useState<Tab>("files");

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="shrink-0 border-b-[3px] border-[#c9a227] px-4 py-3" style={{ background: 'linear-gradient(135deg, #1e3a5f 0%, #2c4a6e 100%)' }}>
        <h1 className="text-white font-serif text-sm font-semibold tracking-wide">
          Whaley Law Firm
        </h1>
      </div>

      {/* Tab Buttons */}
      <div className="shrink-0 border-b border-[#d4c5a9] p-2 bg-[#f8f7f4]">
        <div className="flex w-full bg-[#f5f3ed] border border-[#d4c5a9] rounded-md p-1">
          <button
            onClick={() => setActiveTab("files")}
            className={cn(
              "flex-1 text-[12px] py-1.5 rounded-sm font-medium transition-colors",
              activeTab === "files"
                ? "bg-[#1e3a5f] text-white"
                : "text-[#1e3a5f] hover:bg-white/50"
            )}
            >
              Files
          </button>
          <button
            onClick={() => setActiveTab("threads")}
            className={cn(
              "flex-1 text-[12px] py-1.5 rounded-sm font-medium transition-colors",
              activeTab === "threads"
                ? "bg-[#1e3a5f] text-white"
                : "text-[#1e3a5f] hover:bg-white/50"
            )}
            >
              Threads
          </button>
          <button
            onClick={() => setActiveTab("jobs")}
            className={cn(
              "flex-1 text-[12px] py-1.5 rounded-sm font-medium transition-colors",
              activeTab === "jobs"
                ? "bg-[#1e3a5f] text-white"
                : "text-[#1e3a5f] hover:bg-white/50"
            )}
            >
              Jobs
          </button>
        </div>
        </div>

      {/* Tab Content - use h-full instead of inset-0 for reliable height */}
      <div className="relative flex-1 min-h-0 overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-full overflow-y-auto">
          {activeTab === "files" && <FileBrowser />}
          {activeTab === "threads" && <ThreadManager />}
          {activeTab === "jobs" && <JobsKanban />}
        </div>
      </div>
    </div>
  );
}
