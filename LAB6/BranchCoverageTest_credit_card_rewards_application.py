# Lab 6 - Branch Coverage tests for credit_card_rewards.py
# Name: Sejal Siddapuram | SRN: PES1UG24CS426 | Section: G
#
# Goal: every decision (if / elif / else) evaluates to BOTH True and False,
# including each side of the compound conditions (and / or) and the
# boundary values where a comparison flips.
# Run:
#   coverage run --branch -m pytest BranchCoverageTest_credit_card_rewards_application.py
#   coverage report -m

import pytest
from credit_card_rewards import reward_points, late_payment_fee, card_status


# ======================= reward_points =======================

# --- if card_tier not in POINTS_PER_100 ---
def test_unknown_card_tier_raises():                 # True
    with pytest.raises(ValueError, match="unknown card tier"):
        reward_points("silver", 1000, "grocery", False)


def test_classic_grocery():                          # False (valid tier)
    assert reward_points("classic", 1000, "grocery", False) == 10


# --- if amount <= 0 ---
def test_zero_amount_raises():                       # True (boundary 0)
    with pytest.raises(ValueError, match="invalid amount"):
        reward_points("gold", 0, "grocery", False)


def test_negative_amount_raises():                   # True (negative)
    with pytest.raises(ValueError, match="invalid amount"):
        reward_points("gold", -500, "grocery", False)


def test_small_positive_amount_gives_zero_points():  # False, amount < 100
    assert reward_points("gold", 50, "grocery", False) == 0


# --- if category == "fuel" ---
def test_fuel_gives_zero_points():                   # True
    assert reward_points("platinum", 5000, "fuel", True) == 0


# --- if category == "dining" or category == "travel" ---
def test_dining_doubles_points():                    # True via first operand
    # 1000 // 100 * 1 = 10 -> doubled = 20
    assert reward_points("classic", 1000, "dining", False) == 20


def test_travel_doubles_points():                    # True via second operand
    # 1000 // 100 * 4 = 40 -> doubled = 80
    assert reward_points("platinum", 1000, "travel", False) == 80


def test_shopping_not_doubled():                     # False (both operands False)
    assert reward_points("gold", 1000, "shopping", False) == 20


# --- if is_weekend and card_tier != "classic" ---
def test_gold_weekend_bonus():                       # True
    # 20 points + 50 weekend bonus
    assert reward_points("gold", 1000, "grocery", True) == 70


def test_classic_weekend_no_bonus():                 # False: weekend but classic
    assert reward_points("classic", 1000, "grocery", True) == 10


def test_platinum_weekday_no_bonus():                # False: not weekend
    assert reward_points("platinum", 1000, "grocery", False) == 40


def test_platinum_travel_weekend_all_rules():        # double + bonus together
    # 2550 // 100 = 25 * 4 = 100 -> doubled = 200 -> +50 = 250
    assert reward_points("platinum", 2550, "travel", True) == 250


# ===================== late_payment_fee ======================

# --- if days_late <= 0 or outstanding <= 0 ---
def test_paid_on_time():                             # True via days_late == 0
    assert late_payment_fee(5000, 0) == 0


def test_negative_days_late():                       # True via days_late < 0
    assert late_payment_fee(5000, -3) == 0


def test_nothing_outstanding():                      # True via outstanding <= 0
    assert late_payment_fee(0, 10) == 0


def test_negative_outstanding():                     # True via outstanding < 0
    assert late_payment_fee(-200, 10) == 0


# --- if outstanding <= 1000 / elif <= 10000 / else ---
def test_small_outstanding_fee():                    # first if True
    assert late_payment_fee(500, 5) == 100


def test_outstanding_exactly_1000():                 # boundary of first if
    assert late_payment_fee(1000, 5) == 100


def test_outstanding_just_above_1000():              # elif True
    assert late_payment_fee(1001, 5) == 500


def test_outstanding_exactly_10000():                # boundary of elif
    assert late_payment_fee(10000, 5) == 500


def test_outstanding_above_10000():                  # else branch
    assert late_payment_fee(10001, 5) == 1000


# --- if days_late > 30 ---
def test_exactly_30_days_no_extra():                 # False (boundary)
    assert late_payment_fee(5000, 30) == 500


def test_31_days_extra_charge():                     # True (boundary + 1)
    assert late_payment_fee(5000, 31) == 1250


def test_large_outstanding_very_late():              # else + extra charge
    assert late_payment_fee(50000, 60) == 1750


def test_one_day_late_small_amount():                # smallest late case
    assert late_payment_fee(1, 1) == 100


# ======================= card_status =========================

# --- if is_frozen ---
def test_frozen_card():                              # True
    assert card_status(10, 0, True) == "frozen"


def test_frozen_overrides_blocked():                 # frozen checked first
    assert card_status(99, 5, True) == "frozen"


# --- if missed_payments >= 3 ---
def test_blocked_card_exactly_3_missed():            # True (boundary)
    assert card_status(10, 3, False) == "blocked"


def test_blocked_overrides_over_limit():             # blocked checked before utilisation
    assert card_status(95, 4, False) == "blocked"


# --- if utilisation_percent > 90 ---
def test_over_limit_risk():                          # True
    assert card_status(95, 0, False) == "over limit risk"


def test_utilisation_exactly_90_is_watch():          # False (boundary) -> elif True
    assert card_status(90, 0, False) == "watch"


# --- elif utilisation_percent > 30 or missed_payments > 0 ---
def test_watch_high_utilisation():                   # True via first operand
    assert card_status(50, 0, False) == "watch"


def test_watch_missed_payment_low_utilisation():     # True via second operand
    assert card_status(10, 1, False) == "watch"


def test_two_missed_payments_still_watch():          # 2 < 3 so not blocked
    assert card_status(10, 2, False) == "watch"


def test_utilisation_exactly_30_is_good():           # False (boundary)
    assert card_status(30, 0, False) == "good"


def test_good_card():                                # False -> return "good"
    assert card_status(0, 0, False) == "good"
