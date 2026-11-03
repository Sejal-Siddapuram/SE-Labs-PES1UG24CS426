import pytest
from credit_card_rewards import reward_points, late_payment_fee, card_status

#Example test cases:
def test_classic_grocery():
    assert reward_points("classic", 1000, "grocery", False) == 10

def test_paid_on_time():
    assert late_payment_fee(5000, 0) == 0

#Write the rest of the test cases so that the code is 90- 100% covered.
