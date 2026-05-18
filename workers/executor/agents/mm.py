from shared.events import WorkflowSnapshot
from shared.masaniello import MmSession, compute_next_stake, session_from_snapshot


async def compute_stake(
    snapshot: WorkflowSnapshot,
    decision: dict,
    mm_session: MmSession | None,
) -> tuple[float, MmSession, dict]:
    session = mm_session or session_from_snapshot(snapshot)

    if decision.get("action", "skip") == "skip":
        return 0.0, session, {"risk_level": "low", "reason": "skip"}

    stake, risk_level = compute_next_stake(session)
    meta = {
        "risk_level": risk_level,
        "capital": session.capital,
        "wins": session.wins,
        "losses": session.losses,
        "remaining_trades": session.remaining_trades,
        "wins_needed": session.wins_needed,
    }
    return stake, session, meta
