"""Tests for PairCoder branding in README.md and LISTING.md (T23.2)."""

import os

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
README_PATH = os.path.join(PROJECT_ROOT, "README.md")
LISTING_PATH = os.path.join(PROJECT_ROOT, "badges", "LISTING.md")

BADGE_TEXT = "![Built with PairCoder]"
BADGE_URL = "https://img.shields.io/badge/built%20with-PairCoder-blueviolet"


@pytest.fixture
def readme_content() -> str:
    """Read README.md."""
    with open(README_PATH) as f:
        return f.read()


@pytest.fixture
def listing_content() -> str:
    """Read LISTING.md."""
    with open(LISTING_PATH) as f:
        return f.read()


def test_readme_has_paircoder_badge(readme_content: str) -> None:
    """README.md must contain the PairCoder badge."""
    assert BADGE_TEXT in readme_content
    assert BADGE_URL in readme_content


def test_readme_badge_in_first_5_lines(readme_content: str) -> None:
    """PairCoder badge must be in the badge row (first 5 lines)."""
    first_lines = "\n".join(readme_content.splitlines()[:5])
    assert BADGE_TEXT in first_lines


def test_readme_grep_paircoder(readme_content: str) -> None:
    """grep -i 'paircoder' README.md must return results (AC)."""
    assert "paircoder" in readme_content.lower()


def test_listing_has_paircoder_badge(listing_content: str) -> None:
    """LISTING.md must contain the PairCoder badge."""
    assert BADGE_TEXT in listing_content
    assert BADGE_URL in listing_content


def test_listing_grep_paircoder(listing_content: str) -> None:
    """grep -i 'paircoder' LISTING.md must return results (AC)."""
    assert "paircoder" in listing_content.lower()


def test_listing_has_paircoder_mention_outside_badge_row(
    listing_content: str,
) -> None:
    """LISTING.md must mention PairCoder outside the badge code block."""
    # Remove the badge code block to check for mention elsewhere
    lines = listing_content.splitlines()
    outside_badge = []
    in_code_block = False
    for line in lines:
        if line.strip() == "```":
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            outside_badge.append(line)
    outside_text = "\n".join(outside_badge)
    assert "PairCoder" in outside_text, (
        "LISTING.md must mention PairCoder outside the badge code block"
    )


def test_badge_renders_as_valid_markdown(readme_content: str) -> None:
    """Badge must be valid Markdown image syntax."""
    assert "![Built with PairCoder](https://img.shields.io/badge/" in readme_content
