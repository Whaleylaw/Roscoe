from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

model_with_code_interpreter = model.bind_tools([{"code_execution": {}}])
response = model_with_code_interpreter.invoke("Use Python to calculate 3^3.")

response.content_blocks


[{'type': 'server_tool_call',
  'name': 'code_interpreter',
  'args': {'code': 'print(3**3)', 'language': <Language.PYTHON: 1>},
  'id': '...'},
 {'type': 'server_tool_result',
  'tool_call_id': '',
  'status': 'success',
  'output': '27\n',
  'extras': {'block_type': 'code_execution_result',
   'outcome': <Outcome.OUTCOME_OK: 1>}},
 {'type': 'text', 'text': 'The calculation of 3 to the power of 3 is 27.'}]