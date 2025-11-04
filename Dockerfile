# Stage 1: 构建依赖
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=2.2.1
RUN pip install poetry==$POETRY_VERSION

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Stage 2: 运行时
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]