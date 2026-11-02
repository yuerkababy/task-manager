# Reflection

## 1. What the safety kit caught, and what it missed

**Caught:** While building archiving, `/ship`'s lint step stopped with four `F821` errors in `.claude/hooks/guard_writes.py`. An earlier commit of mine had removed `import os` from the wrong hook file. I meant to clean up `guard_git.py` but edited `guard_writes.py`. Claude was not allowed to edit the hook, so it reported the problem instead of patching it, and I fixed it on `main` in its own commit.

**Missed:** That same bug had already been live for a while, and nothing in the kit noticed. A PreToolUse hook that crashes fails open, and my archive session log shows exactly that: a `PreToolUse:Write hook error ... Traceback` followed by `Wrote 15 lines`. The write went through. No hook checks the hooks, so the protection was silently off until ruff happened to run. The kit also could not stop me from skipping `/diff` before committing both features. I reviewed the final code only after the merge. Human review is the one gate my tools cannot enforce.

## 2. The cost of running two features in parallel

Search merged cleanly, but archiving conflicted in four files: the `list_tasks` signature and docstring, the route call, and the appended tests in both test files. The real cost was a design question neither branch could see. Should `?q=` hide archived tasks? I decided yes, kept `search_tasks` unchanged, and added two combined tests to prove it. Parallel work also cost me setup. The hook fix had to be committed on `main` and fast-forwarded into both worktrees before either could `/ship`, and my own commit-msg hook rejected git's default merge message.

For this pair it was not really worth it. Both features changed `list_tasks`, and they were small, so building archiving after search would have let its plan handle the interaction directly. Parallel worktrees make more sense for features in different files.

## 3. What I would change before my capstone

- Make hooks fail closed: wrap `guard_writes.py` and `guard_git.py` in a try/except that exits 2, and add small pytest tests for the hooks so a broken hook fails the suite.
- Fix `guard_git.py`'s parsing. It blocked a harmless command because it split on `;` inside a quoted string before parsing quotes. It should only split on separators outside quotes.
- Have the commit-msg hook check only the subject line, and make the attribution choice in settings deliberately rather than as a side effect.
- Add a step to `/ship` that shows a file-by-file summary of the diff and asks me to confirm I reviewed it, since skipping review was my biggest real gap.