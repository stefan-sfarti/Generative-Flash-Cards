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

