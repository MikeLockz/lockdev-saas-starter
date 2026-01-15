FROM python:3.11.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /bin/uv

# Install system dependencies (including WeasyPrint requirements)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpango-1.0-0 \
    libharfbuzz-subset0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Set path to include venv
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
