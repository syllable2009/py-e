

uv --version
# 查看可安装的 Python 版本
uv python list --all
# 安装指定版本
uv python install 3.11
uv python uninstall 3.11
# 查看已安装的版本
uv python list
# 创建基于 Python 3.11 的虚拟环境
uv venv --python 3.12 myproject-py312

