"""Masaniello-style progressive staking (spreadsheet-aligned)."""
from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["low", "medium", "high"]


class MmSession(BaseModel):
    capital: float
    wins: int = 0
    losses: int = 0
    cycle_trades: int = 10
    target_wins: int = 6
    payout: float = 1.95
    min_stake: float = 0.35
    max_stake_fraction: float = 0.5

    @property
    def trades_played(self) -> int:
        return self.wins + self.losses

    @property
    def remaining_trades(self) -> int:
        return max(0, self.cycle_trades - self.trades_played)

    @property
    def wins_needed(self) -> int:
        return max(0, self.target_wins - self.wins)


def _prob_at_least_k_wins(n: int, k: int, p: float) -> float:
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    p = min(max(p, 0.001), 0.999)
    return sum(
        math.comb(n, i) * (p**i) * ((1 - p) ** (n - i))
        for i in range(k, n + 1)
    )


def compute_next_stake(session: MmSession) -> tuple[float, RiskLevel]:
    """
    stake = (1 - probability_factor) * capital
    probability_factor = P(meeting target in remaining trades) at expected win rate.
    """
    remaining = session.remaining_trades
    wins_needed = session.wins_needed

    if remaining <= 0 or wins_needed <= 0 or session.capital <= 0:
        return 0.0, "low"
    if wins_needed > remaining:
        return 0.0, "high"

    expected_p = session.target_wins / session.cycle_trades
    prob_success = _prob_at_least_k_wins(remaining, wins_needed, expected_p)
    probability_factor = prob_success
    stake = (1.0 - probability_factor) * session.capital

    edge = session.payout - 1.0
    if edge > 0:
        stake *= min(1.0, expected_p * session.payout / edge)

    cap = session.capital * session.max_stake_fraction
    stake = max(session.min_stake, min(stake, cap))

    pressure = wins_needed / remaining
    if pressure >= 0.7:
        risk: RiskLevel = "high"
    elif pressure >= 0.4:
        risk = "medium"
    else:
        risk = "low"

    return round(stake, 2), risk


def apply_trade_outcome(
    session: MmSession,
    *,
    stake: float,
    outcome: Literal["win", "loss", "pending"],
) -> MmSession:
    updated = session.model_copy(deep=True)
    if outcome == "pending":
        return updated

    if outcome == "win":
        updated.wins += 1
        updated.capital += stake * (updated.payout - 1.0)
    else:
        updated.losses += 1
        updated.capital = max(0.0, updated.capital - stake)

    return updated


def session_from_snapshot(snapshot) -> MmSession:
    return MmSession(
        capital=float(snapshot.risk_capital),
        cycle_trades=int(snapshot.mm_cycle_trades),
        target_wins=int(snapshot.mm_target_wins),
        payout=float(snapshot.mm_payout),
    )
