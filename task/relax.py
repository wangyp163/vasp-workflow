from . import * # 从 task/__init__.py 添加基础模块
from pymatgen.io.vasp.sets import MPRelaxSet

def pre_restart_vasp_relax(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"

    if os.path.exists(relax_path):
        os.chdir(relax_path)
        poscar = relax_path + os.sep + "CONTCAR"
        check_poscar(poscar)
        structure = read_poscar(poscar)
        structure.to_file("POSCAR")
        check_vasp_file()
        print("用于重启结构优化的文件已创建！")
        return relax_path
    else:
        warnings.warn("结构优化路径不存在，我们将启动新的结构优化过程！")
        return pre_relax(work_path)
        
def pre_relax(work_path):
    os.chdir(work_path)
    poscar = work_path + os.sep + "POSCAR"
    check_poscar(poscar)
    structure = read_poscar(poscar)

    relax_path = work_path + os.sep + "relax"
    if os.path.exists(relax_path):
        warnings.warn("结构优化路径已存在，之前的计算结果将被覆盖！")
    else:
        os.mkdir(relax_path)

    ##切换工作路径
    os.chdir(relax_path)
    ### POSCAR
    structure.to_file("POSCAR")
    ### INCAR
    #exec_linux_command(pr.incar_relax_from_vaspkit, pr.hint_incar)
    # 自定义字典
    user_incar_settings = deepcopy(pr.relax_parameter)
    user_incar_settings["ISPIN"] = 1
    user_incar_settings["LDAU"] = None
    user_incar_settings["LMAXMIX"] = None
    auto_ispin = False

    vasp_set = MPRelaxSet(structure, user_incar_settings=user_incar_settings, auto_ispin=auto_ispin)
    incar = vasp_set.incar
    incar.write_file(filename='INCAR')

    ### KPOINTS
    exec_linux_command(pr.kpoints_scf_from_vaspkit, pr.hint_kpoints)

    ### POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    check_vasp_file()
    print("结构优化的输入文件已创建！")

    return relax_path
