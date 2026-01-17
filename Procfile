web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: cd backend && arq app.worker.WorkerSettings
release: cd backend && alembic upgrade head
