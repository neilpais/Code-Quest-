import redis
from rq import Queue, Worker
from test_runner import run_tests

# Redis connection
redis_conn = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Queue
q = Queue("sandbox", connection=redis_conn)


def enqueue_job(file_path, tests):
    job = q.enqueue(run_tests, file_path, tests)
    return job.id


if __name__ == "__main__":
    print("🚀 Worker started...")
    worker = Worker([q], connection=redis_conn)
    worker.work()
