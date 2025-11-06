# ==============================
# 构建阶段
# ==============================
FROM python:3.11-slim AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache \
    PATH=/opt/poetry/bin:/opt/poetry-venv/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==$POETRY_VERSION

# 复制依赖文件
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# 安装依赖到虚拟环境（不包含 dev 依赖，适合生产）
# 启用 BuildKit 缓存加速依赖安装
RUN --mount=type=cache,target=/root/.cache \
    poetry config virtualenvs.create false \
    && poetry install --only=main --no-root --no-interaction --no-ansi

# ==============================
# 运行阶段
# ==============================
FROM python:3.11-slim AS runtime

# 创建非 root 用户（安全最佳实践）
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
WORKDIR /home/appuser/app

# 从 builder 阶段复制已安装的依赖
COPY --from=builder --chown=appuser:appuser /usr/local/lib/python3.11/site-packages ./site-packages
# 设置 Python 路径
ENV PYTHONPATH=/home/appuser/app/site-packages:/home/appuser/app/src

# 复制源代码
COPY --chown=appuser:appuser ./src ./src

# 暴露端口
EXPOSE 8000

# 启动命令：模块路径为 mypy.app.main:app
CMD ["python", "-m", "uvicorn", "mydemo.main:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build -t mypy-app:1.0 .
# docker run -p 8000:8000 mypy-app:1.0
# poetry run uvicorn mydemo.main:app --reload --host 0.0.0.0 --port 8000