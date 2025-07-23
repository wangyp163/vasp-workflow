from . import * # 从 task/__init__.py 添加基础模块
from pymatgen.io.vasp.sets import MPStaticSet

def pre_scf(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"
    scf_path = work_path + os.sep + "scf"

    if os.path.exists(scf_path):
        warnings.warn("自洽计算路径已存在，之前的计算结果将被覆盖！")
        os.chdir(scf_path)
        check_vasp_file()
        print("自洽计算的输入文件已创建！")

        return scf_path
    else:
        os.mkdir(scf_path)

    ### POSCAR
    poscar = work_path + os.sep + "POSCAR"

    if os.path.exists(relax_path):
        os.chdir(relax_path)
        status = check_vasp()
        if status == True:
            e_converged, ionic_converged, all_converged, final_energy = check_vasp_converge()
            if all_converged:
                poscar = relax_path + os.sep + "CONTCAR"
            else:
                warnings.warn("结构优化未收敛，我们将使用上传的 POSCAR 进行自洽计算！")
        else:
            warnings.warn("结构优化失败，我们将使用上传的 POSCAR 进行自洽计算！")

    else:
        warnings.warn("结构优化过程尚未执行，我们将使用上传的 POSCAR 文件进行自洽计算！")

    check_poscar(poscar)
    structure = read_poscar(poscar)

    os.chdir(scf_path)
    ### POSCAR
    structure.to_file("POSCAR")
    ### INCAR
    #exec_linux_command(pr.incar_scf_from_vaspkit, pr.hint_incar)

    ispin, auto_ispin = get_ispin(structure)

    # 自定义字典
    user_incar_settings = deepcopy(pr.scf_parameter)
    user_incar_settings["ISPIN"] = ispin

    vasp_set = MPStaticSet(structure, user_incar_settings=user_incar_settings, auto_ispin=auto_ispin)
    incar = vasp_set.incar

    # 写入 INCAR 文件（假设写到当前目录）
    incar.write_file(filename='INCAR')

    ### KPOINTS
    exec_linux_command(pr.kpoints_scf_from_vaspkit, pr.hint_kpoints)

    ### POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    check_vasp_file()
    print("自洽计算的输入文件已创建！")

    return scf_path
