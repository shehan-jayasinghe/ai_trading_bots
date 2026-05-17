def compute_indicator(market: dict) -> dict:
    ticks = market.get("ticks") or []
    if len(ticks) < 2:
        return {"direction": "neutral", "up_pct": 0.0, "window": 0}

    window = min(5, len(ticks) - 1)
    ups = sum(1 for i in range(1, window + 1) if ticks[i] > ticks[i - 1])
    up_pct = (ups / window) * 100
    if up_pct >= 60:
        direction = "up"
    elif up_pct <= 40:
        direction = "down"
    else:
        direction = "neutral"
    return {"direction": direction, "up_pct": up_pct, "window": window}
