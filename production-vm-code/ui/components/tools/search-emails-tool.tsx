"use client";

import { makeAssistantToolUI } from "@assistant-ui/react";
import { MailIcon } from "lucide-react";

type SearchEmailsArgs = {
  query: string;
  max_results?: number;
  include_spam_trash?: boolean;
};

type ParsedEmail = {
  subject: string;
  from?: string;
  date?: string;
  snippet?: string;
  id?: string;
};

function parseSearchEmails(text: string): ParsedEmail[] {
  // Best-effort parse of gmail_tools.search_emails() output
  // Blocks like:
  // **1. Subject**
  // From: ...
  // Date: ...
  // Snippet: ...
  // ID: ...
  const lines = (text || "").split("\n");
  const emails: ParsedEmail[] = [];
  let cur: ParsedEmail | null = null;

  for (const raw of lines) {
    const line = raw.trim();
    const header = line.match(/^\*\*\d+\.\s+(.*)\*\*$/);
    if (header) {
      if (cur) emails.push(cur);
      cur = { subject: header[1].trim() };
      continue;
    }
    if (!cur) continue;
    const mFrom = line.match(/^From:\s+(.*)$/i);
    if (mFrom) {
      cur.from = mFrom[1].trim();
      continue;
    }
    const mDate = line.match(/^Date:\s+(.*)$/i);
    if (mDate) {
      cur.date = mDate[1].trim();
      continue;
    }
    const mSnippet = line.match(/^Snippet:\s+(.*)$/i);
    if (mSnippet) {
      cur.snippet = mSnippet[1].trim().replace(/\.\.\.$/, "");
      continue;
    }
    const mId = line.match(/^ID:\s+(.*)$/i);
    if (mId) {
      cur.id = mId[1].trim();
      continue;
    }
  }
  if (cur) emails.push(cur);
  return emails;
}

export const SearchEmailsTool = makeAssistantToolUI<SearchEmailsArgs, string>({
  toolName: "search_emails",
  render: ({ args, result, status }) => {
    const emails = result ? parseSearchEmails(result) : [];
    return (
      <div className="mb-4 w-full rounded-lg border p-3">
        <div className="flex items-center gap-2">
          <MailIcon className="size-4 text-muted-foreground" />
          <div className="text-sm font-semibold">Email search</div>
          <div className="flex-1" />
          <div className="text-xs text-muted-foreground">
            {status.type === "running" ? "Searching…" : `${emails.length} parsed`}
          </div>
        </div>

        <div className="mt-2 text-xs text-muted-foreground">
          search_emails({JSON.stringify(args)})
        </div>

        {result && (
          <>
            {emails.length ? (
              <div className="mt-3 flex flex-col gap-2">
                {emails.slice(0, 20).map((e, idx) => (
                  <div key={e.id ?? idx} className="rounded-md border bg-card p-2">
                    <div className="text-sm font-medium">{e.subject}</div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      {e.from ? `From: ${e.from}` : ""}
                      {e.date ? ` · ${e.date}` : ""}
                    </div>
                    {e.snippet && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        {e.snippet}
                      </div>
                    )}
                    {e.id && (
                      <div className="mt-2 font-mono text-[11px] text-muted-foreground">
                        ID: {e.id}
                      </div>
                    )}
                  </div>
                ))}
                {emails.length > 20 && (
                  <div className="text-xs text-muted-foreground">
                    Showing first 20 parsed emails.
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

