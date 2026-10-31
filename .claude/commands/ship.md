---
description: Review the diff, run tests and lint, then commit after my approval
allowed-tools: Bash(git status *) Bash(git diff *) Bash(git add *) Bash(git ls-files *) Bash(pytest -q) Bash(ruff check .)
disable-model-invocation: true
---
## Current changes
!`git status --short`
!`git diff HEAD`

## New (untracked files)
!`git ls-files --others --exclude-standard`

Follow these steps in order and stop at the first step that fails. List the file and line.

### 1. Review the lines added in this diff (including the new files lisdetd above; read them) for:
- print() or breakpoint() calls in application code
- TODO or FIXME comments added in this diff
- commented-out code

### 2. Tests and lint
Run `pytest -q` and then `ruff check .`.
If any tests fail or ruff reports anything other than the knonw F401 in routes/api.py, show the output and stop.

### 3. Propose a commit message
Propose ONE conventional commit message (type(scope): subject,
imperative mood, at most 72 characters) and wait for my approval.

### 4. Commit only after I approve: 
If I approve or give you a corrected message: stage the changed files with `git add <file> ...` (never `git add -A` or `git add .`) and then run `git commit -m "<message>"`. Lastly run `git status --short` to confirm.
If I do not approve, change nothing and run nothing.