Persistence
Loading Agent State
Learn how threadId is used to load previous agent states.

Setting the threadId
When setting the threadId property in CopilotKit, i.e:

When using LangGraph platform, the threadId must be a UUID.


<CopilotKit threadId="2140b272-7180-410d-9526-f66210918b13">
  <YourApp />
</CopilotKit>
CopilotKit will restore the complete state of the thread, including the messages, from the database. (See Message Persistence for more details.)

Loading Agent State
This means that the state of any agent will also be restored. For example:


const { state } = useCoAgent({name: "research_agent"});
// state will now be the state of research_agent in the thread id given above
Learn More
To learn more about persistence and state in CopilotKit, see:

Reading agent state
Writing agent state
Loading Message History
Authentication

Secure your LangGraph agents with user authentication (Platform & Self-hosted)

Threads

Learn how to load chat messages and threads within the CopilotKit framework.

On this page
Setting the threadId
Loading Agent State
Learn More
 
Persistence
Threads
Learn how to load chat messages and threads within the CopilotKit framework.

LangGraph supports threads, a way to group messages together and ultimately maintain a continuous chat history. CopilotKit provides a few different ways to interact with this concept.

This guide assumes you have already gone through the quickstart guide.

Loading an Existing Thread
To load an existing thread in CopilotKit, you can simply set the threadId property on <CopilotKit> like so.

When using LangGraph platform, the threadId must be a UUID.


import { CopilotKit } from "@copilotkit/react-core";
<CopilotKit threadId="37aa68d0-d15b-45ae-afc1-0ba6c3e11353">
  <YourApp />
</CopilotKit>
Dynamically Switching Threads
You can also make the threadId dynamic. Once it is set, CopilotKit will load the previous messages for that thread.


import { useState } from "react";
import { CopilotKit } from "@copilotkit/react-core";
const Page = () => {
  const [threadId, setThreadId] = useState("af2fa5a4-36bd-4e02-9b55-2580ab584f89"); 
  return (
    <CopilotKit threadId={threadId}>
      <YourApp setThreadId={setThreadId} />
    </CopilotKit>
  )
}
const YourApp = ({ setThreadId }) => {
  return (
    <Button onClick={() => setThreadId("679e8da5-ee9b-41b1-941b-80e0cc73a008")}>
      Change Thread
    </Button>
  )
}
Using setThreadId
CopilotKit will also return the current threadId and a setThreadId function from the useCopilotContext hook. You can use setThreadId to change the threadId.


import { useCopilotContext } from "@copilotkit/react-core";
const ChangeThreadButton = () => {
  const { threadId, setThreadId } = useCopilotContext(); 
  return (
    <Button onClick={() => setThreadId("d73c22f3-1f8e-4a93-99db-5c986068d64f")}>
      Change Thread
    </Button>
  )
}

To persist LangGraph messages to a database, you can use either AsyncPostgresSaver or AsyncSqliteSaver. Set up the asynchronous memory by configuring the graph within a lifespan function, as follows:


from fastapi import FastAPI
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from copilotkit import LangGraphAGUIAgent
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
graph = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncPostgresSaver.from_conn_string(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    ) as checkpointer:
        # NOTE: you need to call .setup() the first time you're using your checkpointer
        await checkpointer.setup()
        # Create an async graph
        graph = workflow.compile(checkpointer=checkpointer)
        yield
        # Create SDK with the graph
app = FastAPI(lifespan=lifespan)
add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="research_agent",
        description="Research agent.",
        graph=graph,
    ),
    path="/agents/research_agent"
)
To learn more about persistence in LangGraph, check out the LangGraph documentation.

