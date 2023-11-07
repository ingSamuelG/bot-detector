from logHelper import logHelper
import redis
import os


class testy:
    def __init__(self):
        REDIS_HOST = os.getenv("REDIS_HOST")
        REDIS_PORT = os.getenv("REDIS_PORT")
        REDIS_PASS = os.getenv("REDIS_PASS")

        self.cache = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=0,
            decode_responses=True,
            password=REDIS_PASS,
        )

    def give_me_lines(self):
        self.total = logHelper().get_total_lines()
        val = self.cache.get("total_lines")
        if val:
            print(f"Found: this {val}")
        else:
            print("Not found")
            self.cache.set("total_lines", self.total)
