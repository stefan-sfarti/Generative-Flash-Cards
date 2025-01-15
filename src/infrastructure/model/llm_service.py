import asyncio
import traceback
import torch
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
from langchain.vectorstores import Chroma
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
            )

            self.llm = HuggingFacePipeline(
                pipeline=pipe,
            )

            # Initialize embeddings
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                # model_kwargs={
                #     "device": self.device,
                # },
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

    async def generate_question(self, request: GenerationRequest) -> Question:
        if not self._is_ready:
            raise RuntimeError("Model not initialized")

        try:
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

            prompt = PromptTemplate(
                template="Generate a multiple choice medical question: {context}",
                input_variables=["context"]
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={
                    "prompt": prompt
                }
            )

            result = await qa_chain.ainvoke({"query": "Generate a JSON-formatted multiple-choice medical question."})
            decoded = result['result']
            print(decoded)
            question_data = await self._parse_generated_json(decoded)
            return Question(**question_data)

        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            traceback.print_exc()
            return None

    async def is_ready(self) -> bool:
        """Check if the model is ready."""
        return self._is_ready

    async def _parse_generated_json(self, generated_text: str) -> dict:
        """
         Parses the generated text into a json object, it will catch issues and create default question if necessary.
          """
        try:
            # Attempt to load the JSON from the generated text
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}')
            if json_start == -1 or json_end == -1:
                raise ValueError("No valid JSON found in the generated text.")

            json_string = generated_text[json_start: json_end + 1]

            question_data = json.loads(json_string)
            # Check if the required keys are present in the loaded JSON
            if not all(key in question_data for key in ["question", "options", "correct_answer"]):
                raise ValueError("JSON is missing required keys")

            # Basic input validation
            if not isinstance(question_data["question"], str) or not question_data["question"].strip():
                raise ValueError("Invalid question format")
            if not isinstance(question_data["options"], list) or len(question_data["options"]) != 4:
                raise ValueError("Invalid options format")
            if not isinstance(question_data["correct_answer"], str) or not question_data["correct_answer"].strip():
                raise ValueError("Invalid correct answer format")

            return question_data

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Error parsing json {str(e)}")
            # If parsing or validation fails, return a default question with a new UUID
            return {
                "id": uuid.uuid4().int,
                "question": "Error generating the question, please try again.",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
            }
