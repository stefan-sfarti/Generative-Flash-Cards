import unittest


from uuid import uuid4
from main import FeedbackManager, Question, DifficultyLevel, HFTopic

class TestFeedbackManager(unittest.TestCase):

    def setUp(self):
        self.feedback_manager = FeedbackManager()
        self.question_id = uuid4()
        self.invalid_question_id = "invalid-uuid"

    def test_add_positive_feedback(self):
        # Test adding positive feedback for a question
        self.feedback_manager.add_feedback(self.question_id, True)
        feedback = self.feedback_manager.get_feedback(self.question_id)
        self.assertEqual(feedback['positive'], 1)
        self.assertEqual(feedback['negative'], 0)

    def test_add_negative_feedback(self):
        # Test adding negative feedback for a question
        self.feedback_manager.add_feedback(self.question_id, False)
        feedback = self.feedback_manager.get_feedback(self.question_id)
        self.assertEqual(feedback['positive'], 0)
        self.assertEqual(feedback['negative'], 1)

    def test_aggregate_feedback(self):
        # Test adding multiple feedbacks
        self.feedback_manager.add_feedback(self.question_id, True)
        self.feedback_manager.add_feedback(self.question_id, False)
        self.feedback_manager.add_feedback(self.question_id, True)
        feedback = self.feedback_manager.get_feedback(self.question_id)
        self.assertEqual(feedback['positive'], 2)
        self.assertEqual(feedback['negative'], 1)

    def test_add_feedback_with_invalid_question_id(self):
        # Test that a ValueError is raised for invalid question_id
        with self.assertRaises(ValueError):
            self.feedback_manager.add_feedback(self.invalid_question_id, True)

    def test_add_feedback_with_invalid_feedback_type(self):
        # Test that a TypeError is raised for non-boolean is_positive
        with self.assertRaises(TypeError):
            self.feedback_manager.add_feedback(self.question_id, "yes")

    def test_get_feedback_with_invalid_question_id(self):
        # Test that a ValueError is raised for invalid question_id
        with self.assertRaises(ValueError):
            self.feedback_manager.get_feedback(self.invalid_question_id)

    def test_get_feedback_with_nonexistent_question_id(self):
        # Test that get_feedback returns default values for nonexistent question_id
        feedback = self.feedback_manager.get_feedback(uuid4())
        self.assertEqual(feedback, {'positive': 0, 'negative': 0})

if __name__ == "__main__":
    unittest.main()