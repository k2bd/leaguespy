from dataclasses import dataclass


@dataclass
class PlayerTaskInfo:
    """
    Info about a task and whether a particular player has completed it.
    """

    task_id: int

    region: str

    description: str

    points: int

    completion_pct: str

    player_completed: bool
