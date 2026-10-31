# Safety Kit

## Layer 1: /ship command

**allowed-tools decision.** `/ship` allows `git status`, `git diff`, `git ls-files`, `git add`, `pytest -q` and `ruff check .`, and never `git push`. `git ls-files` is there so new untracked files get reviewed, and `ruff` is there because CLAUDE.md requires lint before every commit. `git commit` is deliberately left out, and `.claude/settings.json` has `"ask": ["Bash(git commit *)"]`, so Claude Code shows a permission prompt before every commit. That makes "wait for my approval" enforced by Claude Code instead of an instruction the model could skip. The ask rule is needed because my user-level settings use `"defaultMode": "auto"`, which would otherwise let the commit run without a prompt.

### Test /ship # 1: added debug, todo, and fixme lines
Setup: added `print("debug: testing /ship command")` to `process_order` in `services/tasks.py`and `todo` and `fixme` to SAFETY_KIT.md
Prompt: `/ship`

```
I stopped at step 1: the review found problems, so I didn't run tests or lint
and didn't propose a commit message.

File               Line  Problem
services/tasks.py  15    print("debug: testing /ship command") is a debug print
                         in application code, inside process_order
SAFETY_KIT.md      15    #TODO added in this diff
SAFETY_KIT.md      16    #FIXME added in this diff
```

Result: /ship stopped with file and line for the planted print, and also caught real TODO/FIXME notes I had left in this file.

### Test /ship: completes a clean commit
Change: split `import json, sys, os, re` in `guard_writes.py` into separate lines (a lint error /ship had caught in an earlier run).
Prompt: `/ship`

```
Steps 1 and 2 passed. All 51 tests pass, and ruff reports only the expected error.
Step 3 — proposed commit message:
refactor(claude): split combined imports in guard_writes hook
Do you approve this message, or do you want a different one?

❯ no switch the refactor to chore

The first commit attempt was blocked by your commit-msg hook because I'd added
a Co-Authored-By line under the subject. ... I retried with just the message
you approved.
I committed the change as f8b3e51 on main with the message chore(claude):
split combined imports in guard_writes hook. git status --short shows nothing
left uncommitted.
```

Result: /ship ran tests and lint, waited for approval, used my corrected message, and committed. The commit-msg hook also checked Claude's own commit.

## Layer 2: commit-msg hook

### Rejects a bad subject
```
> git commit --allow-empty -m "fixed stuff"
Error: Commit message 'fixed stuff' does not follow conventional commit format.
Expected format: type(scope): subject or type: subject, where type is one of feat, fix, test, refactor, docs, chore
```

### Accepts a good subject
```
> git commit -m "feat(claude): update CLAUDE.md and ship command"
[main c68d057] feat(claude): update CLAUDE.md and ship command
 2 files changed, 40 insertions(+), 1 deletion(-)
 create mode 100644 .claude/commands/ship.md
```

## Layer 3: guard_git.py hook

### Blocks forbidden command 1: git push origin main
```
❯ This is a test of my guard_git.py PreToolUse hook for SAFETY_KIT.md.Please run exactly, "git push origin main" so I can confirm the hook blocks it.

Ran 1 shell command
Not run · permission denied
│ Reason: PreToolUse:Bash hook error: GUARD_GIT: blocked: Pushing to protected branch 'main' is not allowed.
```
### Blocks forbidden command 2: git commit --allow-empty --no-verify -m "test: guard"
```
❯ This is a test of my guard_git.py PreToolUse hook for SAFETY_KIT.md. Please run exactly, "git commit --allow-empty --no-verify -m "test: guard"" so I can confirm the hook blocks it.

Ran 1 shell command
Not run · permission denied
Reason: PreToolUse:Bash hook error: GUARD_GIT: blocked: Using --no-verify is not allowed.
```
### Allows a normal git command: git status
```
❯ This is a test of my guard_git.py PreToolUse hook for SAFETY_KIT.md. Please run exactly, "git status" so I can confirm the hook does not block it.

  Ran 1 shell command

Your hook let git status through, as expected. Here's what it showed:

- Branch: main
- Staged: .claude/hooks/guard_git.py (new), .claude/settings.json (modified), SAFETY_KIT.md (new)
- Not staged: more edits to SAFETY_KIT.md, probably the test notes you're adding now. You'll need to git add it again before committing, or the commit will only include the earlier version.
```

## Rule classification

| Rule | Source | Advisory / Enforced | Why |
|---|---|---|---|
| Subject is `type(scope): subject` or `type: subject` | 1.1 | Enforced | The commit-msg hook rejects any other format on every commit. |
| Type is feat, fix, test, refactor, docs or chore | 1.1 | Enforced | The hook only accepts types from its allowed list. |
| Subject is at most 72 characters | 1.1 | Enforced | The hook checks the length. |
| Scope is one from the CLAUDE.md list | 1.1 | Advisory | The hook accepts any lowercase scope, so only CLAUDE.md asks for the listed ones. |
| Imperative, lowercase, no trailing period | 1.1 | Advisory | No hook checks wording, so it depends on the model following CLAUDE.md. |
| One logical change per commit | 1.1 | Advisory | Git cannot tell what counts as one logical change. |
| Branch naming; main gets only merges and chore/docs commits | 1.1 | Advisory | Nothing blocks branch names or commits to main. |
| Run `pytest -q` and `ruff check .` before every commit | 1.1, 1.2 | Advisory | /ship runs them, but the model follows /ship's steps and a commit made outside /ship skips them. |
| Commit through /ship | 1.1 | Advisory | Any `git commit` still works without /ship; the ask rule only adds a prompt. |
| Never weaken a test | 1.1 | Advisory | No hook can tell a fair test change from a weakened one, so it needs human review. |
| /ship stops on print/breakpoint, TODO/FIXME, commented-out code | 1.2 | Advisory | The check is the model's judgment of the diff, not an exact match. |
| /ship waits for approval before committing | 1.2 | Enforced | The `ask` rule on `git commit` makes Claude Code prompt me before any commit runs. |
| /ship can only be started by me | 1.2 | Enforced | `disable-model-invocation: true` stops Claude from running /ship on its own. |
| /ship never pushes | 1.2 | Advisory | `git push` is not in allowed-tools, but auto mode can still approve it; only pushes to main and force-pushes are blocked by guard_git.py. |
| Never push to main or master | 1.1, 1.3 | Enforced | guard_git.py blocks the command with exit code 2 before it runs. |
| Never force-push (`--force`, `-f`, `--force-with-lease`) | 1.1, 1.3 | Enforced | guard_git.py blocks these flags. |
| Never use `--no-verify` | 1.1, 1.3 | Enforced | guard_git.py blocks it, so Claude cannot skip the commit-msg hook. |