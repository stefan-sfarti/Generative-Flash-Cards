import unittest
from uuid import uuid4
from enum import Enum
from typing import List

from dataclasses import dataclass

from main import MultipleChoiceQuestion, DifficultyLevel, HFTopic, ValueBasedQuestion, Range, OpenEndedQuestion


class TestQuestions(unittest.TestCase):

    def setUp(self):
        """Setare date pentru testare"""
        self.mc_question = MultipleChoiceQuestion(
            question_id=uuid4(),
            prompt="Care este funcția principală a inimii?",
            difficulty=DifficultyLevel.BEGINNER,
            topic=HFTopic.DEFINITION_AND_CLASSIFICATION,
            explanation="Inima pompează sângele în corp.",
            options=["Să pompeze sânge", "Să digere mâncarea", "Să filtreze deșeurile", "Să producă hormoni"],
            correct_option_index=0
        )

        self.value_question = ValueBasedQuestion(
            question_id=uuid4(),
            prompt="Care este intervalul normal pentru pulsul de repaus la adulți?",
            difficulty=DifficultyLevel.INTERMEDIATE,
            topic=HFTopic.ASSESSMENT_OF_HF_SEVERITY,
            explanation="Pulsul normal de repaus este între 60-100 bpm.",
            expected_value=70.0,
            unit="bpm",
            tolerance=5.0,
            value_range=Range(60.0, 100.0, "bpm")
        )

        self.open_question = OpenEndedQuestion(
            question_id=uuid4(),
            prompt="Descrie procesul de contracție a inimii.",
            difficulty=DifficultyLevel.ADVANCED,
            topic=HFTopic.DEFINITION_AND_CLASSIFICATION,
            explanation="Contracția inimii implică fluxul de ioni și semnale electrice.",
            required_keywords=["contracția", "electrice", "semnale"],
            model_answer="Contracția inimii este un proces ce implică semnale electrice ce stimulează fibrele musculare...",
            min_words=10
        )

    def test_multiple_choice_validation(self):
        """Testează validarea structurii MultipleChoiceQuestion"""
        self.assertTrue(self.mc_question.validate(), "MultipleChoiceQuestion ar trebui să fie validă.")

    def test_multiple_choice_format(self):
        """Testează formatarea MultipleChoiceQuestion"""
        formatted = self.mc_question.format()
        expected_output = (
            "Care este funcția principală a inimii?\n\n"
            "1. Să pompeze sânge\n"
            "2. Să digere mâncarea\n"
            "3. Să filtreze deșeurile\n"
            "4. Să producă hormoni\n"
        )
        self.assertEqual(formatted, expected_output,
                         "Formatarea întrebării MultipleChoiceQuestion nu corespunde așteptărilor.")

    def test_multiple_choice_correct_answer(self):
        """Testează răspunsul corect pentru MultipleChoiceQuestion"""
        self.assertTrue(self.mc_question.is_correct_answer("1"), "Răspunsul ar trebui să fie corect.")
        self.assertFalse(self.mc_question.is_correct_answer("2"), "Răspunsul ar trebui să fie incorect.")

    def test_value_based_validation(self):
        """Testează validarea structurii ValueBasedQuestion"""
        self.assertTrue(self.value_question.validate(), "ValueBasedQuestion ar trebui să fie validă.")

    def test_value_based_correct_answer_within_tolerance(self):
        """Testează răspunsul corect în intervalul de toleranță pentru ValueBasedQuestion"""
        self.assertTrue(self.value_question.is_correct_answer("72"), "Răspunsul în toleranță ar trebui să fie corect.")
        self.assertTrue(self.value_question.is_correct_answer("75"),
                        "Răspunsul la limita toleranței ar trebui să fie corect.")
        self.assertFalse(self.value_question.is_correct_answer("80"),
                         "Răspunsul în afara toleranței ar trebui să fie incorect.")


    def test_open_ended_correct_answer(self):
        """Testează răspunsul corect pentru OpenEndedQuestion"""
        response = "Contracția inimii este declanșată de semnale electrice și ioni care participă la contracția procesului."
        self.assertTrue(self.open_question.is_correct_answer(response), "Răspunsul ar trebui să fie corect.")

    def test_open_ended_incorrect_answer(self):
        """Testează răspunsul incorect care nu conține toate cuvintele cheie"""
        response = "Inima pompează sânge."
        self.assertFalse(self.open_question.is_correct_answer(response),
                         "Răspunsul ar trebui să fie incorect, deoarece lipsesc cuvintele cheie.")

    def test_open_ended_min_words_failure(self):
        """Testează dacă un răspuns cu un număr insuficient de cuvinte este respins"""
        response = "Contracția inimii."
        self.assertFalse(self.open_question.is_correct_answer(response),
                         "Răspunsul ar trebui să fie incorect, deoarece nu are suficiente cuvinte.")


if __name__ == '__main__':
    unittest.main()
