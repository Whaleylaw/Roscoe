"use client";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { FileBrowser } from "./file-browser";
import { ThreadManager } from "./thread-manager";

export function LeftSidebar() {
  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="bg-navy-gradient border-b-[3px] border-[#c9a227] px-4 py-3">
        <h1 className="text-white font-serif text-sm font-semibold tracking-wide">
          Whaley Law Firm
        </h1>
      </div>
      
      <Tabs defaultValue="files" className="flex-1 flex flex-col">
        <div className="border-b border-[#d4c5a9] p-2 bg-[#f8f7f4]">
          <TabsList className="w-full bg-[#f5f3ed] border border-[#d4c5a9]">
            <TabsTrigger 
              value="files" 
              className="flex-1 text-[12px] data-[state=active]:bg-[#1e3a5f] data-[state=active]:text-white data-[state=inactive]:text-[#1e3a5f]"
            >
              Files
            </TabsTrigger>
            <TabsTrigger 
              value="threads" 
              className="flex-1 text-[12px] data-[state=active]:bg-[#1e3a5f] data-[state=active]:text-white data-[state=inactive]:text-[#1e3a5f]"
            >
              Threads
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="files" className="flex-1 mt-0 overflow-hidden">
          <FileBrowser />
        </TabsContent>

        <TabsContent value="threads" className="flex-1 mt-0 overflow-hidden">
          <ThreadManager />
        </TabsContent>
      </Tabs>
    </div>
  );
}
