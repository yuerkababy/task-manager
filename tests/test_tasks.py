import pytest
from services.tasks import process_order, get_task, create_task, get_tasks_for_user
from services.tasks import list_tasks
from services.tasks import update_task
from services.tasks import search_tasks
from services.tasks import TASKS
from utils.errors import NotFoundError, ValidationError

def test_process_order_valid():
    result = process_order(1)
    assert result["done"] is True

def test_process_order_invalid():
    with pytest.raises(Exception):
        process_order(999)

def test_get_task_valid():
    result = get_task(2)
    assert result["title"] == "Write report"

def test_get_task_invalid():
    with pytest.raises(Exception):
        get_task(999)

def test_get_task_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        get_task(999)

def test_create_task_valid():
    result = create_task("Walk the dog", 1)
    assert result["title"] == "Walk the dog"
    assert result["done"] is False
    assert get_task(result["id"]) is result

def test_create_task_empty_title_raises_validation_error():
    with pytest.raises(ValidationError):
        create_task("   ", 1)

def test_get_tasks_for_user_valid():
    created = create_task("Water plants", 2)
    task_ids = [task["id"] for task in get_tasks_for_user(2)]
    assert created["id"] in task_ids
    assert 3 in task_ids
    assert 1 not in task_ids

def test_get_tasks_for_user_unknown_user_raises_not_found():
    with pytest.raises(NotFoundError):
        get_tasks_for_user(999)

def test_list_tasks_all():
    task_ids = [task["id"] for task in list_tasks()]
    assert {1, 2, 3} <= set(task_ids)

def test_list_tasks_filter_by_priority():
    task_ids = [task["id"] for task in list_tasks(5)]
    assert 3 in task_ids
    assert 1 not in task_ids
    assert 2 not in task_ids

def test_list_tasks_invalid_priority_raises_validation_error():
    for priority in (0, 6, True):
        with pytest.raises(ValidationError):
            list_tasks(priority)

def test_list_tasks_string_priority():
    task_ids = [task["id"] for task in list_tasks("5")]
    assert 3 in task_ids
    with pytest.raises(ValidationError):
        list_tasks("abc")

def test_update_task_valid():
    created = create_task("Fix bike", 1, priority=3)
    result = update_task(created["id"], 1)
    assert result["priority"] == 1
    assert get_task(created["id"])["priority"] == 1

def test_update_task_missing_raises_not_found():
    with pytest.raises(NotFoundError):
        update_task(999, 2)

def test_update_task_invalid_priority_raises_validation_error():
    created = create_task("Clean garage", 1, priority=4)
    for priority in (0, 6, True, "3", None):
        with pytest.raises(ValidationError):
            update_task(created["id"], priority)
    assert get_task(created["id"])["priority"] == 4

def test_search_tasks_matches_title_case_insensitive():
    match = create_task("Feed Zephyrquill cat", 1)
    other = create_task("Unrelated chore", 1)
    task_ids = [task["id"] for task in search_tasks("zephyrQUILL")]
    assert match["id"] in task_ids
    assert other["id"] not in task_ids

def test_search_tasks_matches_description():
    created = create_task("Plain title", 1)
    created["description"] = "Talk to Marrowbeck"
    task_ids = [task["id"] for task in search_tasks("marrowbeck")]
    assert created["id"] in task_ids

def test_search_tasks_task_without_description_does_not_raise():
    created = create_task("Brindlewort errand", 1)
    assert "description" not in created
    task_ids = [task["id"] for task in search_tasks("brindlewort")]
    assert created["id"] in task_ids

def test_search_tasks_no_match_returns_empty_list():
    assert search_tasks("qqxxnomatchzz") == []

@pytest.mark.parametrize("query", ["", "   "])
def test_search_tasks_empty_query_raises_validation_error(query):
    with pytest.raises(ValidationError):
        search_tasks(query)

def test_list_tasks_q_combines_with_priority():
    urgent = create_task("Glimmerfen a", 1, priority=1)
    low = create_task("Glimmerfen b", 1, priority=5)
    task_ids = [task["id"] for task in list_tasks(priority=1, q="glimmerfen")]
    assert urgent["id"] in task_ids
    assert low["id"] not in task_ids

def _mark_archived(task: dict) -> None:
    TASKS[task["id"]]["archived"] = True

def test_archive_task_sets_archived():
    from services.tasks import archive_task
    created = create_task("Old chore", 1)
    result = archive_task(created["id"])
    assert result["archived"] is True
    assert get_task(created["id"]).get("archived") is True

def test_archive_task_missing_raises_not_found():
    from services.tasks import archive_task
    with pytest.raises(NotFoundError):
        archive_task(999)

def test_archive_task_already_archived_is_noop():
    from services.tasks import archive_task
    created = create_task("Twice archived", 1)
    archive_task(created["id"])
    result = archive_task(created["id"])
    assert result["archived"] is True

def test_create_task_default_not_archived():
    result = create_task("Fresh task", 1)
    assert result.get("archived") is False

def test_list_tasks_hides_archived_by_default():
    archived = create_task("Hidden task", 1)
    visible = create_task("Visible task", 1)
    _mark_archived(archived)
    ids = [task["id"] for task in list_tasks()]
    assert archived["id"] not in ids
    assert visible["id"] in ids

def test_list_tasks_archived_hidden_with_priority_filter():
    archived = create_task("Hidden priority task", 1, priority=2)
    _mark_archived(archived)
    ids = [task["id"] for task in list_tasks(priority=2)]
    assert archived["id"] not in ids

def test_list_tasks_include_archived_true():
    archived = create_task("Included task", 1)
    _mark_archived(archived)
    ids = [task["id"] for task in list_tasks(include_archived=True)]
    assert archived["id"] in ids

def test_list_tasks_include_archived_string_parsing():
    archived = create_task("Parsed task", 1)
    _mark_archived(archived)
    for value in ("true", "TRUE"):
        assert archived["id"] in [task["id"] for task in list_tasks(include_archived=value)]
    assert archived["id"] not in [task["id"] for task in list_tasks(include_archived="false")]

def test_list_tasks_include_archived_invalid_raises_validation():
    with pytest.raises(ValidationError):
        list_tasks(include_archived="yes")

def test_list_tasks_q_hides_archived_by_default():
    archived = create_task("Vellicorn archived", 1)
    visible = create_task("Vellicorn visible", 1)
    _mark_archived(archived)
    default_ids = [task["id"] for task in list_tasks(q="vellicorn")]
    assert archived["id"] not in default_ids
    assert visible["id"] in default_ids
    included_ids = [task["id"] for task in list_tasks(q="vellicorn", include_archived=True)]
    assert archived["id"] in included_ids
    assert visible["id"] in included_ids
