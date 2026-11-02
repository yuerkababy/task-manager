# Git Policy: for task-manager (4-person team, all using Claude Code)

## Setup (each teammate, once)
| Rule | Mechanism |
|---|---|
| Run `git config core.hooksPath .githooks` after cloning; git does not copy this setting with the repo. | Human (setup checklist) |
| Launch Claude Code from the repo root so `.claude/settings.json`, hooks and commands load. | Human |

## Branches and commits
| Rule | Mechanism |
|---|---|
| Branches are `feat/<name>`, `fix/<name>` or `chore/<name>`, created from an up-to-date `main`. | CLAUDE.md (Git Conventions) |
| Feature work never commits to `main`; `main` receives merges and small chore/docs commits only. | CLAUDE.md + human review |
| Subjects are `type(scope): subject` or `type: subject`, type in feat/fix/test/refactor/docs/chore, at most 72 characters. | Git hook (`.githooks/commit-msg`) |
| Merge commits use a conventional subject, e.g. `chore: merge feat/search into main`. | Git hook (rejects git's default `Merge branch ...`) |
| Commits go through `/ship`: leftover check (print/breakpoint, TODO/FIXME markers, commented-out code), `pytest -q`, `ruff check .`. | Slash command (`/ship`) |
| Claude cannot commit without a person approving the exact command. | Permission setting (`"ask": ["Bash(git commit *)"]`) |
| Claude never pushes to `main`/`master`, force-pushes, or uses `--no-verify`. | Claude Code hook (`guard_git.py`) |

## Attribution
We **drop** the `Co-Authored-By: Claude` trailer. Every teammate uses Claude Code, so the trailer would appear on nearly every commit and tell a reviewer nothing. The commit-msg hook rejects any extra lines after the subject as a backstop. Mechanism: git hook.

## Parallel worktrees vs. sequential work
| Rule | Mechanism |
|---|---|
| Use parallel worktrees (`.claude/worktrees/<name>`, gitignored) when features touch different functions or files. | Human decision at planning |
| Work sequentially when two features change the same function or schema or one depends on the other. The second feature then plans against the first one's real code. | Human decision at planning |
| Safety-kit fixes (hooks, settings, `/ship`) go on `main` in their own commit first, then into open branches with `git merge --ff-only main` or `git merge main`. They never ride inside a feature branch. | Human review |

## Review and merge rules
| Rule | Mechanism |
|---|---|
| The author reviews the full diff with `/diff` before running `/ship`. | Human review (no tool enforces this) |
| Every merge into `main` needs one human reviewer other than the author. | Human review |
| A merge that needed conflict resolution needs a second reviewer, plus a short note: each conflict, what each side intended, and the chosen behavior. | Human review |
| Any change to an existing test (edit, delete, loosen) needs reviewer sign-off and a written justification; Claude must stop and ask instead of weakening a test. | CLAUDE.md + human review |
| Only people edit `.claude/hooks/`, `.claude/settings.json` and `utils/errors.py`; changes get their own commit and a reviewer. | Claude Code hook (`guard_writes.py`) + human review |
| `pytest -q` passes after every merge, with no weakened tests. | Slash command (`/ship`) + human review |