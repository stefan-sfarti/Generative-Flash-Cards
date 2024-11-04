# Class Relationships:
# - Question (Abstract Base Class)
#   ├── MultipleChoiceQuestion (Concrete Class)
#   ├── ValueBasedQuestion (Concrete Class)
#   └── OpenEndedQuestion (Concrete Class)
#
# - QuestionFactory (Creates different question types)
#   └── Has-a LLMService (Dependency)
#
# - ResponseGenerator (Generates responses for questions)
#   └── Has-a LLMService (Dependency)
#
# - ResponseCache (Caches responses for questions)
#   └── Used-by QuestionFactory (Association)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Union, Tuple
from uuid import UUID, uuid4


# Enums for categorizing questions
class HFTopic(Enum):
    """Topics in Heart Failure education"""
    DEFINITION_AND_CLASSIFICATION = "definition_and_classification"
    DIAGNOSIS = "diagnosis"
    ASSESSMENT_OF_HF_SEVERITY = "assessment_of_hf_severity"
    IMAGING_TECHNIQUES = "imaging_techniques"
    DIAGNOSTIC_TESTS = "diagnostic_tests"
    PHARMACOLOGICAL_THERAPY = "pharmacological_therapy"
    DEVICE_THERAPY = "device_therapy"
    COMORBIDITIES = "comorbidities"
    PREVENTION = "prevention"
    END_OF_LIFE_CARE = "end_of_life_care"


class DifficultyLevel(Enum):
    """Question difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Range:
    """Represents a numeric range with units"""
    min_value: float
    max_value: float
    unit: str


class Question(ABC):
    """
    Abstract base class for all question types.
    Defines the common interface and properties for questions.
    """

    def __init__(
            self,
            question_id: UUID,
            prompt: str,
            difficulty: DifficultyLevel,
            topic: HFTopic,
            explanation: str
    ):
        self.question_id: UUID = question_id
        self.prompt: str = prompt
        self.difficulty: DifficultyLevel = difficulty
        self.topic: HFTopic = topic
        self.explanation: str = explanation

    @abstractmethod
    def validate(self) -> bool:
        """Validates if the question is properly structured"""
        pass

    @abstractmethod
    def format(self) -> str:
        """Returns formatted string representation of the question"""
        pass

    @abstractmethod
    def is_correct_answer(self, response: str) -> bool:
        """Checks if the provided answer is correct"""
        pass


class MultipleChoiceQuestion(Question):
    """
    Multiple choice question implementation.
    Contains a list of options and the index of the correct option.
    """

    def __init__(
            self,
            question_id: UUID,
            prompt: str,
            difficulty: DifficultyLevel,
            topic: HFTopic,
            explanation: str,
            options: List[str],
            correct_option_index: int
    ):
        super().__init__(question_id, prompt, difficulty, topic, explanation)
        self.options: List[str] = options
        self.correct_option_index: int = correct_option_index

    def validate(self) -> bool:
      """Validates if options and correct_option_index are valid"""
      return (len(self.options) > 1 and
                0 <= self.correct_option_index < len(self.options))

    def format(self) -> str:
        """Formats the question with numbered options"""
        formatted = f"{self.prompt}\n\n"
        for i, option in enumerate(self.options):
            formatted += f"{i + 1}. {option}\n"
        return formatted

    def is_correct_answer(self, response: str) -> bool:
        """Checks if the selected option index matches the correct answer"""
        try:
            return int(response) - 1 == self.correct_option_index
        except ValueError:
            return False


class ValueBasedQuestion(Question):
    """
    Numerical value-based question implementation.
    Includes expected value, unit, tolerance range, and acceptable value range.
    """

    def __init__(
            self,
            question_id: UUID,
            prompt: str,
            difficulty: DifficultyLevel,
            topic: HFTopic,
            explanation: str,
            expected_value: float,
            unit: str,
            tolerance: float,
            value_range: Range
    ):
        super().__init__(question_id, prompt, difficulty, topic, explanation)
        self.expected_value: float = expected_value
        self.unit: str = unit
        self.tolerance: float = tolerance
        self.value_range: Range = value_range

    def validate(self) -> bool:
        """Validates if the expected value falls within the acceptable range"""
        return (self.value_range.min_value <= self.expected_value <=
                self.value_range.max_value)

    def format(self) -> str:
        """Formats the question with unit information"""
        return f"{self.prompt} (Answer in {self.unit})"

    def is_correct_answer(self, response: str) -> bool:
        """Checks if the provided value is within tolerance of expected value"""
        try:
            value = float(response)
            return abs(value - self.expected_value) <= self.tolerance
        except ValueError:
            return False


class OpenEndedQuestion(Question):
    """
    Open-ended question implementation.
    Includes keywords/phrases that should be present in a correct answer.
    """

    def __init__(
            self,
            question_id: UUID,
            prompt: str,
            difficulty: DifficultyLevel,
            topic: HFTopic,
            explanation: str,
            required_keywords: List[str],
            model_answer: str,
            min_words: int = 50
    ):
        super().__init__(question_id, prompt, difficulty, topic, explanation)
        self.required_keywords: List[str] = required_keywords
        self.model_answer: str = model_answer
        self.min_words: int = min_words

    def validate(self) -> bool:
        """Validates if the question has required keywords and model answer"""
        return (len(self.required_keywords) > 0 and
                len(self.model_answer.split()) >= self.min_words)

    def format(self) -> str:
        """Formats the open-ended question with any additional instructions"""
        return f"{self.prompt}\n\nPlease provide a detailed explanation " \
               f"(minimum {self.min_words} words)."

    def is_correct_answer(self, response: str) -> bool:
        """
        Checks if the response contains required keywords and meets minimum length.
        Note: In practice, this would likely use more sophisticated NLP techniques.
          """
        words = response.split()
        if len(words) < self.min_words:
            return False

        response_lower = response.lower()
        return all(keyword.lower() in response_lower
                   for keyword in self.required_keywords)


class QuestionFactory:
    """
    Factory class for creating different types of questions.
    Uses LLMService to generate question content.
    """

    def __init__(self, llm_service: 'LLMService'):
        self.llm_service = llm_service

    def create_mc_question(
            self,
            topic: HFTopic,
            difficulty: DifficultyLevel
    ) -> MultipleChoiceQuestion:
        """Creates a multiple choice question"""
        pass

    def create_value_question(
            self,
            topic: HFTopic,
            difficulty: DifficultyLevel
    ) -> ValueBasedQuestion:
        """Creates a value-based question"""
        pass

    def create_open_ended_question(
            self,
            topic: HFTopic,
            difficulty: DifficultyLevel
    ) -> OpenEndedQuestion:
        """Creates an open-ended question"""
        pass


class ResponseGenerator:
    """
    Generates appropriate responses for different question types.
    Uses LLMService for response generation.
    """

    def __init__(self, llm_service: 'LLMService'):
        self.llm_service = llm_service

    def generate_mc_options(self, prompt: str, count: int) -> List[str]:
        """Generates multiple choice options"""
        pass

    def generate_value_range(self, topic: str) -> Range:
        """Generates acceptable value ranges for numeric questions"""
        pass

    def generate_model_answer(self, prompt: str) -> str:
        """Generates model answer for open-ended questions"""
        pass


class ResponseCache:
    """
    Caches responses for questions to improve performance.
    Implements a simple in-memory cache using question IDs as keys.
    """

    def __init__(self):
        self.cached_responses: Dict[UUID, List[str]] = {}

    def get_cached_responses(self, question_id: UUID) -> List[str]:
        """Retrieves cached responses for a question"""
        pass

    def add_responses(self, question_id: UUID, responses: List[str]) -> None:
        """Adds new responses to the cache"""
        pass

    def refresh_cache(self, topic: HFTopic) -> None:
        """Refreshes cached responses for a specific topic"""
        pass


class LLMService:
    """
    Service class for interacting with the Language Learning Model.
    Provides methods for generating questions and validating responses.
    """

    def __init__(self, model_path: str, config: Dict):
        self.model_path: str = model_path
        self.config: Dict = config

    def generate_question(self, topic: HFTopic, difficulty: DifficultyLevel) -> str:
        """Generates question content based on topic and difficulty"""
        pass

    def generate_options(self, question: str, num_options: int) -> List[str]:
        """Generates options for multiple choice questions"""
        pass

    def validate_response(self, question: str, response: str) -> bool:
        """Validates responses using the language model"""
        pass
