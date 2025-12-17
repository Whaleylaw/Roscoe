import { Client, ThreadState } from "@langchain/langgraph-sdk";
import {
  LangChainMessage,
  LangGraphCommand,
} from "@assistant-ui/react-langgraph";

const createClient = () => {
  const raw =
    process.env["NEXT_PUBLIC_LANGGRAPH_API_URL"] ??
    new URL("/api", window.location.href).href;

  // The SDK expects an absolute base URL. Our docker setup uses "/api" (relative),
  // so normalize it in the browser.
  const apiUrl =
    raw.startsWith("http://") || raw.startsWith("https://")
      ? raw
      : new URL(raw, window.location.href).href;
  return new Client({
    apiUrl,
  });
};

export const createThread = async () => {
  const client = createClient();
  // LangGraph /threads requires a JSON body (even if empty).
  // If we omit it, the server returns 422 and the UI ends up with no thread_id,
  // which later surfaces as "Thread not found" when streaming.
  return client.threads.create({});
};

export const getThreadState = async (
  threadId: string,
): Promise<ThreadState<{ messages: LangChainMessage[] }>> => {
  const client = createClient();
  return client.threads.getState(threadId);
};

export const sendMessage = async (params: {
  threadId: string;
  messages?: LangChainMessage[];
  command?: LangGraphCommand | undefined;
}) => {
  const client = createClient();
  // Use "messages" mode - library runtime can handle this
  // "values" mode causes tool results to be ignored (issue #2166)
  const streamMode: ("messages" | "updates" | "values")[] = ["messages"];
  const payload = {
    input: params.messages?.length
      ? {
          messages: params.messages,
        }
      : null,
    command: params.command,
    streamMode,
  };

  // Stateful run against an existing thread, auto-create if missing.
  return client.runs.stream(
    params.threadId,
    process.env["NEXT_PUBLIC_LANGGRAPH_ASSISTANT_ID"]!,
    {
      ...payload,
      ifNotExists: "create",
    },
  );
};
