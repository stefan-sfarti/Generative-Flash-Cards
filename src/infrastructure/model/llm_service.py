import asyncio
import traceback
import random
import re
from typing import Tuple, Optional

import torch
from langchain.chains.llm import LLMChain
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.domain.interfaces import ModelService, Question, GenerationRequest
from src.domain.models import QuestionDifficulty, QuestionSource
import json
import logging
import uuid
import os

import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline


class MistralModelService(ModelService):
    def __init__(self, model_path: str = None, device="cuda:0"):
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA device not available")

        self.device = "cuda:0"
        torch.set_default_tensor_type('torch.cuda.FloatTensor')
        self._lock = asyncio.Lock()
        self.tokenizer = None
        self.model = None
        self._is_ready = False
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        self.collection_name = "medical_guidelines"
        self.persist_directory = "chroma_db"
        self.llm = None
        self.vector_store = None

    async def initialize(self) -> None:
        try:
            torch.cuda.empty_cache()

            self.tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct")

            # Load model with device_map but without specifying exact device
            base_model = AutoModelForCausalLM.from_pretrained(
                "microsoft/Phi-3.5-mini-instruct",
                torch_dtype=torch.float16,
                device_map="auto"  # Let accelerate handle device placement
            )

            self.logger.info(f"Base model device: {next(base_model.parameters()).device}")

            # Create pipeline without device specification
            pipe = pipeline(
                "text-generation",
                model=base_model,
                tokenizer=self.tokenizer,
                max_length=1024,
                truncation=True,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id if self.tokenizer.pad_token_id else self.tokenizer.eos_token_id,
                temperature=0.1,
                top_p=0.7,
                do_sample=True,
                num_return_sequences=1,
            )

            self.llm = HuggingFacePipeline(
                pipeline=pipe,
            )

            # Initialize embeddings
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                encode_kwargs={
                    "normalize_embeddings": True,
                }
            )

            # Initialize vector store
            chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            self.vector_store = Chroma(
                client=chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
            )

            # Log devices for debugging
            self.logger.info(f"Base model device: {next(base_model.parameters()).device}")
            if hasattr(self.embedding_model, 'model'):
                self.logger.info(f"Embedding model device: {next(self.embedding_model.model.parameters()).device}")

            self._is_ready = True

        except Exception as e:
            self.logger.error(f"Initialization error: {str(e)}")
            traceback.print_exc()
            raise

    def parse_question_output(self, text: str) -> Tuple[Optional[str], Optional[list], Optional[str]]:
        try:
            # Clean the output by removing any instruction text
            output_text = text.split("OUTPUT:")[-1].strip() if "OUTPUT:" in text else text

            # Extract question
            question_match = re.search(r"Question:\s*(.*?)(?=Options:|$)", output_text, re.DOTALL)
            if not question_match:
                self.logger.error("Failed to extract question")
                return None, None, None

            question = question_match.group(1).strip()

            # Extract options
            options = []
            option_text = re.search(r"Options:(.*?)(?=Correct answer:|$)", output_text, re.DOTALL)
            if option_text:
                option_lines = option_text.group(1).strip().split('\n')
                for line in option_lines:
                    line = line.strip()
                    if re.match(r'^[A-D]\.', line):
                        options.append(line)

            if len(options) != 4:
                self.logger.error(f"Invalid number of options: {len(options)}")
                return None, None, None

            # Extract correct answer
            correct_answer_match = re.search(r"Correct answer:\s*([A-D])", output_text)
            if not correct_answer_match:
                self.logger.error("Failed to extract correct answer")
                return None, None, None

            correct_answer = correct_answer_match.group(1)

            # Validate the extracted data
            if not all([question, options, correct_answer]):
                self.logger.error("Missing required components in parsed output")
                return None, None, None

            return question, options, correct_answer

        except Exception as e:
            self.logger.error(f"Error parsing question output: {str(e)}")
            return None, None, None
    async def generate_question(self, request: GenerationRequest) -> Question:
        if not self._is_ready:
            raise RuntimeError("Model not initialized")

        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 1})

            # Update prompt to request a natural language formatted question
            prompt = PromptTemplate(
                template="""Based on the following medical context, generate a multiple choice question in exactly this format:

            Question: [Write your question here]
            Options:
            A. [First option]
            B. [Second option]
            C. [Third option]
            D. [Fourth option]
            Correct answer: [A, B, C, or D]

            Context: {context}

            OUTPUT:""",
                input_variables=["context"]
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={
                    "prompt": prompt,
                    "output_key": "result"
                },
            )

            # Request the AI to generate a question
            result = await qa_chain.ainvoke({"query": "Random selection"})
            self.logger.info(f"LLM raw output: {result['result']}")
            question, options, correct_answer = self.parse_question_output(result['result'])

            return Question(
                question=question,
                options=options,
                correct_answer=correct_answer
            )
        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            traceback.print_exc()
            return Question(
                question="Error generating question. Please try again.",
                options=["A. N/A", "B. N/A", "C. N/A", "D. N/A"],
                correct_answer="A"
            )

        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            traceback.print_exc()
            return None

    async def is_ready(self) -> bool:
        """Check if the model is ready."""
        return self._is_ready

    # async def _parse_generated_json(self, generated_text: str) -> dict:
    #     """
    #     Parses the generated text into a JSON object. If issues occur, it creates a default question.
    #     """
    #     # try:
    #         # # Attempt to find and extract the JSON portion from the generated text
    #         # json_start = generated_text.find('{')
    #         # json_end = generated_text.rfind('}')
    #         # print(f"Generated text: {generated_text}")
    #         #
    #         # if json_start == -1 or json_end == -1:
    #         #     raise ValueError("No valid JSON found in the generated text.")
    #         #
    #         # json_string = generated_text[json_start: json_end + 1]
    #         #
    #         # # Attempt to parse the extracted JSON string
    #         # question_data = json.loads(json_string)
    #
    #         # Validate the required keys
    #         # if not all(key in question_data for key in ["question", "options", "correct_answer"]):
    #         #     raise ValueError("JSON is missing required keys")
    #         #
    #         # # Validate the format of the data
    #         # if not isinstance(question_data["question"], str) or not question_data["question"].strip():
    #         #     raise ValueError("Invalid question format")
    #         # if not isinstance(question_data["options"], list) or len(question_data["options"]) != 4:
    #         #     raise ValueError("Invalid options format")
    #         # if not isinstance(question_data["correct_answer"], str) or not question_data["correct_answer"].strip():
    #         #     raise ValueError("Invalid correct answer format")
    #
    #         # Return parsed data if all checks pass
    #         # return question_data
    #
    #     # except (json.JSONDecodeError, ValueError) as e:
    #     #     # Log the error encountered during parsing
    #     #     self.logger.error(f"Error parsing JSON: {str(e)}")
    #     #
    #     #     # Return a default question structure with a new UUID in case of error
    #     #     return {
    #     #         "id": str(uuid.uuid4()),
    #     #         # UUID is converted to string to avoid issues with integer overflow in some cases
    #     #         "question": "Error generating the question, please try again.",
    #     #         "options": ["Option A", "Option B", "Option C", "Option D"],
    #     #         "correct_answer": "Option A",
    #     #     }
    #
