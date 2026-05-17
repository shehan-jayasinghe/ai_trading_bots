from shared.events import WorkflowSnapshot


async def compute_stake(snapshot: WorkflowSnapshot, decision: dict) -> float:
    """TODO: capital + progressive MM from DB."""
    _ = snapshot
    if decision.get("action") == "skip":
        return 0.0
    return 1.0
