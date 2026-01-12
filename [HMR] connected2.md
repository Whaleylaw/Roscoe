[HMR] connected
chat-panel.tsx:94 [ChatPanel] Starting stream with thread: (new)
langgraph-client.ts:151 [LangGraph] Streaming via proxy: /api/chat
langgraph-client.ts:152 [LangGraph] Thread ID: (new thread)
langgraph-client.ts:153 [LangGraph] Messages: 1
forward-logs-shared.ts:95 [Fast Refresh] rebuilding
forward-logs-shared.ts:95 [Fast Refresh] done in 412ms
langgraph-client.ts:167 [LangGraph] Thread created/used: 6d92ecff-9da6-4526-969e-e783454cb5cb
chat-panel.tsx:19 [ChatPanel] LangGraph thread created: 6d92ecff-9da6-4526-969e-e783454cb5cb
langgraph-client.ts:230 [LangGraph] Event: metadata {"run_id":"019bb288-b465-7542-ac72-8e86f8d6ced2","attempt":1}
langgraph-client.ts:234 [LangGraph] Run ID from metadata: 019bb288-b465-7542-ac72-8e86f8d6ced2
chat-panel.tsx:25 [ChatPanel] Run started: 019bb288-b465-7542-ac72-8e86f8d6ced2
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"type":"human","content":"Show me the file directory for Wayne Weber."}]}},"name":"roscoe_paralegal","tags":[],"run_id":"019bb288-b465-7542-ac72-8e86f8d6ced2","metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"name":"PatchToolCallsMiddleware.before_agent","tags":["graph:step:
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-b49e-7751-b608-36f892ef38b3","name":"PatchToolCallsMiddleware.before_agent","tags":["graph:step:1"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"messages":{"value":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"input":{"messages":[{"content":"Show me the file directory
langgraph-client.ts:230 [LangGraph] Event: updates {"PatchToolCallsMiddleware.before_agent":{"messages":{"value":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}}}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"name":"ShellToolMiddleware.before_agent","tags":["graph:step:2"],"
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-b4a0-7633-8d0f-a7a3ea24dae8","name":"ShellToolMiddleware.before_agent","tags":["graph:step:2"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":null,"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"run_id":"019bb288-b4a0-7633-8d0f-a7a3ea24dae8","name":
langgraph-client.ts:230 [LangGraph] Event: updates {"ShellToolMiddleware.before_agent":null}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"name":"SummarizationMiddleware.before_model","tags":["graph:step:3
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-b4a9-75f3-a7ec-844917a0c4a2","name":"SummarizationMiddleware.before_model","tags":["graph:step:3"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version"
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":null,"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"run_id":"019bb288-b4a9-75f3-a7ec-844917a0c4a2","name":
langgraph-client.ts:230 [LangGraph] Event: updates {"SummarizationMiddleware.before_model":null}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"}]}},"name":"model","tags":["graph:step:4"],"run_id":"019bb288-b4ad-7f12
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":[{"content":"I am Roscoe, an experienced paralegal specializing in personal injury litigation. My core identity is built around precision, organization, and proactive client service.\n\n## Professional Philosophy\n\nI follow systematic approaches to minimize
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_start","data":{"input":{"messages":[[{"content":"I am Roscoe, an experienced paralegal specializing in personal injury litigation. My core identity is built around precision, organization, and proactive client service.\n\n## Professional Philosophy\n\nI follow systematic appr
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_call
langgraph-client.ts:230 [LangGraph] Event: messages/metadata {"lc_run--019bb288-b81f-7b32-958e-2f447f644be6":{"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.30","langgraph_plan":"developer","langgraph_host":"self-hosted","langgraph_api_url":"http:
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null}]
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"I","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[],
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":
langgraph-client.ts:334 [LangGraph] Message content: I
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"'ll generate","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[],"usag
langgraph-client.ts:334 [LangGraph] Message content: I'll generate
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" an","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[],"u
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" interactive","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an interactive
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" HTML","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an interactive HTML
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" directory browser","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invali
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_c
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an interactive HTML directory browser
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" for the","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6"
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an interactive HTML directory browser for the
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" Wayne Weber case folder","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81f
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an interactive HTML directory browser for the Wayne Weber case folder
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":".","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_calls":[],
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-b81
langgraph-client.ts:334 [LangGraph] Message content: I'll generate an interactive HTML directory browser for the Wayne Weber case folder.
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1}],"additional_kwargs":{},"response_metadata":{"model_
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[{"name"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":""}],"additional_kwargs":{},"response_
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"{\"","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[{"na
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\""}],"additional_kwargs":{},"respon
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"root","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root"}],"additional_kwargs":{},"re
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"_path\": \"","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_call
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \""}],"additional_kwa
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: ''}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"pr","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"in
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"pr"}],"additional_k
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'pr'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"oject","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"project"}],"additio
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'project'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"s/Wayne-Web","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_call
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Web"
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Web'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"er-MVA-01-01","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"-2022\"","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":", \"max_dept","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"h\": 3","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[]
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":", ","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"in
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"\"sort_by\": ","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_ca
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"\"nam","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3, sort_by: 'nam'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"partial_json":"e\"}","type":"input_json_delta","index":1}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3, sort_by: 'name'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[],"additional_kwargs":{},"response_metadata":{"stop_reason":"tool_use","stop_sequence":null,"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-b81f-7b32-958e-2f447f644be6","tool_calls":[],"invalid_tool_
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": \"projects/Wayne-Webe
langgraph-client.ts:342 [LangGraph] Tool call: generate_directory_browser
chat-panel.tsx:173 [Tool Call] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3, sort_by: 'name'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_end","data":{"output":{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-b4ad-7f12-965c-fde2a1307468","name":"model","tags":["graph:step:4"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.30","langgraph_plan":"dev
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"messages":[{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,
langgraph-client.ts:230 [LangGraph] Event: updates {"model":{"messages":[{"content":[{"text":"I'll generate an interactive HTML directory browser for the Wayne Weber case folder.","type":"text","index":0},{"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","input":{},"name":"generate_directory_browser","type":"tool_use","index":1,"partial_json":"{\"root_path\": 
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML directory brows
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-c7b9-70d1-8b1a-8abd36db4bcf","name":"TodoListMiddleware.after_model","tags":["graph:step:5"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":null,"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML dir
langgraph-client.ts:230 [LangGraph] Event: updates {"TodoListMiddleware.after_model":null}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"__type":"tool_call_with_context","tool_call":{"name":"generate_directory_browser","args":{"root_path":"projects/Wayne-Weber-MVA-01-01-2022","max_depth":3,"sort_by":"name"},"id":"toolu_01Tv1dUYD94dyEj75DDr3DUE","type":"tool_call"},"state":{"messages":[{"con
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_tool_start","data":{"input":{"root_path":"projects/Wayne-Weber-MVA-01-01-2022","max_depth":3,"sort_by":"name"}},"name":"generate_directory_browser","tags":["seq:step:1"],"run_id":"019bb288-c7c1-7740-8096-3e2b3ed30325","metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-
langgraph-client.ts:251 [LangGraph] Tool starting: generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3, sort_by: 'name'}
chat-panel.tsx:133 [Tool Start] generate_directory_browser {root_path: 'projects/Wayne-Weber-MVA-01-01-2022', max_depth: 3, sort_by: 'name'}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_tool_end","data":{"output":{"content":"✓ Directory browser generated and displayed\n\n📁 Showing: projects/Wayne-Weber-MVA-01-01-2022\n📊 Contents: 216 files, 92 folders\n💾 Saved: /Reports/directory_browser_20260112_140747.html\n\n{\"__display_document__\": true, \"path\": \"/Reports/d
langgraph-client.ts:264 [LangGraph] Tool ended: generate_directory_browser
chat-panel.tsx:154 [Tool End] generate_directory_browser {content: '✓ Directory browser generated and displayed\n\n📁 Sh…"Directory: projects/Wayne-Weber-MVA-01-01-2022"}', additional_kwargs: {…}, response_metadata: {…}, type: 'tool', name: 'generate_directory_browser', …}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-c7bd-7421-86af-345109b5ccac","name":"tools","tags":["graph:step:6"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.30","langgraph_plan":"dev
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"messages":[{"content":"✓ Directory browser generated and displayed\n\n📁 Showing: projects/Wayne-Weber-MVA-01-01-2022\n📊 Contents: 216 files, 92 folders\n💾 Saved: /Reports/directory_browser_20260112_140747.html\n\n{\"__display_document__\": true, \"path\"
langgraph-client.ts:230 [LangGraph] Event: messages/metadata {"f96a65f3-42e8-4ea9-9634-462a11319613":{"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.30","langgraph_plan":"developer","langgraph_host":"self-hosted","langgraph_api_url":"http://localh
langgraph-client.ts:230 [LangGraph] Event: messages/complete [{"content":"✓ Directory browser generated and displayed\n\n📁 Showing: projects/Wayne-Weber-MVA-01-01-2022\n📊 Contents: 216 files, 92 folders\n💾 Saved: /Reports/directory_browser_20260112_140747.html\n\n{\"__display_document__\": true, \"path\": \"/Reports/directory_browser_20260112_140747.html\"
langgraph-client.ts:334 [LangGraph] Message content: ✓ Directory browser generated and displayed

📁 Showing: projects/Wayne-Weber-MVA-01-01-2022
📊 Cont...
langgraph-client.ts:230 [LangGraph] Event: updates {"tools":{"messages":[{"content":"✓ Directory browser generated and displayed\n\n📁 Showing: projects/Wayne-Weber-MVA-01-01-2022\n📊 Contents: 216 files, 92 folders\n💾 Saved: /Reports/directory_browser_20260112_140747.html\n\n{\"__display_document__\": true, \"path\": \"/Reports/directory_browser_2
langgraph-client.ts:307 [LangGraph] Tool result found: generate_directory_browser ✓ Directory browser generated and displayed

📁 Showing: projects/Wayne-Weber-MVA-01-01-2022
📊 Contents: 216 files, 92 folders
💾 Saved: /Reports/directory_browser_20260112_140747.html

{"__display_document__": true, "path": "/Reports/directory_browser_20260112_140747.html", "type": "html", "title": "Directory: projects/Wayne-Weber-MVA-01-01-2022"}
chat-panel.tsx:195 [Tool Result] generate_directory_browser Type: string
chat-panel.tsx:196 [Tool Result] Full result: ✓ Directory browser generated and displayed

📁 Showing: projects/Wayne-Weber-MVA-01-01-2022
📊 Contents: 216 files, 92 folders
💾 Saved: /Reports/directory_browser_20260112_140747.html

{"__display_document__": true, "path": "/Reports/directory_browser_20260112_140747.html", "type": "html", "title": "Directory: projects/Wayne-Weber-MVA-01-01-2022"}
chat-panel.tsx:233 [Tool Result] Checking for __display_document__, result type: string
chat-panel.tsx:235 [Tool Result] Result is string, length: 351
chat-panel.tsx:236 [Tool Result] First 500 chars: ✓ Directory browser generated and displayed

📁 Showing: projects/Wayne-Weber-MVA-01-01-2022
📊 Contents: 216 files, 92 folders
💾 Saved: /Reports/directory_browser_20260112_140747.html

{"__display_document__": true, "path": "/Reports/directory_browser_20260112_140747.html", "type": "html", "title": "Directory: projects/Wayne-Weber-MVA-01-01-2022"}
chat-panel.tsx:242 [Tool Result] JSON match found: YES
chat-panel.tsx:244 [Tool Result] Matched JSON: {"__display_document__": true, "path": "/Reports/directory_browser_20260112_140747.html", "type": "html", "title": "Directory: projects/Wayne-Weber-MVA-01-01-2022"}
chat-panel.tsx:246 [Tool Result] Parsed JSON: {__display_document__: true, path: '/Reports/directory_browser_20260112_140747.html', type: 'html', title: 'Directory: projects/Wayne-Weber-MVA-01-01-2022'}
chat-panel.tsx:248 [Tool Result] ✅ Display document requested: {__display_document__: true, path: '/Reports/directory_browser_20260112_140747.html', type: 'html', title: 'Directory: projects/Wayne-Weber-MVA-01-01-2022'}
chat-panel.tsx:259 [Tool Result] Opening document: /Reports/directory_browser_20260112_140747.html Type: html
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML directory brows
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-c7fe-7ba0-a5c9-adc93841c1b0","name":"SummarizationMiddleware.before_model","tags":["graph:step:7"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version"
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":null,"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML dir
langgraph-client.ts:230 [LangGraph] Event: updates {"SummarizationMiddleware.before_model":null}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML directory brows
forward-logs-shared.ts:95 [Fast Refresh] rebuilding
forward-logs-shared.ts:95 [Fast Refresh] done in 387ms
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":[{"content":"I am Roscoe, an experienced paralegal specializing in personal injury litigation. My core identity is built around precision, organization, and proactive client service.\n\n## Professional Philosophy\n\nI follow systematic approaches to minimize
right-panel.tsx:35  GET http://34.63.223.97:3000/api/workspace/file?path=%2FReports%2Fdirectory_browser_20260112_140747.html 500 (Internal Server Error)
RightPanel.useEffect @ right-panel.tsx:35
react_stack_bottom_frame @ react-dom-client.development.js:28101
runWithFiberInDEV @ react-dom-client.development.js:984
commitHookEffectListMount @ react-dom-client.development.js:13690
commitHookPassiveMountEffects @ react-dom-client.development.js:13777
commitPassiveMountOnFiber @ react-dom-client.development.js:16731
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16751
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16723
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:17008
recursivelyTraversePassiveMountEffects @ react-dom-client.development.js:16676
commitPassiveMountOnFiber @ react-dom-client.development.js:16766
flushPassiveEffects @ react-dom-client.development.js:19857
flushPendingEffects @ react-dom-client.development.js:19783
flushSpawnedWork @ react-dom-client.development.js:19739
commitRoot @ react-dom-client.development.js:19333
commitRootWhenReady @ react-dom-client.development.js:18176
performWorkOnRoot @ react-dom-client.development.js:18052
performSyncWorkOnRoot @ react-dom-client.development.js:20397
flushSyncWorkAcrossRoots_impl @ react-dom-client.development.js:20239
processRootScheduleInMicrotask @ react-dom-client.development.js:20278
(anonymous) @ react-dom-client.development.js:20416Understand this error
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_start","data":{"input":{"messages":[[{"content":"I am Roscoe, an experienced paralegal specializing in personal injury litigation. My core identity is built around precision, organization, and proactive client service.\n\n## Professional Philosophy\n\nI follow systematic appr
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_call
langgraph-client.ts:230 [LangGraph] Event: messages/metadata {"lc_run--019bb288-ca7a-7cb1-b517-65962376839f":{"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.30","langgraph_plan":"developer","langgraph_host":"self-hosted","langgraph_api_url":"http:
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":[],"usage_metadata":null}]
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"Perfect! I've generated an","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[]
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_ca
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" interactive directory","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"in
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_call
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" browser for the","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" Wayne Weber case.","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invali
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case.","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-ca7a-
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case.
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" You","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--019bb288-c
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" can now:","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_ca
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_run--0
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n\n-","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n-","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"lc_r
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

-
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" **","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":[
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"id":"l
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"Expan","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expan","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,"i
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"d/","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":[]
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"type":"ai","name":null,
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"collapse folders** by","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"inv
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider":"anthropic"},"ty
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" clicking on them","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_provider"
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- **See","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_ca
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","model_
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" file","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-20250929","m
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" sizes","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-202509
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" an","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":[
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes an","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-sonnet-4-5-202
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"d modification","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_to
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":"claude-
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" dates**","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_name":
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- **Navigate through the ","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the ","type":"text","index":0}],"additional_kwargs":{},"respon
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"8","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":[],
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8","type":"text","index":0}],"additional_kwargs":{},"respo
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"-bucket organization","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"inva
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization","type":"text","index":0}],"addition
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" system**","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_ca
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**","type":"text","index":0}],
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n\nThe case","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case","type":"text",
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" has","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has","type":"te
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" **","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":[
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **","type":
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"216 files across","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" 92 folders**,","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_to
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" organize","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_ca
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"d into","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" the","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" standar","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"d buc","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"kets:\n- Client","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_t
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- Investigation  ","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"inval
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- Medical Records\n- Insurance","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- Lien\n- Expenses","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"inva
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- Negotiation Settlement\n-","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls"
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" Litigation","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"\n- case","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_cal
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"_information\n\nYou","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"inval
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" can explore","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" the structure in","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" the right","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_c
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" panel.","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_call
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" Let","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_calls":
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" me know if you'","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":"d like me to look","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[{"text":" at any specific files or folders!","type":"text","index":0}],"additional_kwargs":{},"response_metadata":{"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_c
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:334 [LangGraph] Message content: Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:

- *...
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_stream","data":{"chunk":{"content":[],"additional_kwargs":{},"response_metadata":{"stop_reason":"end_turn","stop_sequence":null,"model_provider":"anthropic"},"type":"AIMessageChunk","name":null,"id":"lc_run--019bb288-ca7a-7cb1-b517-65962376839f","tool_calls":[],"invalid_tool_
langgraph-client.ts:230 [LangGraph] Event: messages/partial [{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe case has **216 files
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chat_model_end","data":{"output":{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket orga
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organizat
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-c802-75e2-88e8-b8f885bbdb50","name":"model","tags":["graph:step:8"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.30","langgraph_plan":"dev
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"messages":[{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-buc
langgraph-client.ts:230 [LangGraph] Event: updates {"model":{"messages":[{"content":[{"text":"Perfect! I've generated an interactive directory browser for the Wayne Weber case. You can now:\n\n- **Expand/collapse folders** by clicking on them\n- **See file sizes and modification dates**\n- **Navigate through the 8-bucket organization system**\n\nThe
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML directory brows
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-dd05-7fb2-b019-340ec5953d23","name":"TodoListMiddleware.after_model","tags":["graph:step:9"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.6.
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":null,"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML dir
langgraph-client.ts:230 [LangGraph] Event: updates {"TodoListMiddleware.after_model":null}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_start","data":{"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML directory brows
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_stream","run_id":"019bb288-dd0a-7143-a037-70b0e9ded3d1","name":"ShellToolMiddleware.after_agent","tags":["graph:step:10"],"metadata":{"created_by":"system","assistant_id":"6a400679-513b-5045-9d51-a258e6eea81f","run_attempt":1,"langgraph_version":"1.0.5","langgraph_api_version":"0.
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":null,"input":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML dir
langgraph-client.ts:230 [LangGraph] Event: updates {"ShellToolMiddleware.after_agent":null}
langgraph-client.ts:230 [LangGraph] Event: events {"event":"on_chain_end","data":{"output":{"messages":[{"content":"Show me the file directory for Wayne Weber.","additional_kwargs":{},"response_metadata":{},"type":"human","name":null,"id":"fa93bc53-4e60-4482-ab8c-b5ea69df6126"},{"content":[{"text":"I'll generate an interactive HTML directory browse
forward-logs-shared.ts:95 [Fast Refresh] rebuilding
forward-logs-shared.ts:95 [Fast Refresh] done in 639ms
4(index):1 Uncaught (in promise) Error: A listener indicated an asynchronous response by returning true, but the message channel closed before a response was receivedUnderstand this error