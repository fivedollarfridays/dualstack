"""Shared utilities for task lifecycle scripts."""

from pathlib import Path

VALID_STATUSES = frozenset(["pending", "in_progress", "blocked", "review", "done"])

STATUS_DONE = "done"

ACCEPTANCE_CRITERIA_HEADING = "## acceptance criteria"


def find_task_file(
    task_id: str, *, include_archive: bool = False
) -> Path | None:
    """Find a task file by ID prefix.

    Args:
        task_id: Task ID prefix (e.g., "TASK-001").
        include_archive: Also search the archive directory.

    Returns:
        Path to the matching task file, or None.
    """
    dirs = [Path(".paircoder/tasks")]
    if include_archive:
        dirs.append(Path(".paircoder/tasks/archive"))

    for task_dir in dirs:
        match = next(task_dir.glob(f"{task_id}*.task.md"), None)
        if match is not None:
            return match

    return None
