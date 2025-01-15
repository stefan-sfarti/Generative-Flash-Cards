from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


# Domain Models
class QuestionDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionSource(str, Enum):
    ESC_GUIDELINES = "ESC Guidelines"
    GENERAL_KNOWLEDGE = "General Knowledge"


class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: str


class GenerationRequest(BaseModel):
    topic: str = "heart_failure"
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM