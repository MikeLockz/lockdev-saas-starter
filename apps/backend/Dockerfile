FROM python:3.11.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Set path to include venv
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
