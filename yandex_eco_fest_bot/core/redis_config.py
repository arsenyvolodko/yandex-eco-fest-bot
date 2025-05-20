import redis

from yandex_eco_fest_bot.core import config

r = redis.Redis(host=config.REDIS_HOST, port=6379, decode_responses=True)
