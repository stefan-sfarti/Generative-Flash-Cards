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