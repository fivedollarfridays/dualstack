"""Tests for badges/LISTING.md marketplace listing document."""

import os
import re

import pytest

LISTING_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "badges", "LISTING.md"
)


@pytest.fixture
def listing_content() -> str:
    """Read the LISTING.md file."""
    assert os.path.exists(LISTING_PATH), "badges/LISTING.md must exist"
    with open(LISTING_PATH) as f:
        return f.read()


def test_listing_exists() -> None:
    """LISTING.md must exist in badges directory."""
    assert os.path.exists(LISTING_PATH)


def test_has_product_name(listing_content: str) -> None:
    """Must contain DualStack product name."""
    assert "DualStack" in listing_content


def test_has_tagline(listing_content: str) -> None:
    """Must have a tagline section."""
    assert "### Tagline" in listing_content


def test_has_price(listing_content: str) -> None:
    """Must show $79 one-time pricing."""
    assert "$79" in listing_content
    assert "lifetime updates" in listing_content.lower()


def test_has_description(listing_content: str) -> None:
    """Must have a description section."""
    assert "### Description" in listing_content


def test_emphasizes_python_fastapi(listing_content: str) -> None:
    """Must emphasize Python/FastAPI positioning."""
    assert "FastAPI" in listing_content
    assert "Python" in listing_content


def test_has_whats_in_the_box(listing_content: str) -> None:
    """Must have 'What's in the box' feature list."""
    assert "What's in the box" in listing_content


def test_has_why_this_exists(listing_content: str) -> None:
    """Must have 'Why this exists' positioning."""
    assert "Why this exists" in listing_content


def test_has_differentiator_list(listing_content: str) -> None:
    """Must have 12-point differentiator list."""
    assert "12 things" in listing_content.lower() or "won't find" in listing_content


def test_has_competitive_table(listing_content: str) -> None:
    """Must have competitive comparison table."""
    assert "Competitive comparison" in listing_content
    assert "Shipfast" in listing_content or "ShipFast" in listing_content
    assert "Supastarter" in listing_content
    assert "Makerkit" in listing_content


def test_has_not_included_table(listing_content: str) -> None:
    """Must have 'What's NOT included' section."""
    assert "NOT included" in listing_content


def test_has_badge_row(listing_content: str) -> None:
    """Must have badge row with actual metrics."""
    assert "Badge row" in listing_content or "badge row" in listing_content
    assert "1,357" in listing_content or "1357" in listing_content
    assert "95%" in listing_content


def test_has_thumbnail_spec(listing_content: str) -> None:
    """Must have thumbnail/hero image text spec."""
    assert "Thumbnail" in listing_content or "hero image" in listing_content


def test_has_faq_section(listing_content: str) -> None:
    """Must have FAQ section with 6+ questions."""
    assert "FAQ" in listing_content
    # At least 6 bold question-answer pairs in FAQ area
    faq_start = listing_content.index("FAQ")
    faq_text = listing_content[faq_start:]
    questions = re.findall(r"\*\*[^*]+\?\*\*", faq_text)
    assert len(questions) >= 6, f"Expected 6+ FAQ questions, found {len(questions)}"


def test_has_seo_keywords(listing_content: str) -> None:
    """Must have SEO keywords section."""
    assert "SEO keywords" in listing_content or "SEO" in listing_content


def test_has_account_setup_notes(listing_content: str) -> None:
    """Must have account setup notes for Gumroad + LemonSqueezy."""
    assert "Gumroad" in listing_content
    assert "LemonSqueezy" in listing_content


def test_has_zero_vulnerabilities(listing_content: str) -> None:
    """Badge row must show 0 vulnerabilities."""
    assert "0 vulnerabilities" in listing_content or "vulnerabilities-0" in listing_content
