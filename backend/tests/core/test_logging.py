"""Tests for app.core.logging module."""

import typing

import structlog

from app.core.logging import get_logger


class TestGetLogger:
    """Test get_logger function."""

    def test_returns_usable_logger(self):
        """get_logger should return a usable structlog logger."""
        logger = get_logger("test")
        # Must have standard logging methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")

    def test_return_type_annotation_is_bound_logger(self):
        """get_logger should have BoundLogger return type annotation, not Any."""
        hints = typing.get_type_hints(get_logger)
        assert hints["return"] is structlog.stdlib.BoundLogger
