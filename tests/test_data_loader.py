"""
test_data_loader.py
--------------------
Tests for the data loader and the recommendations engine.

These tests serve two purposes:
  1. Regression tests — they protect against accidental removal of validation
     logic. If anyone ever 'fixes' the loader to silently drop bad rows, these
     tests will fail.
  2. Design-rule tests — they enforce ethical design rules in code (e.g.
     'every learner gets at least one suggestion', 'the learner's stated need
     comes first').

Run with:  pytest -v
"""

import sys
import os
from pathlib import Path

# Make sure tests can import from the project root (where utils/ lives).
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.data_loader import confidence_band, load_data
from utils.recommendations import recommend_for_learner


# ======================================================================
# Tests for confidence_band()
# ======================================================================

def test_confidence_band_maps_scores_to_correct_bands():
    """Scores 1 and 2 -> Low, 3 -> Medium, 4 and 5 -> High."""
    assert confidence_band(1) == "Low"
    assert confidence_band(2) == "Low"
    assert confidence_band(3) == "Medium"
    assert confidence_band(4) == "High"
    assert confidence_band(5) == "High"


def test_confidence_band_returns_none_for_missing_values():
    """Missing values must not be guessed at — they return None.

    This protects the design rule: 'we don't guess when data is missing'.
    """
    import pandas as pd
    assert confidence_band(None) is None
    assert confidence_band(pd.NA) is None
    assert confidence_band(float("nan")) is None
    assert confidence_band("") is None


def test_confidence_band_returns_none_for_out_of_range_scores():
    """Out-of-range scores (the L008 case) return None — never coerced.

    This is the ethical safeguard: refuse to assign a band when the score
    is outside the valid 1–5 range, rather than silently snapping it to
    the nearest valid band.
    """
    assert confidence_band(0) is None
    assert confidence_band(6) is None
    assert confidence_band(7) is None     # the actual L008 value
    assert confidence_band(-1) is None
    assert confidence_band(100) is None


# ======================================================================
# Tests for load_data()
# ======================================================================

def test_load_data_detects_duplicate_learner_ids():
    """The L013 case — duplicate IDs in the dataset must be flagged in the report."""
    df, report = load_data(str(PROJECT_ROOT / "data" / "learners.csv"))
    assert "L013" in report["duplicate_ids"], (
        "The deliberate duplicate (L013) should appear in the report's duplicate_ids list. "
        "If this test fails, the duplicate detection logic has been broken."
    )


def test_load_data_detects_invalid_province_entries():
    """The L024 case — the malformed 'Gautng' typo must be flagged."""
    df, report = load_data(str(PROJECT_ROOT / "data" / "learners.csv"))
    invalid_ids = [issue["learner_id"] for issue in report["invalid_province"]]
    assert "L024" in invalid_ids, (
        "The deliberate malformed province (L024 = 'Gautng') should be flagged. "
        "If this test fails, the province validation logic has been broken."
    )


def test_load_data_detects_out_of_range_confidence_scores():
    """The L008 case — confidence score of 7 (outside 1-5) must be flagged."""
    df, report = load_data(str(PROJECT_ROOT / "data" / "learners.csv"))
    out_of_range_ids = [issue["learner_id"] for issue in report["out_of_range_confidence"]]
    assert "L008" in out_of_range_ids, (
        "The deliberate out-of-range score (L008 = 7) should be flagged. "
        "If this test fails, the range validation logic has been broken."
    )


# ======================================================================
# Tests for recommend_for_learner()
# ======================================================================

def test_recommend_for_learner_always_returns_at_least_one_suggestion():
    """Design rule: a learner must never come back with zero recommendations.

    'No recommendations' would silently read as 'no support need', which is
    its own ethical risk. The fallback ensures a check-in is always proposed.
    """
    # An almost-empty learner — nothing triggers any specific rule.
    empty_learner = {
        "device_access": "Own laptop",
        "internet_access": "Stable",
        "employment_status": "Unemployed",
        "programming_confidence_band": "High",
        "support_need": "None right now",
    }
    suggestions = recommend_for_learner(empty_learner)
    assert len(suggestions) >= 1, (
        "Every learner must receive at least one suggestion. "
        "The 'check-in' fallback is missing or broken."
    )


def test_recommend_for_learner_puts_stated_need_first():
    """Design rule: the learner's own voice ranks first.

    What the learner SAID they need must appear before any inferred
    suggestion. This protects the stakeholder-map principle that the
    most-affected person should be most visible in the system.
    """
    # A learner who triggers multiple inferred rules AND has a stated need.
    # The stated need must come back as the first suggestion.
    learner = {
        "device_access": "Phone only",          # would trigger device-loan rule
        "internet_access": "Unstable",          # would trigger data-bundle rule
        "employment_status": "Full-time",       # would trigger evening-sessions rule
        "programming_confidence_band": "Low",   # would trigger mentor rule
        "support_need": "Mental health support",  # the learner's own voice
    }
    suggestions = recommend_for_learner(learner)
    assert "Mental health support" in suggestions[0]["action"], (
        "The learner's stated support need must appear first in the suggestion list. "
        "If this test fails, the voice-first design rule has been broken."
    )