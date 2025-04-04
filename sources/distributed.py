import os
import socket
from typing import Optional, Dict, Tuple

import redis
import redis.exceptions
from tenacity import retry, wait_random_exponential, retry_if_exception_type

from sources import logger


class Worker:

    PENDING_QUEUE_KEY_TEMPLATE = "{project}:queue:pending"
    WORKING_QUEUE_KEY_TEMPLATE = "{project}:queue:working"
    TASK_PENDING_KEY_TEMPALTE = "{project}:pending:{task_id}"
    TASK_WORKING_KEY_TEMPLATE = "{project}:working:{task_id}"

    def __init__(self, project: str):
        self.project = project
        self.pending_queue_key = Worker.PENDING_QUEUE_KEY_TEMPLATE.format(project=project)
        self.working_queue_key = Worker.WORKING_QUEUE_KEY_TEMPLATE.format(project=project)
        self.redis = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            password=os.environ.get("REDIS_PASSWORD", None),
            decode_responses=True,
        )

    @retry(
        wait=wait_random_exponential(multiplier=0.2, max=5),
        retry=retry_if_exception_type((redis.exceptions.WatchError, redis.exceptions.ConnectionError)),
    )
    def acquire_task(self) -> Optional[Tuple[str, Dict[str, str]]]:
        """
        Acquire a task from the pending queue.

        :return: A tuple containing the task ID and its payload if successful, otherwise None.
        """
        with self.redis.pipeline() as pipe:
            pipe.watch(self.pending_queue_key)

            task_id = pipe.lindex(self.pending_queue_key, 0)
            if task_id is None:
                logger.info("No pending tasks available in the queue.")
                pipe.unwatch()
                return None

            task_pending_key = Worker.TASK_PENDING_KEY_TEMPALTE.format(project=self.project, task_id=task_id)
            task_pending_val = self.redis.hgetall(task_pending_key)
            if task_pending_val is None:
                logger.error(f"Task {task_id} is not a valid pending task but was unexpectedly found in the pending queue.")
                pipe.unwatch()
                return None

            pipe.multi()
            pipe.lpop(self.pending_queue_key)
            pipe.rpush(self.working_queue_key, task_id)
            task_working_key = Worker.TASK_WORKING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
            pipe.hset(task_working_key, "hostname", socket.gethostname())
            pipe.hset(task_working_key, "pid", os.getpid())
            pipe.hset(task_working_key, "heartbeat", self.redis.time()[0])
            pipe.execute()

            logger.info(f"Successfully acquired task {task_id} from the pending queue and moved it to the working queue.")
            return task_id, task_pending_val

    @retry(
        wait=wait_random_exponential(multiplier=0.2, max=5),
        retry=retry_if_exception_type(redis.exceptions.ConnectionError),
    )
    def release_task(self, task_id: str) -> None:
        """
        Release a task from the working queue and remove its working record.

        :param task_id: The ID of the task to be released.
        """
        self.redis.lrem(self.working_queue_key, 1, task_id)
        logger.info(f"Task {task_id} has been successfully released from the working queue.")

    @retry(
        wait=wait_random_exponential(multiplier=0.2, max=5),
        retry=retry_if_exception_type(redis.exceptions.ConnectionError),
    )
    def heartbeat(self, task_id: str) -> None:
        """
        Update the heartbeat for a task in the working record to indicate it is still active.

        :param task_id: The ID of the task for which to update the heartbeat.
        """
        task_working_key = Worker.TASK_WORKING_KEY_TEMPLATE.format(project=self.project, task_id=task_id)
        self.redis.hset(task_working_key, "heartbeat",  self.redis.time()[0])
        logger.info(f"Heartbeat for task {task_id} has been successfully updated in the working record.")

if __name__ == "__main__":
    import time

    worker = Worker("textbook")
    while task := worker.acquire_task():
        task_id, task_payload = task
        for _ in range(5):
            time.sleep(1)
            worker.heartbeat(task_id)
        worker.release_task(task_id)
