from api.openapi.dto import Response
# 代码写在py文件中，Python 会把当前的文件路径当作当前工作目录/根目录（Python 会把 some_script.py 所在目录加入 sys.path[0]）
# 绝对导入，Python 会在 sys.path 中找api,from后的名字如果不在这个目录下就无法导入，必须使用相对根目录下的包路径

python -m module_name 
# 把 module_name 当作一个模块（而不是脚本）来运行，并且将当前目录（命令执行时的 CWD）加入 sys.path 的首位。
方式	                         当前工作目录（CWD）	   sys.path[0]	     模块搜索起点
python script.py	         script.py所在目录      script.py所在目录	     从脚本所在目录开始找包
python -m package.module	你执行命令时所在的目录	    你执行命令时所在的目录	  从项目根目录开始找包

# __init__.py的作用

# 1.简化导入：from mypackage import MyClass, my_function  ← 不用写 from mypackage.module1 import MyClass
from .module1 import MyClass
from .module2 import my_function

# 2.mypackage/__init__.py
# 定义 __all__这样 from mypackage import * 只会导入这两个名字。
__all__ = ['MyClass', 'my_function']

# 3.设置包的元信息
__version__ = "1.0.0"
__author__ = "Alice"

# 4.标识为一个包路径，而非普通目录

Python 模块名不能包含 -，Poetry 通常会自动将 - 转为 _
