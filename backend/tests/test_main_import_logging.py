"""Tests for ImportError logging in app.main (S-9)."""

import importlib
import logging
import sys
from unittest.mock import patch


class TestImportErrorLogging:
    """Test that ImportError on optional modules is logged, not silenced."""

    def test_items_import_error_is_logged(self):
        """When items module fails to import, it should log a message."""
        import app.main

        # Remove cached item modules so reload triggers the import path
        saved = {}
        for key in list(sys.modules.keys()):
            if key.startswith("app.items"):
                saved[key] = sys.modules.pop(key)

        block = {"app.items": None, "app.items.routes": None}

        with patch.object(logging.getLogger("app.main"), "info") as mock_info:
            with patch.dict("sys.modules", block):
                importlib.reload(app.main)

            # Find the call that mentions "Items module not available"
            calls = [
                c
                for c in mock_info.call_args_list
                if len(c.args) >= 1 and "Items module not available" in str(c.args[0])
            ]
            assert len(calls) >= 1, (
                f"Expected 'Items module not available' log. "
                f"Got calls: {mock_info.call_args_list}"
            )

        # Restore modules
        sys.modules.update(saved)
        importlib.reload(app.main)

    def test_billing_import_error_is_logged(self):
        """When billing module fails to import, it should log a message."""
        import app.main

        saved = {}
        for key in list(sys.modules.keys()):
            if key.startswith("app.billing"):
                saved[key] = sys.modules.pop(key)

        block = {"app.billing": None, "app.billing.routes": None}

        with patch.object(logging.getLogger("app.main"), "info") as mock_info:
            with patch.dict("sys.modules", block):
                importlib.reload(app.main)

            calls = [
                c
                for c in mock_info.call_args_list
                if len(c.args) >= 1 and "Billing module not available" in str(c.args[0])
            ]
            assert len(calls) >= 1, (
                f"Expected 'Billing module not available' log. "
                f"Got calls: {mock_info.call_args_list}"
            )

        sys.modules.update(saved)
        importlib.reload(app.main)
