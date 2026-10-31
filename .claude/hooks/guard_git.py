"""PreToolUse hook: blocks any command that pushes to main/master, force pushes (--force, -f, --force-with-lease), or uses --no-verify."""

import json
import shlex
import sys
import os
import re

PROTECTED_BRANCHES = ["main", "master"]
FORCE_FLAGS = ["--force", "-f", "--force-with-lease"]

def block(message):
    print(f"GUARD_GIT: blocked: {message}", file=sys.stderr)
    sys.exit(2)

def split_command(command):
    try:
        return shlex.split(command)
    except Exception as e:
        block(f"Failed to parse command: {e}")

def check_command(command):
    tokens = split_command(command)
    cmd, subcmd = tokens[0], tokens[1]
    
    if cmd != "git":
        return

    # Check for push to protected branches
    if subcmd == "push":
        for branch in PROTECTED_BRANCHES:
            if branch in tokens:
                block(f"Pushing to protected branch '{branch}' is not allowed.")

    # Check for force push flags
    if any(flag in tokens for flag in FORCE_FLAGS):
        block("Force pushing is not allowed.")

    # Check for --no-verify flag
    if "--no-verify" in tokens:
        block("Using --no-verify is not allowed.")

def main():
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")
    for piece in re.split(r"&&|\|\||;|\|", command):
        check_command(piece)
    sys.exit(0)

if __name__ == "__main__":
    main()