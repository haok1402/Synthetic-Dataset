"""
Author: Hao Kang  
Date: April 4, 2025  
Disclaimer: GPT-4 was used to improve the documentation of this code.

This script defines a Worker class that manages task acquisition, tracking, and completion
within a Redis-backed task queue system.
"""

import os
import socket
import time
from typing import Optional, Dict, Tuple

import redis
import redis.exceptions
from tenacity import retry, wait_random_exponential, retry_if_exception_type

from sources import logger


class Worker:
    """
    Worker class to manage tasks in a Redis-backed task queue.

    Responsibilities:
    - Fetch a task from a pending queue.
    - Move it to a working queue with associated metadata.
    - Periodically send heartbeat signals to indicate activity.
    - Release completed tasks by removing them from queues and Redis keys.
    """

    PENDING_QUEUE_KEY_TEMPLATE = "{project}:queue:pending"
    WORKING_QUEUE_KEY_TEMPLATE = "{project}:queue:working"
    TASK_PENDING_KEY_TEMPLATE = "{project}:pending:{task_id}"
    TASK_WORKING_KEY_TEMPLATE = "{project}:working:{task_id}"

    def __init__(self, project: str):
        """
        Initialize a new Worker instance for a given project.

        :param project: The name of the project, used as a namespace prefix in Redis.
        """
        self.project = project
        self.pending_queue_key = Worker.PENDING_QUEUE_KEY_TEMPLATE.format(project=project)
        self.working_queue_key = Worker.WORKING_QUEUE_KEY_TEMPLATE.format(project=project)
        self.redis = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            db=int(os.environ.get("REDIS_DB", 0)),
            username=os.environ.get("REDIS_USERNAME", None),
            password=os.environ.get("REDIS_PASSWORD", None),
            decode_responses=True,
        )

    @retry(
        wait=wait_random_exponential(multiplier=0.2, max=5),
        retry=retry_if_exception_type((redis.exceptions.WatchError, redis.exceptions.ConnectionError)),
    )
    def acquire_task(self) -> Optional[Tuple[str, Dict[str, str]]]:
        """
        Acquire the next task from the pending queue.

        Atomically moves the task to the working queue and records worker metadata,
        including hostname, process ID, and heartbeat timestamp.

        :return: A tuple (task_id, task_data) if a task is acquired, else None.
        """
        with self.redis.pipeline() as pipe:
            pipe.watch(self.pending_queue_key)

            # Peek at the next task in the pending queue
            task_id = pipe.lindex(self.pending_queue_key, 0)
            if task_id is None:
                logger.info("No pending tasks available in the queue.")
                pipe.unwatch()
                return None

            # Fetch the task's data
            task_pending_key = Worker.TASK_PENDING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
            task_pending_val = self.redis.hgetall(task_pending_key)
            if not task_pending_val:
                logger.error(f"Task {task_id} is not valid but found in the pending queue.")
                pipe.unwatch()
                return None

            # Begin atomic transaction to move task to working queue
            pipe.multi()
            pipe.lpop(self.pending_queue_key)
            pipe.rpush(self.working_queue_key, task_id)

            task_working_key = Worker.TASK_WORKING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
            pipe.hset(task_working_key, "hostname", socket.gethostname())
            pipe.hset(task_working_key, "pid", os.getpid())

            timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(self.redis.time()[0]))
            pipe.hset(task_working_key, "heartbeat", timestamp)
            pipe.execute()

            logger.info(f"Successfully acquired task {task_id} from the pending queue.")
            return task_id, task_pending_val

    @retry(
        wait=wait_random_exponential(multiplier=0.2, max=5),
        retry=retry_if_exception_type(redis.exceptions.ConnectionError),
    )
    def release_task(self, task_id: str) -> None:
        """
        Release a completed or failed task from the working queue.

        Removes the task from the working list and deletes its associated Redis keys.

        :param task_id: The ID of the task to be released.
        """
        with self.redis.pipeline() as pipe:
            pipe.lrem(self.working_queue_key, 1, task_id)

            task_working_key = Worker.TASK_WORKING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
            pipe.delete(task_working_key)

            task_pending_key = Worker.TASK_PENDING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
            pipe.delete(task_pending_key)

            pipe.execute()
            logger.info(f"Task {task_id} has been successfully released from the working queue.")

    @retry(
        wait=wait_random_exponential(multiplier=0.2, max=5),
        retry=retry_if_exception_type(redis.exceptions.ConnectionError),
    )
    def heartbeat(self, task_id: str) -> None:
        """
        Send a heartbeat for a task to indicate it's still being processed.

        Updates the heartbeat timestamp in the task's working record.

        :param task_id: The ID of the task being worked on.
        """
        task_working_key = Worker.TASK_WORKING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(self.redis.time()[0]))
        self.redis.hset(task_working_key, "heartbeat", timestamp)
        logger.info(f"Heartbeat for task {task_id} recorded at {timestamp}.")


if __name__ == "__main__":
    worker = Worker("textbook")
    while task := worker.acquire_task():
        task_id, task_payload = task
        for _ in range(5):
            time.sleep(1)
            worker.heartbeat(task_id)
        worker.release_task(task_id)
