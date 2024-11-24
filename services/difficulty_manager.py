class DifficultyManager:
    """
    Static DifficultyManager for setting an initial difficulty level at the
    start of a test session.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.selected_difficulty = None

    def set_initial_difficulty(self, difficulty: DifficultyLevel):
        """Sets the initial difficulty level for the test session."""
        if not isinstance(difficulty, DifficultyLevel):
            raise ValueError("Invalid difficulty level.")
        self.selected_difficulty = difficulty

    def get_current_difficulty(self) -> DifficultyLevel:
        """Retrieves the currently selected difficulty level."""
        if self.selected_difficulty is None:
            raise RuntimeError("Difficulty level has not been set. Call set_initial_difficulty first.")
        return self.selected_difficulty

    def apply_difficulty_to_llm(self, topic: HFTopic):
        """
        Generates a question with the fixed difficulty setting by passing
        it to the LLMService.
        """
        if self.selected_difficulty is None:
            raise RuntimeError("Difficulty level not set. Call set_initial_difficulty first.")
        if not isinstance(topic, HFTopic):
            raise ValueError("Invalid topic: Must be an instance of HFTopic enum.")

        return self.llm_service.generate_question(topic, self.selected_difficulty)