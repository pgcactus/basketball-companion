from typing import List, Literal

from pydantic import BaseModel


class Shot(BaseModel):
    timestamp_of_outcome: str
    result: Literal["made", "missed"]
    shot_type: Literal["jump shot", "three-pointer", "layup", "free throw", "floater"]
    total_shots_made_so_far: int
    total_shots_missed_so_far: int
    feedback: str


class SessionAnalysis(BaseModel):
    shots: List[Shot]
    session_summary: str
