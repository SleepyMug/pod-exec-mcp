FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    podman \
    bash \
    procps \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install .

EXPOSE 8000

CMD ["pod_exec_mcp"]
