# CopilotKit v1.50 Pre-Release Packet

Hi everyone - thanks again for signing up for the CopilotKit v1.50 pre-release.  We’ve been working for a while now on this significant upgrade, and appreciate your help in making sure it is ready for the rest of the world.

This page explains: 

- Getting Started
- What is Included in CopilotKit v1.50
- Sharing Feedback and Getting Help

# Getting Started

Make sure to set your CopilotKit version to `^1.50.0-beta.3`

PNPM Install:
`pnpm add @copilotkit/react-core@beta @copilotkit/react-ui@beta @copilotkit/runtime@beta`

Note that we are still working on docs, and examples and some of the fit and finish on the release.  We appreciate your patience and determination.  Please do not hesitate to [share feedback or ask for help](https://www.notion.so/2b63aa381852812bb4f3fdabc89a6d94?pvs=21)!

---

# What is Included in CopilotKit v1.50

CopilotKit v1.50 is a major update.  It includes many highly sought after new features, under the hood improvements and simplifications, and extensive improvements to existing core elements:

| [**Threads and Persistence**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | Multiple, long running and resumable, agent conversations |
| --- | --- |
| [**useAgent**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | Superset of useCoAgent with more control, including: Shared State, Time Travel, Multi-Agent Execution and Agent Mutual Awareness |
| [**New Design System**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | Deeper UX customization |
| [**Direct to LLM** **Improvements**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | Shared state
Additional supported LLMs |
| [**Zod schema support**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | Type safe compilation and runtime |
| [**Simplified Infrastructure**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | Removal of GraphQL |
| [**Backwards Compatibility**](https://www.notion.so/CopilotKit-v1-50-Pre-Release-Packet-2b23aa381852800fae86ca323de6fc1e?pvs=21) | All CopilotKit v 1.10 compatible apps can be updated to v 1.50 with no required coding changes |

## Backwards Compatibility

Everything you’re already using continues to work.  v1.50 is fully backwards compatible with client code using v1.10.  In fact, as a first step in this pre-release period, we would love for you to start with just rebuilding, and let us know if you run into any problems.

### V2 interfaces

As we said above, all of the v1 (or unversioned) hooks continue to work with v1.50.  To take advantage of new hooks you’ll use those marked as /v2 (shown below).

You can opt into any of the new developer interfaces or keep using the old ones. Mixing is allowed in the following configurations:

- New Chat component + old hooks
- Old components + new hooks
- New v2 APIs are exposed under a subpath:
    
    ```tsx
    import { CopilotChat, useAgent } from "@copilotkit/react-core/v2";
    ```
    

## **Threads & Persistence**

v1.50 delivers support for threaded conversations, with built in thread storage and connection components.  Support for development with InMemory or SQLite is provided out of the box.

- Thread storage
    - **For development:** `InMemory` or `SQLite` out of the box
        
        ```tsx
        import { CopilotRuntime } from "@copilotkit/runtime";
        
        const runtime = new CopilotRuntime({
          agents: {
            default: agent,
          },
          runner: new InMemoryAgentRunner(), // new abstraction for persistence
        });
        ```
        
    - **For production**
        - **Coming soon! -** Use **Copilot Cloud** (managed) or **Copilot Enterprise** (self hosted) to persist threads to your own databases, get automatic stream reconnection, in-built product analytics.
            - **👉 Join the [Enterprise Early Access](https://go.copilotkit.ai/enterprise-threads-waitlist) waitlist!**
        
- Thread connection
    - Loading a thread
        
        ```tsx
        import { CopilotChat } from "@copilotkit/react-core/v2"
        
        <CopilotChat threadId="xyz" /> // connects to runtime's runner
        ```
        
    - Stream reconnection
        
        ```tsx
        import { CopilotChat } from "@copilotkit/react-core/v2"
        
        <CopilotChat threadId="xyz" /> // will reconnect if page is reloaded
        ```
        

---

## **`useAgent`**

The v2 hook useAgent is a proper superset of `useCoAgent` which gives more control over the agent connection, including:

- Shared state
    
    ```tsx
    import { useAgent } from "@copilotkit/react-core/v2";
    
    const { agent } = useAgent({ agentId: "my-agent" });
    
    agent.state
    agent.setState
    ```
    
- Time travel
    
    ```tsx
    import { useAgent } from "@copilotkit/react-core/v2";
    
    const { agent } = useAgent({ agentId: "my-agent" });
    
    agent.setMessages()
    ```
    
- Multi-agent execution
    
    ```tsx
    import { useAgent } from "@copilotkit/react-core/v2";
    
    const { agent: langgraph } = useAgent({ agentId: "langgraph" });
    const { agent: pydantic } = useAgent({ agentId: "pydantic" });
    
    [langgraph, pydantic].forEach((agent) => {
      agent.addMessage({ id: crypto.randomUUID(), role: "user", content: message });
      agent.runAgent();
    });
    ```
    
- You can even make Agents aware of each other
    
    ```tsx
    import { useAgent } from "@copilotkit/react-core/v2";
    
    const { agent: langgraph } = useAgent({ agentId: "langgraph" });
    const { agent: pydantic } = useAgent({ agentId: "pydantic" });
    
    langgraph.setMessages(pydantic.messages)
    pydantic.setMessages(langgraph.messages)
    ```
    

---

## **New Design System**

You can continue to use the design system in the v1 interfaces, but v2 provides A full UI overhaul with deeper customization:

- New `CopilotChat`, `CopilotSidebar`, `CopilotPopup`
    - Just an import away at `@copilotkit/react-core/v2`
    - New slot system for flexible overrides
    - Much better out-of-the-box markdown rendering
- Suggestions API that works cleanly with agents

---

## Zod Schema Support

Many CopilotKit hooks now take Zod schemas, enforcing type safety at both compile and run time.

- `useHumanInTheLoop` - now takes Zod schemas
- `useFrontendTool` - now takes Zod schemas
- `useRenderToolCall` - new dev-experience principles

---

## Simplified Infrastructure

Earlier versions of CopilotKit required GraphQL installation.  That is completely removed by the new architecture.

---

## **Direct to LLM Improvements**

Our direct to LLM integration now supports more models and implements shared state.

- BasicAgent - Now with broader model support

```tsx
import { BasicAgent } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  agents: {
    myBasicAgent: new BasicAgent({
		  model: "openai/gpt-4o", // much broader model support
		  prompt: "You are a helpful AI assistant.",
		  temperature: 0.7,
		});
  },
});
```

- Shared state support

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

const { agent } = useAgent({agentId: "myBasicAgent"});  
const { state, setState } = agent;
```

---

# Sharing Feedback and Getting Help

### Find an issue? We’d Love Your Feedback

If you run into anything unexpected:

→ **Please raise an issue in the v1.50 beta [Discord support channel](https://go.copilotkit.ai/v150-discord-support-channel)**

Your feedback is incredibly valuable at this stage.

### Does Your Team Need Help?

If you’re using CopilotKit in a production product or business, we’d love to help.

You can schedule time with the team here:

👉 [Scheduling link](https://calendly.com/d/cnqt-yr9-hxr/talk-to-copilotkit?)