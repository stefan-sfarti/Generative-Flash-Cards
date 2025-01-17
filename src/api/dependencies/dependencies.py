# src/api/dependencies/dependencies.py
import os
from src.infrastructure.model.llm_service import PhiModelService
from src.infrastructure.cache.redis_cache_service import RedisCacheService
from src.application.question_service import DefaultQuestionService
from dotenv import load_dotenv
import logging
import torch

# Loads .env file
load_dotenv(dotenv_path="./config/.env")

_model_service = None
_cache_service = None
_question_service = None


def get_model_service():
   global _model_service
   if _model_service is None:
        model_path = "./mistral_mcq_final"
        _model_service = PhiModelService(model_path=model_path)
   return _model_service

def get_cache_service():
   global _cache_service
   if _cache_service is None:
      redis_host = os.environ.get("REDIS_HOST")
      redis_port = os.environ.get("REDIS_PORT")
      redis_db = os.environ.get("REDIS_DB")
      if redis_port is None:
        redis_port = 6379  # default port
      if redis_db is None:
          redis_db = 0  # default db
      _cache_service = RedisCacheService(redis_host=redis_host, redis_port=int(redis_port), redis_db=int(redis_db))
   return _cache_service


def get_question_service():
    global _question_service
    if _question_service is None:
       cache_service = get_cache_service()
       model_service = get_model_service()
       _question_service = DefaultQuestionService(cache_service, model_service)
    return _question_service


async def init_app_dependencies():
    logging.basicConfig(level=logging.INFO)
    model_service = get_model_service()
    cache_service = get_cache_service()
    await model_service.initialize()