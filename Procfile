web: uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT
worker: uv run arq src.worker.WorkerSettings
release: uv run alembic upgrade head
