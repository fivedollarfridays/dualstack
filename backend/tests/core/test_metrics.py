"""Tests for app.core.metrics module."""

import pytest
from unittest.mock import patch, MagicMock

from app.core.metrics import (
    increment_http_requests,
    observe_http_duration,
    increment_db_operations,
    increment_external_api_calls,
    track_job_metrics,
    update_pool_metrics,
)


class TestHttpMetrics:
    """Test HTTP metric helper functions."""

    def test_increment_http_requests(self):
        """increment_http_requests should increment the counter."""
        # Should not raise - just verify it runs
        increment_http_requests("GET", "/api/test", 200)

    def test_observe_http_duration(self):
        """observe_http_duration should observe the histogram."""
        observe_http_duration("POST", "/api/test", 0.123)


class TestDbMetrics:
    """Test database metric helper functions."""

    def test_increment_db_operations(self):
        """increment_db_operations should increment the counter."""
        increment_db_operations("select", "users", "success")

    def test_increment_db_operations_error(self):
        """increment_db_operations should handle error status."""
        increment_db_operations("insert", "items", "error")


class TestExternalApiMetrics:
    """Test external API metric helpers."""

    def test_increment_external_api_calls(self):
        """increment_external_api_calls should increment the counter."""
        increment_external_api_calls("stripe", "create_charge", "success")

    def test_increment_external_api_calls_error(self):
        """increment_external_api_calls should handle error status."""
        increment_external_api_calls("stripe", "create_charge", "error")


class TestTrackJobMetrics:
    """Test track_job_metrics decorator."""

    @pytest.mark.asyncio
    async def test_success_path(self):
        """Decorated function should track success metrics."""

        @track_job_metrics("test_job")
        async def my_job():
            return "done"

        result = await my_job()
        assert result == "done"

    @pytest.mark.asyncio
    async def test_failure_path(self):
        """Decorated function should track failure metrics and re-raise."""

        @track_job_metrics("failing_job")
        async def my_failing_job():
            raise ValueError("something broke")

        with pytest.raises(ValueError, match="something broke"):
            await my_failing_job()

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        """Decorated function should preserve original function name via wraps."""

        @track_job_metrics("named_job")
        async def original_name():
            pass

        assert original_name.__name__ == "original_name"


class TestUpdatePoolMetrics:
    """Test update_pool_metrics function."""

    def test_with_pool_that_has_size(self):
        """Should update gauge metrics when pool has size/checkedout/overflow."""
        mock_pool = MagicMock()
        mock_pool.size.return_value = 5
        mock_pool.checkedout.return_value = 2
        mock_pool.overflow.return_value = 0

        mock_engine = MagicMock()
        mock_engine.pool = mock_pool

        with patch("app.core.database.get_engine", return_value=mock_engine):
            update_pool_metrics()

    def test_with_no_engine(self):
        """Should return early when engine is None."""
        with patch("app.core.database.get_engine", return_value=None):
            update_pool_metrics()  # Should not raise

    def test_with_static_pool(self):
        """Should return early when pool has no size attribute (StaticPool)."""
        mock_pool = MagicMock(spec=[])  # Empty spec = no attributes
        mock_engine = MagicMock()
        mock_engine.pool = mock_pool

        with patch("app.core.database.get_engine", return_value=mock_engine):
            update_pool_metrics()  # Should not raise
