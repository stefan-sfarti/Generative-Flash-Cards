import redis
import json
from typing import Optional
from src.domain.interfaces import CacheService, Question
from src.domain.models import QuestionDifficulty
import logging


class RedisCacheService(CacheService):
    def __init__(self, redis_host: str, redis_port: int, redis_db: int):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.logger = logging.getLogger(__name__)

    async def get_cached_question(self, topic: str, difficulty: QuestionDifficulty) -> Optional[Question]:
        key = self._generate_cache_key(topic, difficulty)
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return Question(**json.loads(cached_data))
            return None
        except redis.exceptions.ConnectionError as e:
            self.logger.error(f"Error connecting to redis {str(e)}")
            return None

    async def cache_question(self, question: Question, topic: str, difficulty: QuestionDifficulty) -> None:
        key = self._generate_cache_key(topic, difficulty)
        try:
            self.redis_client.set(key, question.model_dump_json())
        except redis.exceptions.ConnectionError as e:
            self.logger.error(f"Error connecting to redis {str(e)}")

    async def get_cache_size(self, topic: str, difficulty: QuestionDifficulty) -> int:
        key_pattern = self._generate_cache_key(topic, difficulty) + '*'
        try:
            return len(self.redis_client.keys(key_pattern))
        except redis.exceptions.ConnectionError as e:
            self.logger.error(f"Error connecting to redis {str(e)}")
            return 0

    def _generate_cache_key(self, topic: str, difficulty: QuestionDifficulty) -> str:
        return f"question:{topic}:{difficulty.value}"