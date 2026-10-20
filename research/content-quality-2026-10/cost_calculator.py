"""Illustrative monthly cost model. USD inputs; not current vendor prices."""
import json
from decimal import Decimal, ROUND_HALF_UP


def amount(value):
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError("Inputs must be finite and nonnegative")
    return result


def calculate(*, seats, seat_price, metered=0, hosting=0, energy=0,
              hardware=0, amortization_months=36, incremental_review_hours=0,
              hourly_rate=0, accepted_tasks=0):
    if type(seats) is not int or seats < 1:
        raise ValueError("seats must be a positive integer")
    if type(accepted_tasks) is not int or accepted_tasks < 0:
        raise ValueError("accepted_tasks must be a nonnegative integer")
    if type(amortization_months) is not int or amortization_months < 1:
        raise ValueError("amortization_months must be a positive integer")
    cash = seats * amount(seat_price) + amount(metered) + amount(hosting) + amount(energy)
    amortized = amount(hardware) / amortization_months
    labor = amount(incremental_review_hours) * amount(hourly_rate)
    economic = cash + amortized + labor
    money = lambda n: str(n.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return {
        "currency": "USD",
        "recurring_cash": money(cash),
        "hardware_amortization": money(amortized),
        "incremental_review_value": money(labor),
        "economic_cost": money(economic),
        "economic_cost_per_seat": money(economic / seats),
        "economic_cost_per_accepted_task": money(economic / accepted_tasks) if accepted_tasks else None,
        "upfront_hardware_cash": money(amount(hardware)),
    }


if __name__ == "__main__":
    scenarios = {
        "team_illustration": calculate(seats=10, seat_price=20, metered=100,
                                      incremental_review_hours=12, hourly_rate=60,
                                      accepted_tasks=100),
        "home_illustration": calculate(seats=1, seat_price=0, energy="1.20", hardware=600),
    }
    print(json.dumps(scenarios, indent=2))
