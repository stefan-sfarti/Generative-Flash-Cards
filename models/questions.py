from abc import ABC, abstractmethod

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
