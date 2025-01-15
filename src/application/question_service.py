from typing import Optional
from src.domain.interfaces import QuestionService, CacheService, ModelService, Question, GenerationRequest
import asyncio
import logging
from fastapi import HTTPException


class DefaultQuestionService(QuestionService):
    def __init__(self, cache_service: CacheService, model_service: ModelService):
        self.cache_service = cache_service
        self.model_service = model_service
        self.logger = logging.getLogger(__name__)

    async def get_question(self, request: GenerationRequest) -> Question:

        # cached_question = await self.cache_service.get_cached_question(request.topic, request.difficulty)
        # if cached_question:
        #     self.logger.info("Retrieved question from cache.")
        #     return cached_question

        self.logger.info("Generating a new question.")
        question = None
        try:
            question = await self.model_service.generate_question(request)
        except Exception as e:
            self.logger.error(f"Failed to generate question from model service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate question from model service: {str(e)}")

        if not question:
            self.logger.error(f"Model did not generate a question: ")
            raise HTTPException(status_code=500, detail=f"Model did not generate a question.")

        try:
            await self.cache_service.cache_question(question, request.topic, request.difficulty)
        except Exception as e:
            self.logger.error(f"Failed to cache question: {str(e)}")

        return question

    async def generate_and_cache_questions(self, request: GenerationRequest, count: int) -> None:
        for _ in range(count):
            try:
                self.logger.info(f"Generating and caching new question.")
                question = await self.model_service.generate_question(request)
                if question:
                    await self.cache_service.cache_question(question, request.topic, request.difficulty)
            except Exception as e:
                self.logger.error(f"Failed to generate and cache new question with error {str(e)}")
                continue
            await asyncio.sleep(1)