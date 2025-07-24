"""
核心工具模块 - 统一的基础模块导入
提供所有模块需要的基础功能和工具导入
"""

# 标准库
import os
import sys
import warnings
import importlib
from pathlib import Path
from copy import deepcopy, copyfile
from typing import Dict, Any, Optional, List, Union

# 第三方库
import numpy as np

# 设置警告过滤器
warnings.filterwarnings('ignore', category=UserWarning)

# 常用别名
PathLike = Union[str, Path]