# Python 工程化（即构建可维护、可测试、可部署的高质量软件系统）
Python 工程化是指将 Python 项目从“脚本级”提升到可维护、可测试、可部署、可协作的工业级软件工程实践。
它不仅仅是写代码，而是围绕项目结构、依赖管理、代码质量、自动化、部署等维度建立规范.

# Python 工程化的要求
项目模板生成器 + 依赖管理 + 虚拟环境 + 打包 

# 最佳实践
很多团队开始采用 Poetry 管理项目 + uv 加速安装 的混合模式
Poetry 是“项目经理”，uv 是“安装火箭”。两者不是互斥，而是互补。
Poetry 是“一体化项目管理工具”。
uv 是“高性能底层依赖引擎”，可作为 Poetry/pip 的加速替代。

# poetry的使用
Poetry 是一个 Python 依赖管理和打包工具（类似 Node.js 的 npm 或 Rust 的 cargo）。
Poetry 使用pyproject.toml 作为唯一配置文件，并在此基础上扩展了依赖解析、虚拟环境管理、发布等功能。
功能：依赖管理，虚拟环境管理，项目打包，发布到 PyPI，脚本管理
Poetry 扩展了 pyproject.toml 的语法，加入了自己的字段
pyproject.toml 是“标准”，Poetry 是“实现”
Poetry 自动创建并管理虚拟环境，确保团队成员环境一致。

# pyproject.toml
pyproject.toml 是一个 标准配置文件（由 PEP 518 和 PEP 621 定义）。
文件格式为 TOML（比 JSON/YAML 更简洁、易读）。

# uv
在 Python 生态中，uv 是由 Astral（Ruff 的开发团队）推出的一个超快速的 Python 包安装器和解析器，旨在替代或补充传统的工具如 pip、pip-tools、virtualenv 和 poetry 的部分功能。
uv 会自动生成并维护一个 uv.lock 文件（类似 poetry.lock 或 package-lock.json）

# poetry的使用
python3.10 --version # 确保安装py的对应版本
poetry --version # 确保安装poetry 
uv --version # 确保安装uv

poetry new demo # 创建项目
cd demo
poetry env activate
deactivate
poetry install # 检查 pyproject.toml 中的 python = "^3.10" 等约束,在系统中查找匹配的 Python 解释器,用该解释器创建虚拟环境并安装依赖
poetry add requests # 初始化依赖，这会更新 pyproject.toml 和 poetry.lock。
poetry env remove # 删除虚拟环境
或者指定 poetry env use python3.10 # 重新创建一个基于 Python 3.10 的虚拟环境

poetry env info
poetry env info --path # 查询虚拟环境地址
poetry add --group dev black ipython # 安装dev环境依赖

uv pip install black ipython httpx # 使用 uv 在当前激活的虚拟环境中安装
或者uv pip install --python $(poetry env info --path)/bin/python black ipython
uv安装的依赖不会出现在 pyproject.toml 中，仅用于临时开发工具（如调试、格式化、性能分析等）

poetry config virtualenvs.in-project true # 在项目根目录生成 .venv/，便于 IDE 自动识别，也方便 CI 清理



# poetry 运行 poetry run python -m myproject.app.main
要让 poetry run python -m my-e.app.main 成功运行，必须满足：
pyproject.toml 中 name = "myproject"
存在 myproject/ 目录（与 name 完全一致）
myproject/__init__.py 存在（可以为空）
已执行 poetry install（将项目作为可编辑包安装） # 将当前项目以 可编辑模式（editable install） 安装进去

