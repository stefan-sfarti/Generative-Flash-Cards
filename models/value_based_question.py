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

