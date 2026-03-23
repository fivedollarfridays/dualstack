"""Version validation tests for security patches."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestNextVersion:
    def test_next_version_patched(self) -> None:
        pkg = json.loads((ROOT / "frontend" / "package.json").read_text())
        raw = pkg["dependencies"]["next"]
        # Strip any range prefix (^, ~, >=) to get bare version
        version = re.sub(r"^[^0-9]*", "", raw)
        # Must be >= 15.5.13 (fixes GHSA-ggv3-7p47-pfv8 and GHSA-3x4c-7xq6-9pq8)
        parts = [int(x) for x in version.split(".")]
        assert parts >= [15, 5, 13], f"next {version} < 15.5.13"

    def test_eslint_config_next_matches(self) -> None:
        pkg = json.loads((ROOT / "frontend" / "package.json").read_text())
        next_ver = re.sub(r"^[^0-9]*", "", pkg["dependencies"]["next"])
        eslint_ver = pkg["devDependencies"]["eslint-config-next"]
        assert eslint_ver == next_ver, f"eslint-config-next {eslint_ver} != next {next_ver}"


class TestPyasn1Pin:
    def test_pyasn1_pinned_in_requirements(self) -> None:
        reqs = (ROOT / "backend" / "requirements.txt").read_text()
        assert "pyasn1" in reqs, "pyasn1 must be pinned in requirements.txt"
        # Must specify >= 0.6.3
        match = re.search(r"pyasn1>=(\d+\.\d+\.\d+)", reqs)  # handles >=0.6.3,<1.0
        assert match, "pyasn1 must use >= version constraint"
        parts = [int(x) for x in match.group(1).split(".")]
        assert parts >= [0, 6, 3], f"pyasn1 pin {match.group(1)} < 0.6.3"
