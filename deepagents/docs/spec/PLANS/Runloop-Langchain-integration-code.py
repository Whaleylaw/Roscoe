from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from runloop_api_client import Runloop
import os

# Initialize client
runloop = Runloop() # API Key is automatically loaded from "RUNLOOP_API_KEY" environment variable

def generate_maze_creator():
    try: 
        # Generate code using OpenAI
        llm = ChatOpenAI(model="gpt-4o")
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", prompt)
        ])
        output_parser = StrOutputParser()

        # Create and run the chain
        chain = prompt_template | llm | output_parser
        maze_generation_script = chain.invoke({"input": prompt})

        # Execute the script in a Devbox
        devbox = runloop.devboxes.create_and_await_running()
        print("Devbox ID:", devbox.id)

        runloop.devboxes.write_file_contents(devbox.id,
         file_path= "gen_maze.py",
         contents= maze_generation_script
         )

        result = runloop.devboxes.execute(devbox.id,
            command= "python gen_maze.py --size 10"
        )

        if not result.exit_status:
            print("Maze generated successfully\n", result.stdout)
        else:
            print("Script execution failed:", result.stderr)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    generate_maze_creator()