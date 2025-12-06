"""
Deep Agent Coder - Command Line Interface

Usage:
    python -m deep_agent_coder new [project_name]
    python -m deep_agent_coder continue <thread_id>
    python -m deep_agent_coder status [project_name]
    python -m deep_agent_coder chat  # Interactive REPL
"""

import argparse
import uuid
import json
import sys
from pathlib import Path

from .agent import create_coder_agent, create_simple_agent


def run_agent(agent, thread_id: str, message: str):
    """Run the agent with a single message and return the response."""
    config = {"configurable": {"thread_id": thread_id}}
    
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )
    
    # Get the last AI message
    for msg in reversed(result["messages"]):
        if msg.type == "ai" and msg.content:
            return msg.content
    
    return "No response generated."


def interactive_chat(agent, thread_id: str):
    """Run an interactive chat session with the agent."""
    print(f"\n🤖 Deep Agent Coder")
    print(f"📋 Thread: {thread_id}")
    print(f"Type 'quit' or 'exit' to end the session.\n")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ("quit", "exit", "q"):
                print("\nGoodbye! Thread saved for later.")
                break
            
            if not user_input:
                continue
            
            print("\n🔄 Thinking...\n")
            
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
            
            # Print the response
            for msg in reversed(result["messages"]):
                if msg.type == "ai" and msg.content:
                    print(f"Agent: {msg.content}\n")
                    break
                    
        except KeyboardInterrupt:
            print("\n\nInterrupted. Thread saved for later.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def cmd_new(args):
    """Start a new project/thread."""
    project_name = args.project or "project"
    thread_id = f"{project_name}-{uuid.uuid4().hex[:8]}"
    
    print(f"🚀 Starting new project: {project_name}")
    print(f"📋 Thread ID: {thread_id}")
    print(f"💾 Save this ID to continue later!\n")
    
    if args.simple:
        agent = create_simple_agent(workspace_dir=args.workspace)
    else:
        agent = create_coder_agent(workspace_dir=args.workspace)
    
    initial_message = f"""
    Starting new project: {project_name}
    
    Please:
    1. Check /memories/projects/{project_name}/ for any existing state
    2. If this is truly new, ask me about requirements
    3. Create the project structure in /workspace/{project_name}/
    """
    
    if args.interactive:
        interactive_chat(agent, thread_id)
    else:
        response = run_agent(agent, thread_id, initial_message)
        print(f"Agent: {response}")


def cmd_continue(args):
    """Continue an existing thread."""
    thread_id = args.thread_id
    
    print(f"📋 Continuing thread: {thread_id}")
    
    if args.simple:
        agent = create_simple_agent(workspace_dir=args.workspace)
    else:
        agent = create_coder_agent(workspace_dir=args.workspace)
    
    if args.interactive:
        interactive_chat(agent, thread_id)
    else:
        message = args.message or "What's the current status? What should we work on next?"
        response = run_agent(agent, thread_id, message)
        print(f"Agent: {response}")


def cmd_status(args):
    """Show status of a project or list all projects."""
    print("📊 Project Status\n")
    
    # This would read from /memories/projects/ but we need the agent to do that
    # For now, just show the workspace
    workspace = Path(args.workspace)
    
    if workspace.exists():
        print(f"Workspace: {workspace.absolute()}\n")
        for item in workspace.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                print(f"  📁 {item.name}/")
    else:
        print(f"Workspace not found: {workspace}")


def cmd_chat(args):
    """Start interactive chat (new thread)."""
    thread_id = f"chat-{uuid.uuid4().hex[:8]}"
    
    if args.simple:
        agent = create_simple_agent(workspace_dir=args.workspace)
    else:
        agent = create_coder_agent(workspace_dir=args.workspace)
    
    interactive_chat(agent, thread_id)


def main():
    parser = argparse.ArgumentParser(
        description="Deep Agent Coder - Multi-agent coding assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m deep_agent_coder new my-app
  python -m deep_agent_coder continue my-app-a1b2c3d4
  python -m deep_agent_coder chat --simple
        """,
    )
    
    parser.add_argument(
        "--workspace", "-w",
        default="/workspace",
        help="Workspace directory for code files (default: /workspace)",
    )
    parser.add_argument(
        "--simple", "-s",
        action="store_true",
        help="Use in-memory storage instead of Postgres (for testing)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # new command
    new_parser = subparsers.add_parser("new", help="Start a new project")
    new_parser.add_argument("project", nargs="?", help="Project name")
    new_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    new_parser.set_defaults(func=cmd_new)
    
    # continue command
    continue_parser = subparsers.add_parser("continue", help="Continue an existing thread")
    continue_parser.add_argument("thread_id", help="Thread ID to continue")
    continue_parser.add_argument("--message", "-m", help="Message to send")
    continue_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    continue_parser.set_defaults(func=cmd_continue)
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show project status")
    status_parser.add_argument("project", nargs="?", help="Project name")
    status_parser.set_defaults(func=cmd_status)
    
    # chat command
    chat_parser = subparsers.add_parser("chat", help="Interactive chat session")
    chat_parser.set_defaults(func=cmd_chat)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
