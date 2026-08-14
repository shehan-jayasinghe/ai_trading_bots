from app.flow import FlowCalculator, _aggression, _imbalance


def test_aggression_and_imbalance():
    assert abs(_aggression(80, 50) - 80 / 130) < 1e-9
    assert _aggression(0, 0) is None
    assert abs(_imbalance(420, 310) - (110 / 730)) < 1e-9


def test_buy_sell_from_trades():
    calc = FlowCalculator()
    calc.on_book([(100.0, 10.0)], [(100.5, 8.0)])
    calc.on_trade(price=100.0, qty=80.0, side="BUY", event_time_ms=1_000)
    calc.on_trade(price=100.1, qty=50.0, side="SELL", event_time_ms=1_100)
    closed = calc.on_trade(price=100.2, qty=1.0, side="BUY", event_time_ms=2_000)
    assert closed is not None
    snap = calc.snapshot(closed)
    assert snap["buy_volume"] == 80.0
    assert snap["sell_volume"] == 50.0
    assert abs(snap["delta"] - 30.0) < 1e-9
    assert snap["pressure"] == "buying"
