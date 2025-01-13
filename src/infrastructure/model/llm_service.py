import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from src.domain.interfaces import ModelService, Question, GenerationRequest
from src.domain.models import QuestionSource


class MistralModelService(ModelService):
    def __init__(self, model_path, device="cuda"):
        self.model_path = model_path
        self.device = torch.device(device)
        self.tokenizer = None
        self.model = None
        self._is_ready = False

    async def initialize(self) -> None:
        """Initialize the model and tokenizer."""
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        print("Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            use_cache=True,
            trust_remote_code=True,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            device_map="auto",
        ).to(self.device)

        self.model = PeftModel.from_pretrained(self.model, self.model_path)
        self.model.eval()

        self._is_ready = True
        print("Model is ready.")

    async def generate_question(self, request: GenerationRequest) -> Question:
        if not self._is_ready:
            raise RuntimeError("Model not initialized. Call initialize() first.")

        prompt = f"""Generate a multiple-choice question about heart failure based on the ESC guidelines, formatted strictly as a JSON object.
                    The JSON object must have the following fields:
                    -   "id": a unique integer identifier for the question.
                    -   "question": the question text.
                    -   "options": an array of four possible answers.
                    -   "correct_answer": the correct answer from the options.
                    -  "explanation": a brief explanation of why the correct answer is correct.
                    If a question cannot be formulated from the ESC guidelines, fallback to general heart failure knowledge.

                    Example:
                    {{
                        "id": 1,
                        "question": "What is the first-line pharmacological therapy for patients with heart failure with reduced ejection fraction?",
                        "options": ["Beta-blockers", "ACE inhibitors", "Diuretics", "Digoxin"],
                        "correct_answer": "ACE inhibitors",
                     }}"""

        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=200, temperature=0.7,
                                          pad_token_id=self.tokenizer.eos_token_id)

        decoded_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Parse question and options from the output string
        question, options, correct_answer, explanation = await self._parse_generated_text(decoded_output)

        return Question(
            question=question,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            source=QuestionSource.ESC_GUIDELINES,
            difficulty=request.difficulty,
        )

    async def is_ready(self) -> bool:
        """Check if the model is ready."""
        return self._is_ready

    async def _parse_generated_text(self, generated_text: str) -> tuple[str, list[str], str, str]:
        """
        Parses the generated text to extract question, options, correct answer, and explanation.
        This parsing is highly dependent on the model output and may require adjustments.
        """

        try:
            parts = generated_text.strip().split("###")
            question_part, options_part, correct_answer_part, explanation_part = parts
            question = question_part.replace("Question:", "").strip()
            options = [opt.strip() for opt in options_part.replace("Options:", "").strip().split("\n")]
            correct_answer = correct_answer_part.replace("Correct Answer:", "").strip()
            explanation = explanation_part.replace("Explanation:", "").strip()

        except ValueError:
            return "Error generating the question.", [], "", ""

        return question, options, correct_answer, explanation