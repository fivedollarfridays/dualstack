"""Tests for app.core.scheduler module."""

from unittest.mock import MagicMock

from app.core.scheduler import get_scheduler, reset_scheduler
import app.core.scheduler as scheduler_module


class TestGetScheduler:
    """Test get_scheduler function."""

    def setup_method(self):
        reset_scheduler()

    def teardown_method(self):
        reset_scheduler()

    def test_returns_scheduler(self):
        """get_scheduler should return an AsyncIOScheduler."""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        scheduler = get_scheduler()
        assert isinstance(scheduler, AsyncIOScheduler)

    def test_returns_same_instance(self):
        """get_scheduler should return the same instance on repeated calls."""
        s1 = get_scheduler()
        s2 = get_scheduler()
        assert s1 is s2


class TestResetScheduler:
    """Test reset_scheduler function."""

    def setup_method(self):
        reset_scheduler()

    def teardown_method(self):
        reset_scheduler()

    def test_clears_singleton(self):
        """reset_scheduler should clear the singleton so next call creates new."""
        s1 = get_scheduler()
        reset_scheduler()
        s2 = get_scheduler()
        assert s1 is not s2

    def test_safe_when_no_scheduler(self):
        """reset_scheduler should be safe to call when no scheduler exists."""
        reset_scheduler()  # Should not raise

    def test_shuts_down_running_scheduler(self):
        """reset_scheduler should shut down a running scheduler."""
        # Create a mock scheduler that reports as running
        mock_scheduler = MagicMock()
        mock_scheduler.running = True
        scheduler_module._scheduler = mock_scheduler

        reset_scheduler()

        mock_scheduler.shutdown.assert_called_once_with(wait=False)
        assert scheduler_module._scheduler is None

    def test_does_not_shutdown_stopped_scheduler(self):
        """reset_scheduler should not call shutdown on a non-running scheduler."""
        scheduler = get_scheduler()
        # Scheduler is not started, so running is False
        assert not scheduler.running
        reset_scheduler()
        assert scheduler_module._scheduler is None
