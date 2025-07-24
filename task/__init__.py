from core.utils import *
# 导入所有task模块并导出函数
task_modules = [
    'relax', 'scf', 'dos', 'phonon', 'magnetic', 
    'elastic', 'absorption', 'bader', 'pbe_band'
]

# 动态导入所有task模块的函数到当前命名空间
for module_name in task_modules:
    try:
        module = importlib.import_module(f'task.{module_name}')
        # 获取模块中的所有公共函数
        for attr_name in dir(module):
            if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                globals()[attr_name] = getattr(module, attr_name)
    except ImportError:
        pass  # 如果模块不存在则跳过
