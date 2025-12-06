import { NextRequest } from "next/server";
import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  ExperimentalEmptyAdapter,
  LangGraphAgent,
} from "@copilotkit/runtime";

// Create runtime lazily to ensure env vars are loaded
function getRuntime() {
  const langGraphUrl = process.env.ROSCOE_LANGGRAPH_URL || "http://localhost:8123";
  console.log("[CopilotKit] Using LangGraph URL:", langGraphUrl);
  
  return new CopilotRuntime({
    agents: {
      roscoe_paralegal: new LangGraphAgent({
        deploymentUrl: langGraphUrl,
        graphId: "roscoe_paralegal",
      }),
    },
  });
}

const serviceAdapter = new ExperimentalEmptyAdapter();

export const POST = async (req: NextRequest) => {
  const runtime = getRuntime();
  
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/chat",
  });

  return handleRequest(req);
};
