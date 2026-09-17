FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1

ARG INSTALL_DOCLING=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/codebase/agents

RUN python -m pip install --upgrade pip
RUN python -m pip install \
    "openai>=1.0.0" \
    "anthropic>=0.34.0" \
    "google-genai>=0.8.0" \
    "PyYAML>=6.0" \
    "requests>=2.31.0" \
    "python-pptx>=1.0"

RUN if [ "$INSTALL_DOCLING" = "true" ]; then python -m pip install "docling>=2.0"; fi

COPY codebase/agents /app/codebase/agents

RUN mkdir -p /app/codebase/agents/data/ingested

CMD ["python", "classroom_cli.py", "--provider", "openai"]
