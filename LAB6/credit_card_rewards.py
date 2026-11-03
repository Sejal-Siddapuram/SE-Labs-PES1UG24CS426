POINTS_PER_100 = {"classic": 1, "gold": 2, "platinum": 4}


def reward_points(card_tier, amount, category, is_weekend):
    if card_tier not in POINTS_PER_100:
        raise ValueError("unknown card tier")
    if amount <= 0:
        raise ValueError("invalid amount")
    if category == "fuel":
        return 0
    points = amount // 100 * POINTS_PER_100[card_tier]
    if category == "dining" or category == "travel":
        points = points * 2
    if is_weekend and card_tier != "classic":
        points += 50
    return points


def late_payment_fee(outstanding, days_late):
    if days_late <= 0 or outstanding <= 0:
        return 0
    if outstanding <= 1000:
        fee = 100
    elif outstanding <= 10000:
        fee = 500
    else:
        fee = 1000
    if days_late > 30:
        fee += 750
    return fee


def card_status(utilisation_percent, missed_payments, is_frozen):
    if is_frozen:
        return "frozen"
    if missed_payments >= 3:
        return "blocked"
    if utilisation_percent > 90:
        return "over limit risk"
    elif utilisation_percent > 30 or missed_payments > 0:
        return "watch"
    return "good"
