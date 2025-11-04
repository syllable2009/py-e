python 使用虚拟环境.venv，创建好以后不能直接“升级”虚拟环境，因为虚拟环境是绑定到创建时所用的 Python 解释器的。一旦底层 Python 版本改变，虚拟环境就不再兼容。

brew update
brew install pyenv pyenv-virtualenv

判断当前使用的 shell 是 sh 还是 zsh
echo $0
echo $SHELL

# 对于配置 shell=bash (默认)用户:
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init - bash)"' >> ~/.profile

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
echo 'eval "$(pyenv init - bash)"' >> ~/.bash_profile
# 激活配置
source ~/.bashrc

# 对于 zsh 用户(bash 不需要执行)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init - zsh)"' >> ~/.zshrc
source ~/.zshrc

#查看安装的python版本
pyenv versions
# 安装 Python 3.13.3
pyenv install 3.13.3

# 设置当前用户的 python-version
pyenv global 3.13.3

# 确认已安装对应的版本 Python 3.13.3
python3.13 --version
mac安装 brew install python@3.13
验证安装成功 which python3.13

创建新环境，注意目录
python3.10 -m venv .venv
激活环境
source .venv/bin/activate

deactivate

删除对应的环境
rm -rf .venv 

# 安装依赖
pip install -r requirements.txt          # 如果你导出了 requirements.txt
# 或
poetry install                           # 如果使用 Poetry

pip list  # 确认依赖已安装


在 Python 生态中，uv 是由 Astral（Ruff 的开发团队）推出的一个超快速的 Python 包安装器和解析器，旨在替代或补充传统的工具如 pip、pip-tools、virtualenv 和 poetry 的部分功能。
pip install uv

1.创建项目目录app
mkdir app && cd app
2.uv初始化pyproject.toml
uv init --lib
3.手动调整pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "app"
version = "0.1.0"
description = "A production-ready FastAPI app with uv"
authors = [{name = "Your Name", email = "you@example.com"}]
requires-python = ">=3.10"
dependencies = [
"fastapi>=0.109.0",
"uvicorn[standard]>=0.27.0",
]

[project.optional-dependencies]
dev = [
"pytest>=8.0",
"pytest-asyncio>=0.23.0",
"httpx>=0.25.0",
"ruff>=0.4.0",
"mypy>=1.8.0",
"types-requests",
]

[tool.setuptools.packages.find]
where = ["src"] # 避免“当前目录可导入”的陷阱。
include = ["app*"]

[project.scripts]
start = "app.main:run"

# tool.setuptools.packages.find是 setuptools（Python 官方打包工具）在 pyproject.toml 中用于自动发现项目源代码包（packages） 的指令。它的作用是告诉 setuptools：
# “请到 src/ 目录下去找 Python 包，只要名字以 app 开头的都包含进来。”

4. 安装依赖:这会自动创建虚拟环境（默认在 .venv）并安装所有包。
uv venv [路径] 创建虚拟环境.venv
source .venv/bin/activate
uv sync --all-extras  # 安装主依赖 + dev 依赖
uv sync               # 仅安装生产依赖
在开发过程中直接安装
uv add requests 添加开发依赖
uv add "httpx>=0.25.0,<0.27.0" 
uv add requests@latest
uv add --group dev pytest-asyncio 添加生产依赖
也可以手动编辑pyproject.toml
   dependencies = [
   "requests>=2.32.5",
   ]
   [dependency-groups]
   dev = [
   "pytest-asyncio>=1.2.0",
   ]
编辑完成uv sync --all-extras或者uv sync
5. 编写代码
src/app/main.py
src/app/api/v1/endpoints.py

# 在项目根目录下执行
uv run python -m my_package.scripts.my_script


6. 添加测试
tests/test_api.py
   import pytest
   from httpx import AsyncClient
   from app.main import app

@pytest.mark.asyncio
async def test_hello():
async with AsyncClient(app=app, base_url="http://test") as ac:
response = await ac.get("/api/v1/hello")
assert response.status_code == 200
assert response.json() == {"message": "Hello from FastAPI + uv!"}
7.运行测试
uv run pytest
# 路径是相对于当前工作目录的，方法名不需要加 test_ 前缀（但函数本身必须以 test_ 开头才能被 pytest 识别）
uv run pytest path/to/test.py::ClassName::test_method
8.添加 Makefile（可选但推荐）
.PHONY: install test lint format type-check

install:
uv sync --all-extras

test:
uv run pytest

lint:
uv run ruff check src tests

format:
uv run ruff format src tests

type-check:
uv run mypy src

serve:
uv run start

现在你可以用 make test、make serve 等命令。

9.Dockerfile

# 构建阶段
FROM python:3.11-slim AS builder

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# 复制依赖声明
COPY --chown=app:app pyproject.toml ./

# 安装依赖（仅生产依赖）
RUN /uv pip install --system --no-cache-dir --compile .

# 复制源码
COPY --chown=app:app src/ ./src/

# 运行阶段（可选：直接使用 builder 镜像）
FROM builder AS runner
EXPOSE 8000
CMD ["python", "-m", "app.main"]

# 构建镜像
docker build -t fastapi-uv-app .

# 运行
docker run -p 8000:8000 fastapi-uv-app



