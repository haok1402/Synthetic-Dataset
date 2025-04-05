import os
import argparse
import redis
from sources import logger
from sources.queue import Queue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, required=True)
    parsed = parser.parse_args()

    queue = Queue(parsed.topic)
    queue.cleanup()

    itps, otps = 0.0, 0.0
    for tid in queue.redis.smembers(queue.working_tasks):
        metrics = Queue.METRICS_TEMPLATE.format(topic=parsed.topic, tid=tid)
        itps += float(queue.redis.hget(metrics, "itps") or 0)
        otps += float(queue.redis.hget(metrics, "otps") or 0)
    logger.info(f"itps: {itps:.2f}")
    logger.info(f"otps: {otps:.2f}")

if __name__ == "__main__":
    main()
