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