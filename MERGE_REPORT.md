# Merge Report

## Merge 1: `feat/search` into `main`

No conflicts. `main` only had the hook fix, which `feat/search` already contained. I merged with `--no-ff` so the history shows the branch. My commit-msg hook rejected git's default message `Merge branch 'feat/search'` because it is not a conventional commit, so I completed the merge with `chore: merge feat/search into main` instead of skipping the hook.

## Merge 2: `feat/archive` into `main`

Four files conflicted. I resolved them with Claude, which explained each side and proposed a resolution, and I approved each decision.

### 1. `services/tasks.py`: `list_tasks` signature, docstring and body
- **Search intended:** add `q: str | None = None`; when given, start from `search_tasks(q)` instead of all tasks.
- **Archive intended:** add `include_archived: bool | str | None = False`, parse it with `_parse_include_archived`, and drop archived tasks unless it is true.
- **Resolution:** keep both parameters, `q` first and `include_archived` last; every caller passes them by keyword, so the order does not affect callers. Order in the body: parse `include_archived`, choose the starting list (search results or all tasks), hide archived tasks, then apply the priority/estimate filters. The docstring documents both parameters and all `ValidationError` cases.
- **Why:** filtering archived tasks after the search means `?q=` hides archived matches by default, the same as every other listing filter. I used `task.get("archived", False)` so a task without the field can never raise a raw `KeyError`.

### 2. `routes/api.py`: `list_tasks_route`
- **Search intended:** pass `q=request.args.get("q")`.
- **Archive intended:** pass `include_archived=request.args.get("include_archived")`.
- **Resolution:** pass both, as keywords, in a single `list_tasks` call. The route still has no logic, per CLAUDE.md.

### 3. `tests/test_tasks.py`: imports and appended tests
- **Search intended:** import `search_tasks` and add the search tests.
- **Archive intended:** import `TASKS`, add a `_mark_archived` helper, and add the archive tests.
- **Resolution:** kept both imports and both test blocks unchanged.

### 4. `tests/test_api.py`: appended tests
- **Search intended:** three route tests for `?q=`.
- **Archive intended:** a helper plus five route tests for `include_archived`.
- **Resolution:** kept both blocks unchanged.

### Design decision: direct `search_tasks()` calls
`search_tasks` itself was left unchanged, so calling it directly still returns archived tasks. Every user-facing path (`list_tasks` and `GET /api/tasks`) hides them. I did not change `search_tasks` because neither feature asked for it, and a merge should not quietly change a function's behavior.

### Test changes
No existing test was edited, deleted or loosened. I added two tests to prove the combined behavior:
- `test_list_tasks_q_hides_archived_by_default`: an archived task matching `q` is hidden unless `include_archived=True`.
- `test_list_tasks_route_q_with_include_archived`: `?q=<word>&include_archived=true` returns the archived match.

### Final test run
```
pytest -q
.............................................................................   [100%]
77 passed in 0.50s
```