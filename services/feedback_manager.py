class FeedbackManager:
    """
    Manages feedback for each generated question.
    Feedback is stored as positive or negative per question ID.
    """

    def __init__(self):
        self.feedback_data: Dict[UUID, Dict[str, int]] = {}

    def add_feedback(self, question_id: UUID, is_positive: bool):
        if not isinstance(question_id, UUID):
            raise ValueError("Invalid question_id: Must be a UUID instance.")
        if not isinstance(is_positive, bool):
            raise TypeError("Invalid feedback type: Must be a boolean value.")

        if question_id not in self.feedback_data:
            self.feedback_data[question_id] = {'positive': 0, 'negative': 0}
        if is_positive:
            self.feedback_data[question_id]['positive'] += 1
        else:
            self.feedback_data[question_id]['negative'] += 1


    def get_feedback(self, question_id: UUID):
        if not isinstance(question_id, UUID):
            raise ValueError("Invalid question_id: Must be a UUID instance.")
        return self.feedback_data.get(question_id, {'positive': 0, 'negative': 0})
