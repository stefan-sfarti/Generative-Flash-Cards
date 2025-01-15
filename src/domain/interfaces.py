from abc import ABC, abstractmethod
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


# Core Interfaces
class ModelService(ABC):
    """Interface for model operations"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the model"""
        pass

    @abstractmethod
    async def generate_question(self, request: GenerationRequest) -> Question:
        """Generate a new question based on the request"""
        pass

    @abstractmethod
    async def is_ready(self) -> bool:
        """Check if the model is loaded and ready"""
        pass


class CacheService(ABC):
    """Interface for caching operations"""

    @abstractmethod
    async def get_cached_question(self, topic: str, difficulty: QuestionDifficulty) -> Optional[Question]:
        """Retrieve a cached question if available"""
        pass

    @abstractmethod
    async def cache_question(self, question: Question, topic: str, difficulty: QuestionDifficulty) -> None:
        """Cache a generated question"""
        pass

    @abstractmethod
    async def get_cache_size(self, topic: str, difficulty: QuestionDifficulty) -> int:
        """Get current number of cached questions for topic/difficulty"""
        pass


class QuestionService(ABC):
    """High-level interface for question operations"""

    @abstractmethod
    async def get_question(self, request: GenerationRequest) -> Question:
        """Get a question, either from cache or newly generated"""
        pass

    @abstractmethod
    async def generate_and_cache_questions(self, request: GenerationRequest, count: int) -> None:
        """Background task to generate and cache questions"""
        pass