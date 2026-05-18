def _tick_prices(market: dict) -> list[float]:
    """Extract numeric prices from Deriv ({epoch, price}) or stub float ticks."""
    raw_prices = market.get("prices")
    if raw_prices:
        return [float(p) for p in raw_prices]

    prices: list[float] = []
    for tick in market.get("ticks") or []:
        if isinstance(tick, dict):
            price = tick.get("price")
            if price is not None:
                prices.append(float(price))
        elif isinstance(tick, (int, float)):
            prices.append(float(tick))
    return prices


def compute_indicator(market: dict) -> dict:
    prices = _tick_prices(market)
    if len(prices) < 2:
        return {"direction": "neutral", "up_pct": 0.0, "window": 0}

    window = min(5, len(prices) - 1)
    ups = sum(1 for i in range(1, window + 1) if prices[i] > prices[i - 1])
    up_pct = (ups / window) * 100
    if up_pct >= 60:
        direction = "up"
    elif up_pct <= 40:
        direction = "down"
    else:
        direction = "neutral"
    return {"direction": direction, "up_pct": up_pct, "window": window}
