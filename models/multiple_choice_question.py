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