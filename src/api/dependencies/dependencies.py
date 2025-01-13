from src.infrastructure.model.llm_service import MistralModelService
from src.infrastructure.cache.redis_cache_service import RedisCacheService
from src.application.question_service import DefaultQuestionService
import os
from dotenv import load_dotenv
import logging

# Loads .env file
load_dotenv()


def get_model_service():
    model_path = "./mistral_mcq_final"
    device = "cuda" if os.environ.get("USE_CUDA") == "true" and torch.cuda.is_available() else "cpu"
    model_service = MistralModelService(model_path=model_path, device=device)
    return model_service


def get_cache_service():
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = int(os.environ.get("REDIS_PORT"))
    redis_db = int(os.environ.get("REDIS_DB"))
    cache_service = RedisCacheService(redis_host=redis_host, redis_port=redis_port, redis_db=redis_db)
    return cache_service


def get_question_service():
    cache_service = get_cache_service()
    model_service = get_model_service()
    question_service = DefaultQuestionService(cache_service, model_service)
    return question_service


async def init_app_dependencies():
    logging.basicConfig(level=logging.INFO)
    model_service = get_model_service()
    await model_service.initialize()