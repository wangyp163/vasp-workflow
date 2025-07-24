#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VASP任务管理模块
提供根据task_name动态调用对应task模块函数的功能
"""

from core.utils import *
from core.Function import *
from core.parameter_function import *

def post_vasp(work_path, task_name):
    """
    VASP计算任务完成后进行后处理。
    根据task_name执行不同的后处理操作，如DOS、PBE_band、Phonon、Magnetic、Elastic、Absorption、Bader等。
    如果计算未收敛，则抛出VASP_ERROR。
    
    Args:
        work_path (str): 工作路径。
        task_name (str): 任务类型名称。
    
    Raises:
        VASP_ERROR: 如果VASP计算任务失败或未收敛。
    """
    if task_name == pr.mag:
        work_path = work_path + os.sep + "scf"
    else:
        work_path = work_path + os.sep + task_name
    os.chdir(work_path)
    if check_vasp():
        e_converged, ionic_converged, all_converged, final_energy = check_vasp_converge()
        if all_converged:
            print("VASP 计算任务执行成功，结果已收敛！")
            print("最终能量为: {}".format(final_energy))

            # 根据task_name动态调用对应模块的所有函数
            task_functions = {
                'dos': 'dos',
                'PBE_band': 'pbe_band',
                'phonon': 'phonon',
                pr.mag: 'magnetic',
                'elastic': 'elastic',
                'absorption': 'absorption',
                'bader': 'bader',
            }
            
            # 获取对应的模块名
            module_name = task_functions.get(task_name, task_name)
            
            try:
                # 动态导入task模块
                task_module = __import__(f'task.{module_name}', fromlist=['*'])
                # 获取模块中的所有函数
                module_functions = {name: obj for name, obj in task_module.__dict__.items() 
                if callable(obj) and not name.startswith('_')}
                
                # 调用post_xxx函数或plot_xxx函数
                post_func_name = f'post_{task_name}'
                plot_func_name = f'plot_{task_name}'
                
                if post_func_name in module_functions:
                    module_functions[post_func_name](work_path)
                elif plot_func_name in module_functions:
                    module_functions[plot_func_name]()
                else:
                    # 尝试调用与task_name相关的其他函数
                    related_funcs = [name for name in module_functions.keys() 
                                   if task_name.lower() in name.lower()]
                    if related_funcs:
                        for func_name in related_funcs:
                            if func_name.startswith('post_') or func_name.startswith('plot_'):
                                module_functions[func_name](work_path if func_name.startswith('post_') else None)
                                
            except ImportError as e:
                print(f"无法导入task.{module_name}模块: {e}")
            except AttributeError as e:
                print(f"模块task.{module_name}中找不到相关函数: {e}")

        else:
            raise VASP_ERROR("错误：VASP 计算任务执行成功，但结果未收敛！")

    else:
        raise VASP_ERROR("错误：VASP 计算任务执行失败！")

def pre_vasp(work_path, args):
    """
    根据任务类型准备VASP计算任务的输入文件
    
    Args:
        work_path (str): 工作路径
        args: 命令行参数对象，包含task属性
    """
    task_name = args.task
    task_functions = {
        'relax': 'relax',
        'scf': 'scf', 
        'dos': 'dos',
        'PBE_band': 'pbe_band',
        'phonon': 'phonon',
        'magnetic': 'magnetic',
        'elastic': 'elastic',
        'absorption': 'absorption',
        'bader': 'bader',
    }
    
    if task_name in task_functions:
        module_name = task_functions[task_name]
        try:
            # 动态导入task模块
            task_module = __import__(f'task.{module_name}', fromlist=['*'])
            # 获取模块中的所有函数
            module_functions = {name: obj for name, obj in task_module.__dict__.items() 
                                if callable(obj) and not name.startswith('_')}
            
            # 调用pre_xxx函数
            pre_func_name = f'pre_{task_name}'
            if pre_func_name in module_functions:
                module_functions[pre_func_name](work_path)
                print(f"已执行{task_name}任务的预处理")
            else:
                print(f"模块task.{module_name}中找不到{pre_func_name}函数")
                
        except ImportError as e:
            print(f"无法导入task.{module_name}模块: {e}")
        except AttributeError as e:
            print(f"模块task.{module_name}中找不到{pre_func_name}函数: {e}")
    else:
        print(f"不支持的task类型: {task_name}")

def run_vasp_task(work_path, task_name):
    """
    运行指定的VASP计算任务
    
    Args:
        work_path (str): 工作路径
        task_name (str): 任务类型名称
    """
    from core.Function import run_vasp
    run_vasp(work_path, task_name)

def run_vasp(work_path, base_name):
    """
    根据task_name动态运行VASP计算任务。
    
    Args:
        work_path (str): 工作路径
        base_name (str): 任务类型名称，如elastic、dos等
    """
    # 任务名称到模块名的映射
    task_functions = {
        'relax': 'relax',
        'scf': 'scf', 
        'dos': 'dos',
        'PBE_band': 'pbe_band',
        'phonon': 'phonon',
        'magnetic': 'magnetic',
        'elastic': 'elastic',
        'absorption': 'absorption',
        'bader': 'bader',
    }
    
    if base_name == pr.mag:
        work_path = work_path + os.sep + "scf"
    else:
        work_path = work_path + os.sep + base_name
    os.chdir(work_path)
    check_vasp_file()
    
    # 动态导入对应task模块并调用相关函数
    module_name = task_functions.get(base_name, base_name)
    
    try:
        # 动态导入task模块
        task_module = __import__(f'task.{module_name}', fromlist=['*'])
        # 获取模块中的所有函数
        module_functions = {name: obj for name, obj in task_module.__dict__.items() 
                          if callable(obj) and not name.startswith('_')}
        
        # 尝试调用run_xxx或pre_run_xxx函数
        run_func_name = f'run_{base_name}'
        pre_run_func_name = f'pre_run_{base_name}'
        
        if run_func_name in module_functions:
            module_functions[run_func_name](work_path)
        elif pre_run_func_name in module_functions:
            module_functions[pre_run_func_name](work_path)
        else:
            # 默认执行VASP标准运行
            try:
                exec_linux_command(pr.vasp_std, pr.hint_vasp)
            except:
                exec_linux_command(pr.vasp_ncl, pr.hint_vasp)
                
    except ImportError:
        # 如果无法导入模块，使用默认运行方式
        try:
            exec_linux_command(pr.vasp_std, pr.hint_vasp)
        except:
            exec_linux_command(pr.vasp_ncl, pr.hint_vasp)