import argparse
import os
from core.Function import *

def main():
    parser = argparse.ArgumentParser(description='VASP Workflow 主程序')
    
    # 必需参数
    parser.add_argument('-i', '--input', type=str, required=True, help='VASP计算任务的工作路径')
    parser.add_argument('-t', '--task', choices=['relax', 'scf', 'dos', 'PBE_band', 'phonon', 'magnetic', 'elastic', 'absorption', 'bader'], required=True, help='任务类型')
    parser.add_argument('-p', '--process', choices=['pre', 'run', 'post'], required=True, help='处理类型: pre (预处理), run (运行计算), post (后处理)')
    
    args = parser.parse_args()
    if not args.input:
        print('未提供 VASP 计算任务的工作路径！')
        exit(-1)
    # 运行部分
    work_path = os.path.abspath(args.input)

    # 根据阶段类型执行相应操作
    if args.process == 'pre':
        # 预处理阶段
        from core.task_manager import pre_vasp
        pre_vasp(work_path, args)
    elif args.process == 'run':
        # 运行计算阶段
        from core.task_manager import run_vasp
        run_vasp(work_path, args.task)
    elif args.process == 'post':
        # 后处理阶段
        from core.task_manager import post_vasp
        post_vasp(work_path, args.task)

if __name__ == '__main__':
    main()
