from typing import Literal
from pydantic import BaseModel


class RequiredSkill(BaseModel):
    name: str
    level: Literal["notions", "intermediate", "advanced", "unknown"]
    alternatives: list[str]      # other tools that also satisfy this requirement

class Skill(BaseModel):
    name: str
    level: Literal["notions", "intermediate", "advanced", "unknown"]


class Offer(BaseModel):
    title: str
    required_skills: list[RequiredSkill]          # now with levels (parked item #4 ✅)
    bonus: list[str]
    level: Literal["junior", "mid", "senior", "unknown"]
    contract: Literal["stage", "cdi", "cdd", "freelance", "unknown"]
    location: str
    required_language: Literal["fr", "en", "unknown"]


class CV(BaseModel):
    full_name: str
    skills: list[Skill]
    languages: list[str]
    location: str
