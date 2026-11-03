# Lab 6 - Code (Line) Coverage tests for credit_card_rewards.py
# Name: Sejal Siddapuram | SRN: PES1UG24CS426 | Section: G
#
# Goal: make every line of credit_card_rewards.py execute at least once.
# Run:
#   coverage run -m pytest CodeCoverageTest_credit_card_rewards_application.py
#   coverage report -m

import pytest
from credit_card_rewards import reward_points, late_payment_fee, card_status


# ---------------- reward_points ----------------

def test_classic_grocery():
    # starter test: 1000 // 100 * 1 = 10, no bonus
    assert reward_points("classic", 1000, "grocery", False) == 10


def test_unknown_card_tier_raises():
    # covers: raise ValueError("unknown card tier")
    with pytest.raises(ValueError, match="unknown card tier"):
        reward_points("silver", 1000, "grocery", False)


def test_invalid_amount_raises():
    # covers: raise ValueError("invalid amount")
    with pytest.raises(ValueError, match="invalid amount"):
        reward_points("gold", 0, "grocery", False)


def test_fuel_gives_zero_points():
    # covers: return 0 for fuel
    assert reward_points("gold", 5000, "fuel", False) == 0


def test_gold_dining_on_weekend():
    # covers: dining doubles points AND weekend bonus for non-classic
    # 1000 // 100 * 2 = 20 -> doubled = 40 -> +50 weekend = 90
    assert reward_points("gold", 1000, "dining", True) == 90


# ---------------- late_payment_fee ----------------

def test_paid_on_time():
    # starter test: days_late <= 0 -> no fee
    assert late_payment_fee(5000, 0) == 0


def test_small_outstanding_fee():
    # outstanding <= 1000 -> 100
    assert late_payment_fee(800, 5) == 100


def test_medium_outstanding_very_late():
    # 1000 < outstanding <= 10000 -> 500, plus 750 for > 30 days late
    assert late_payment_fee(5000, 40) == 1250


def test_large_outstanding_fee():
    # outstanding > 10000 -> 1000
    assert late_payment_fee(20000, 10) == 1000


# ---------------- card_status ----------------

def test_frozen_card():
    assert card_status(10, 0, True) == "frozen"


def test_blocked_card():
    assert card_status(10, 3, False) == "blocked"


def test_over_limit_risk():
    assert card_status(95, 0, False) == "over limit risk"


def test_watch_high_utilisation():
    assert card_status(50, 0, False) == "watch"


def test_good_card():
    assert card_status(10, 0, False) == "good"
