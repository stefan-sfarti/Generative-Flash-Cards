import unittest
from main import DifficultyManager, DifficultyLevel, HFTopic, LLMService

class MockLLMService(LLMService):
    """Mock LLMService to verify the difficulty level passed."""
    def __init__(self):
        self.received_difficulty = None

    def generate_question(self, topic, difficulty):
        # Capture the difficulty to verify correct application
        self.received_difficulty = difficulty
        return f"Question for {difficulty} on {topic}."

class TestStaticDifficultyManager(unittest.TestCase):

    def setUp(self):
        self.mock_llm_service = MockLLMService()
        self.difficulty_manager = DifficultyManager(self.mock_llm_service)

    def test_set_initial_difficulty(self):
        # Test that we can set an initial difficulty level
        self.difficulty_manager.set_initial_difficulty(DifficultyLevel.INTERMEDIATE)
        selected_difficulty = self.difficulty_manager.get_current_difficulty()
        self.assertEqual(selected_difficulty, DifficultyLevel.INTERMEDIATE)

    def test_generate_question_with_static_difficulty(self):
        # Test that the selected difficulty level is applied for question generation
        self.difficulty_manager.set_initial_difficulty(DifficultyLevel.ADVANCED)
        self.difficulty_manager.apply_difficulty_to_llm(HFTopic.DIAGNOSIS)
        self.assertEqual(self.mock_llm_service.received_difficulty, DifficultyLevel.ADVANCED)

    def test_set_initial_difficulty_invalid(self):
        # Ensure ValueError is raised for invalid difficulty level
        with self.assertRaises(ValueError):
            self.difficulty_manager.set_initial_difficulty("invalid-difficulty")

    def test_get_current_difficulty_without_setting(self):
        # Ensure RuntimeError is raised if get_current_difficulty is called before setting
        with self.assertRaises(RuntimeError):
            self.difficulty_manager.get_current_difficulty()

    def test_apply_difficulty_to_llm_without_setting_difficulty(self):
        # Ensure RuntimeError is raised if apply_difficulty_to_llm is called before setting difficulty
        with self.assertRaises(RuntimeError):
            self.difficulty_manager.apply_difficulty_to_llm(HFTopic.DIAGNOSIS)

    def test_apply_difficulty_to_llm_invalid_topic(self):
        # Ensure ValueError is raised if topic is not a valid HFTopic
        self.difficulty_manager.set_initial_difficulty(DifficultyLevel.BEGINNER)
        with self.assertRaises(ValueError):
            self.difficulty_manager.apply_difficulty_to_llm("invalid-topic")


if __name__ == "__main__":
    unittest.main()
