import redis.asyncio as redisasync
import redis.exceptions
import json
from typing import Optional
from src.domain.interfaces import CacheService, Question
from src.domain.models import QuestionDifficulty
import logging


class RedisCacheService(CacheService):
    logger = logging.getLogger(__name__)

    def __init__(self, redis_host: str, redis_port: int, redis_db: int):
        try:
            self.redis_client = redisasync.Redis(host=redis_host, port=redis_port, db=redis_db)
            self.logger.info("Successfully connected to redis.")
        except redis.exceptions.RedisError as e:
            self.logger.error(f"Error initializing redis: {str(e)}")
            raise

    async def get_cached_question(self, topic: str, difficulty: QuestionDifficulty) -> Optional[Question]:
        key = self._generate_cache_key(topic, difficulty)
        try:
            cached_data = await self.redis_client.get(key)
            if cached_data:
                try:
                    self.logger.debug(f"Retrieved cached data for key {key}: {cached_data}")
                    question = Question(**json.loads(cached_data))
                    self.logger.debug(f"Parsed cached question for key {key}: {question}")
                    return question
                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Error deserializing cached question from redis {str(e)} for key {key}: {cached_data}")
                    return None
            else:
                self.logger.debug(f"No cached data found for key {key}.")

            return None
        except redis.exceptions.RedisError as e:
            self.logger.error(f"Error getting cached question from redis: {str(e)} for key {key}")
            return None

    async def cache_question(self, question: Question, topic: str, difficulty: QuestionDifficulty) -> None:
        if not question:
            self.logger.warning("Attempted to cache a None question, skipping...")
            return

        key = self._generate_cache_key(topic, difficulty)
        try:
            question_str = question.model_dump_json()
            await self.redis_client.set(key, question_str)
            self.logger.debug(f"Cached question for key {key}: {question_str}")
        except redis.exceptions.RedisError as e:
            self.logger.error(f"Error caching question to redis: {str(e)} for key {key}")

    async def get_cache_size(self, topic: str, difficulty: QuestionDifficulty) -> int:
        key_pattern = self._generate_cache_key(topic, difficulty) + '*'
        try:
            count = 0
            async for key in self.redis_client.scan_iter(match=key_pattern):
                count += 1
            self.logger.debug(f"Cache size for key {key_pattern}: {count}")
            return count
        except redis.exceptions.RedisError as e:
            self.logger.error(f"Error retrieving cache size from redis: {str(e)}")
            return 0

    def _generate_cache_key(self, topic: str, difficulty: QuestionDifficulty) -> str:
        return f"question:{topic}:{difficulty.value}"