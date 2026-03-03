"""APScheduler singleton for background jobs."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Module-level singleton
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """Get the APScheduler singleton instance.

    Returns:
        The AsyncIOScheduler instance, created on first call.
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def reset_scheduler() -> None:
    """Reset the scheduler singleton (for testing).

    This allows tests to get a fresh scheduler instance.
    """
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
