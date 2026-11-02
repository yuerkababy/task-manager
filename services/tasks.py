from services.users import get_user
from utils.errors import NotFoundError, ValidationError

TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1, "priority": 1, "estimate": 1, "archived": False},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1, "priority": 3, "estimate": 5, "archived": False},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2, "priority": 5, "estimate": 8, "archived": False},
}

_UNSET = object()

def process_order(task_id: int) -> dict:
    task = TASKS[task_id]
    task["done"] = True
    return task

def get_task(task_id: int) -> dict:
    """Retrieve a task by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    return TASKS[task_id]

def _validate_priority(priority: int) -> None:
    """Check that a priority value is valid.

    Args:
        priority: The priority to check, from 1 (urgent) to 5 (low).

    Raises:
        ValidationError: If priority is not an integer from 1 to 5.
    """
    if isinstance(priority, bool) or not isinstance(priority, int) or not 1 <= priority <= 5:
        raise ValidationError("priority", "must be an integer from 1 to 5")

def _validate_estimate(estimate: int) -> None:
    """Check that an estimate value is valid.

    Args:
        estimate: The estimate to check, from 1 to 8.

    Raises:
        ValidationError: If estimate is not an integer from 1 to 8.
    """
    if isinstance(estimate, bool) or not isinstance(estimate, int) or not 1 <= estimate <= 8:
        raise ValidationError("estimate", "must be an integer from 1 to 8")

def create_task(title: str, user_id: int, priority: int = 3, estimate: int = 1) -> dict:
    """Create a new task.

    Args:
        title: The task's title.
        user_id: The ID of the user who owns the task.
        priority: The task's priority, from 1 (urgent) to 5 (low). Defaults to 3.
        estimate: The task's estimate, from 1 to 8. Defaults to 1.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is empty, priority is not an integer from 1 to 5,
            or estimate is not an integer from 1 to 8.
    """
    if not title or not title.strip():
        raise ValidationError("title", "cannot be empty")
    _validate_priority(priority)
    _validate_estimate(estimate)
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {
        "id": new_id, "title": title, "done": False, "user_id": user_id,
        "priority": priority, "estimate": estimate, "archived": False,
    }
    return TASKS[new_id]

def update_task(task_id: int, priority: int, estimate: int | object = _UNSET) -> dict:
    """Update a task's priority and, optionally, its estimate.

    Args:
        task_id: The unique identifier for the task.
        priority: The new priority, from 1 (urgent) to 5 (low).
        estimate: The new estimate, from 1 to 8. If omitted, the estimate is unchanged.

    Returns:
        The updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If priority is not an integer from 1 to 5, or estimate is
            given and is not an integer from 1 to 8.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    _validate_priority(priority)
    if estimate is not _UNSET:
        _validate_estimate(estimate)
        TASKS[task_id]["estimate"] = estimate
    TASKS[task_id]["priority"] = priority
    return TASKS[task_id]

def archive_task(task_id: int) -> dict:
    """Archive a task so it is hidden from list_tasks by default.

    Archiving a task that is already archived leaves it unchanged.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The archived task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    TASKS[task_id]["archived"] = True
    return TASKS[task_id]

def _parse_include_archived(include_archived: bool | str | None) -> bool:
    """Convert an include_archived value to a bool.

    Args:
        include_archived: A bool, None (treated as False), or a string such as a raw
            query parameter, "true" or "false" (case-insensitive).

    Returns:
        True if archived tasks should be included, otherwise False.

    Raises:
        ValidationError: If include_archived is a string other than "true" or "false",
            or is not a bool, string, or None.
    """
    if include_archived is None:
        return False
    if isinstance(include_archived, bool):
        return include_archived
    if isinstance(include_archived, str):
        value = include_archived.lower()
        if value == "true":
            return True
        if value == "false":
            return False
    raise ValidationError("include_archived", "must be true or false")

def get_tasks_for_user(user_id: int) -> list[dict]:
    """Retrieve all tasks owned by a user.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A list of the user's task records (empty if the user has no tasks).

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    get_user(user_id)
    return [task for task in TASKS.values() if task["user_id"] == user_id]

def search_tasks(query: str) -> list[dict]:
    """Retrieve tasks whose title or description contains a keyword, case-insensitive.

    Args:
        query: The text to search for.

    Returns:
        A list of matching task records (empty if none match).

    Raises:
        ValidationError: If query is empty or only whitespace.
    """
    if not query or not query.strip():
        raise ValidationError("q", "cannot be empty")
    needle = query.strip().casefold()
    return [
        task for task in TASKS.values()
        if needle in task["title"].casefold()
        or needle in task.get("description", "").casefold()
    ]

def list_tasks(
    priority: int | str | None = None,
    estimate: int | str | None = None,
    q: str | None = None,
    include_archived: bool | str | None = False,
) -> list[dict]:
    """Retrieve tasks, optionally filtered by priority, estimate, and/or keyword.

    Archived tasks are excluded unless include_archived is true.

    Args:
        priority: If given, only return tasks with this priority, from 1 (urgent) to 5 (low).
            A string (such as a raw query parameter) is converted to an integer first.
        estimate: If given, only return tasks with this estimate, from 1 to 8.
            A string (such as a raw query parameter) is converted to an integer first.
        q: If given, only return tasks whose title or description contains this text,
            case-insensitive.
        include_archived: If true, also return archived tasks. Accepts a bool, None
            (treated as False), or "true"/"false" (case-insensitive). Defaults to False.

    Returns:
        A list of task records (empty if no tasks match).

    Raises:
        ValidationError: If priority is given and is not an integer from 1 to 5,
            estimate is given and is not an integer from 1 to 8, q is given and is
            empty or only whitespace, or include_archived is not a valid true/false value.
    """
    include_archived = _parse_include_archived(include_archived)
    tasks = search_tasks(q) if q is not None else list(TASKS.values())
    if not include_archived:
        tasks = [task for task in tasks if not task.get("archived", False)]
    if priority is not None:
        if isinstance(priority, str):
            try:
                priority = int(priority)
            except ValueError:
                raise ValidationError("priority", "must be an integer from 1 to 5") from None
        _validate_priority(priority)
        tasks = [task for task in tasks if task["priority"] == priority]
    if estimate is not None:
        if isinstance(estimate, str):
            try:
                estimate = int(estimate)
            except ValueError:
                raise ValidationError("estimate", "must be an integer from 1 to 8") from None
        _validate_estimate(estimate)
        tasks = [task for task in tasks if task["estimate"] == estimate]
    return tasks
