from typing import List, Literal
from pydantic import BaseModel, Field

class PitchPoint(BaseModel):
    problem: str = Field(..., min_length=10, max_length=1000)
    solution: str = Field(..., min_length=10, max_length=1000)
    impact: str = Field(..., min_length=10, max_length=1000)

class MultiPitchRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    audience: Literal["Recruiter", "Project Manager", "Developer", "Non-Technical"]
    # we will **enforce** 2min in the controller regardless of what’s sent
    length: Literal["30s","60s","2min"] = "2min"
    tech: List[str] = Field(..., min_length=1)
    points: List[PitchPoint] = Field(..., min_length=2, max_length=3)  # 2–3 points per project

class MultiPitchResponse(BaseModel):
    title: str
    audience: str
    length: Literal["2min"]
    pitches: List[str]  # one pitch per point (each ~2 min)