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
