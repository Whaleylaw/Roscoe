"""
Deep Agent Coder - CLI Argument Tests

Tests for the command-line interface in cli.py.
"""

import pytest
import argparse
import sys
from unittest.mock import patch, MagicMock
from io import StringIO


class TestCLIImports:
    """Test that cli module imports work."""

    def test_import_cli_module(self):
        """Test that cli module can be imported."""
        from deep_agent_coder import cli

        assert cli is not None

    def test_import_main_function(self):
        """Test that main function can be imported."""
        from deep_agent_coder.cli import main

        assert main is not None
        assert callable(main)

    def test_import_cmd_functions(self):
        """Test that command functions can be imported."""
        from deep_agent_coder.cli import cmd_new, cmd_continue, cmd_status, cmd_chat

        assert cmd_new is not None
        assert cmd_continue is not None
        assert cmd_status is not None
        assert cmd_chat is not None


class TestHelpCommands:
    """Test --help for main and all subcommands."""

    def test_help_command(self):
        """Test main --help displays help message."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    main()

            assert exc_info.value.code == 0

    def test_help_shows_description(self):
        """Test that --help shows the description."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--help']):
            with pytest.raises(SystemExit):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    main()
                    output = mock_stdout.getvalue()
                    assert 'Deep Agent Coder' in output

    def test_new_help_command(self):
        """Test 'new --help' displays help for new command."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'new', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new_callable=StringIO):
                    main()

            assert exc_info.value.code == 0

    def test_continue_help_command(self):
        """Test 'continue --help' displays help for continue command."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new_callable=StringIO):
                    main()

            assert exc_info.value.code == 0

    def test_status_help_command(self):
        """Test 'status --help' displays help for status command."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'status', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new_callable=StringIO):
                    main()

            assert exc_info.value.code == 0

    def test_chat_help_command(self):
        """Test 'chat --help' displays help for chat command."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'chat', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new_callable=StringIO):
                    main()

            assert exc_info.value.code == 0


class TestNewCommand:
    """Test argument parsing for 'new' command."""

    def test_new_command_parsing(self):
        """Test that 'new' command parses correctly."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'new', 'my-project']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                # Verify the command was called
                assert mock_cmd.called

                # Verify arguments
                args = mock_cmd.call_args[0][0]
                assert args.project == 'my-project'
                assert args.command == 'new'

    def test_new_command_with_no_project_name(self):
        """Test 'new' command without project name."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'new']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.project is None

    def test_new_command_with_interactive_flag(self):
        """Test 'new' command with --interactive flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'new', 'my-project', '--interactive']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.interactive is True

    def test_new_command_with_interactive_short_flag(self):
        """Test 'new' command with -i flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'new', 'my-project', '-i']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.interactive is True

    def test_new_command_with_workspace_flag(self):
        """Test 'new' command with --workspace flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--workspace', '/tmp/workspace', 'new', 'my-project']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/tmp/workspace'

    def test_new_command_with_simple_flag(self):
        """Test 'new' command with --simple flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--simple', 'new', 'my-project']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.simple is True

    def test_new_command_default_workspace(self):
        """Test 'new' command uses default workspace."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'new', 'my-project']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/workspace'


class TestContinueCommand:
    """Test argument parsing for 'continue' command."""

    def test_continue_command_parsing(self):
        """Test that 'continue' command parses correctly."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', 'my-thread-123']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                # Verify the command was called
                assert mock_cmd.called

                # Verify arguments
                args = mock_cmd.call_args[0][0]
                assert args.thread_id == 'my-thread-123'
                assert args.command == 'continue'

    def test_continue_command_requires_thread_id(self):
        """Test that 'continue' command requires thread_id."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stderr', new_callable=StringIO):
                    main()

            # argparse exits with code 2 for missing required arguments
            assert exc_info.value.code == 2

    def test_continue_command_with_message_flag(self):
        """Test 'continue' command with --message flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', 'my-thread-123', '--message', 'Hello']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.message == 'Hello'

    def test_continue_command_with_message_short_flag(self):
        """Test 'continue' command with -m flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', 'my-thread-123', '-m', 'Hello']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.message == 'Hello'

    def test_continue_command_with_interactive_flag(self):
        """Test 'continue' command with --interactive flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', 'my-thread-123', '--interactive']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.interactive is True

    def test_continue_command_with_interactive_short_flag(self):
        """Test 'continue' command with -i flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', 'my-thread-123', '-i']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.interactive is True

    def test_continue_command_with_simple_flag(self):
        """Test 'continue' command with --simple flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--simple', 'continue', 'my-thread-123']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.simple is True

    def test_continue_command_without_message(self):
        """Test 'continue' command without message uses default."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'continue', 'my-thread-123']):
            with patch('deep_agent_coder.cli.cmd_continue') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.message is None


class TestStatusCommand:
    """Test argument parsing for 'status' command."""

    def test_status_command_parsing(self):
        """Test that 'status' command parses correctly."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'status']):
            with patch('deep_agent_coder.cli.cmd_status') as mock_cmd:
                main()

                # Verify the command was called
                assert mock_cmd.called

                # Verify arguments
                args = mock_cmd.call_args[0][0]
                assert args.command == 'status'

    def test_status_command_with_project_name(self):
        """Test 'status' command with project name."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'status', 'my-project']):
            with patch('deep_agent_coder.cli.cmd_status') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.project == 'my-project'

    def test_status_command_without_project_name(self):
        """Test 'status' command without project name."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'status']):
            with patch('deep_agent_coder.cli.cmd_status') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.project is None

    def test_status_command_with_workspace_flag(self):
        """Test 'status' command with --workspace flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--workspace', '/tmp/workspace', 'status']):
            with patch('deep_agent_coder.cli.cmd_status') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/tmp/workspace'


class TestChatCommand:
    """Test argument parsing for 'chat' command."""

    def test_chat_command_parsing(self):
        """Test that 'chat' command parses correctly."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'chat']):
            with patch('deep_agent_coder.cli.cmd_chat') as mock_cmd:
                main()

                # Verify the command was called
                assert mock_cmd.called

                # Verify arguments
                args = mock_cmd.call_args[0][0]
                assert args.command == 'chat'

    def test_chat_command_with_simple_flag(self):
        """Test 'chat' command with --simple flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--simple', 'chat']):
            with patch('deep_agent_coder.cli.cmd_chat') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.simple is True

    def test_chat_command_with_workspace_flag(self):
        """Test 'chat' command with --workspace flag."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '--workspace', '/tmp/workspace', 'chat']):
            with patch('deep_agent_coder.cli.cmd_chat') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/tmp/workspace'

    def test_chat_command_default_workspace(self):
        """Test 'chat' command uses default workspace."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'chat']):
            with patch('deep_agent_coder.cli.cmd_chat') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/workspace'


class TestMainBehavior:
    """Test main function behavior."""

    def test_main_no_command_shows_help(self):
        """Test that running with no command shows help and exits."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stdout', new_callable=StringIO):
                    main()

            assert exc_info.value.code == 1

    def test_main_invalid_command_exits(self):
        """Test that invalid command causes exit."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', 'invalid-command']):
            with pytest.raises(SystemExit) as exc_info:
                with patch('sys.stderr', new_callable=StringIO):
                    main()

            # argparse exits with code 2 for invalid arguments
            assert exc_info.value.code == 2


class TestGlobalFlags:
    """Test global flags that apply to all commands."""

    def test_workspace_short_flag(self):
        """Test -w short flag for workspace."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '-w', '/custom/workspace', 'status']):
            with patch('deep_agent_coder.cli.cmd_status') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/custom/workspace'

    def test_simple_short_flag(self):
        """Test -s short flag for simple mode."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '-s', 'chat']):
            with patch('deep_agent_coder.cli.cmd_chat') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.simple is True

    def test_global_flags_before_subcommand(self):
        """Test that global flags work before subcommand."""
        from deep_agent_coder.cli import main

        with patch('sys.argv', ['deep_agent_coder', '-w', '/custom', '-s', 'new', 'project']):
            with patch('deep_agent_coder.cli.cmd_new') as mock_cmd:
                main()

                args = mock_cmd.call_args[0][0]
                assert args.workspace == '/custom'
                assert args.simple is True
                assert args.project == 'project'
