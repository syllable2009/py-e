# 
Python 工程化是指将 Python 项目从“脚本级”提升到可维护、可测试、可部署、可协作的工业级软件工程实践。
它不仅仅是写代码，而是围绕项目结构、依赖管理、代码质量、自动化、部署等维度建立规范.

#   结构
myproject/
├── src/                     # 源码目录（避免与测试/配置混在一起）
│   └── myproject/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       └── core/
├── tests/                   # 测试代码
│   ├── __init__.py
│   ├── test_api.py
│   └── conftest.py
├── docs/                    # 文档
├── scripts/                 # 部署/运维脚本
├── .gitignore
├── pyproject.toml           # ✅ 现代标准：依赖 + 构建配置
├── README.md
├── Makefile                 # 本地开发快捷命令
└── Dockerfile               # 容器化部署

# Poetry
Poetry 是一个 Python 依赖管理和打包工具（类似 Node.js 的 npm 或 Rust 的 cargo）。
Poetry 使用pyproject.toml 作为唯一配置文件，并在此基础上扩展了依赖解析、虚拟环境管理、发布等功能。
功能：依赖管理，虚拟环境管理，项目打包，发布到 PyPI，脚本管理
Poetry 扩展了 pyproject.toml 的语法，加入了自己的字段
pyproject.toml 是“标准”，Poetry 是“实现”。
# pyproject.toml
pyproject.toml 是一个 标准配置文件（由 PEP 518 和 PEP 621 定义）。
文件格式为 TOML（比 JSON/YAML 更简洁、易读）。

# uv
在 Python 生态中，uv 是由 Astral（Ruff 的开发团队）推出的一个超快速的 Python 包安装器和解析器，旨在替代或补充传统的工具如 pip、pip-tools、virtualenv 和 poetry 的部分功能。

uv 会自动生成并维护一个 uv.lock 文件（类似 poetry.lock 或 package-lock.json）
