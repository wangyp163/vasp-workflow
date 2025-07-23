from . import * # 从 task/__init__.py 添加基础模块
from pymatgen.io.vasp.sets import MPStaticSet
import numpy as np
import matplotlib.pyplot as plt
def pre_dos(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"
    scf_path = work_path + os.sep + "scf"
    dos_path = work_path + os.sep + "dos"
    incar_status = False
    poscar = work_path + os.sep + "POSCAR"
    if os.path.exists(dos_path):
        warnings.warn("态密度计算路径已存在，之前的计算结果将被覆盖！")
        if os.path.exists(scf_path) and check_relax_or_scf(scf_path):
            ## 判断前一步自洽的状态
            chgcar = scf_path + os.sep + "CHGCAR"
            os.chdir(dos_path)
            copyfile(chgcar, "CHGCAR")
            check_vasp_file()
            print("态密度计算的输入文件已创建！")
            return dos_path
        else:
            return dos_path

    else:
        os.mkdir(dos_path)
        if os.path.exists(scf_path) and check_relax_or_scf(scf_path):
            ## 判断前一步自洽的状态
            poscar = scf_path + os.sep + "POSCAR"
            chgcar = scf_path + os.sep + "CHGCAR"
            incar =  scf_path + os.sep + "INCAR"
            incar_status = True
            os.chdir(dos_path) ## 切换目录，下面把scf的文件，复制到dos
            copyfile(chgcar, "CHGCAR")
            copyfile(incar, "INCAR")
            os.system('echo "ICHARG =  11" >> INCAR')
        else:
            warnings.warn("自洽场计算（SCF）已失败、未执行或未收敛，我们将不会使用电荷密度文件（CHGCAR）进行态密度（DOS）计算！")
            if os.path.exists(relax_path) and check_relax_or_scf(relax_path):
                poscar = relax_path + os.sep + "CONTCAR"
            else:
                warnings.warn("结构优化（RELAX）已失败、未执行或未收敛，我们将使用上传的POSCAR文件进行态密度（DOS）计算！")


    check_poscar(poscar)
    structure = read_poscar(poscar)
    os.chdir(dos_path)
    ### POSCAR
    structure.to_file("POSCAR")
    ### INCAR
    if not incar_status:
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
    exec_linux_command(pr.kpoints_dos_from_vaspkit, pr.hint_kpoints)
    ### POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    check_vasp_file()
    ### 修改INCAR
    os.system('echo "EMAX =  20" >> INCAR')
    os.system('echo "EMIN =  -20" >> INCAR')
    print("态密度计算的输入文件已创建！")
    return dos_path
    
def post_dos(work_path='./dos'):
    datas = np.loadtxt('TDOS.dat', dtype=np.float64)
    # --------------------- PLOTs ------------------------
    axe = plt.subplot(111)
    rows, cols = datas.shape
    nspin = cols - 1

    axe.plot(datas[:, 0], datas[:, 1], linewidth=1.0, color=pr.colormaps[0], label=pr.spin_labels[0])

    if (nspin > 1):
        axe.plot(datas[:, 0], datas[:, 2], linewidth=1.0, color=pr.colormaps[1], label=pr.spin_labels[1])
        axe.legend(loc='best', shadow=False, labelspacing=0.1)

    axe.set_ylabel(r'DOS', fontdict=pr.font)
    axe.set_ylabel(r'Engergy(eV)', fontdict=pr.font)
    plt.yticks(fontsize=pr.font['size'] - 2)
    axe.set_xlim((datas[:, 0][0], datas[:, 0][-1]))
    fig = plt.gcf()
    fig.set_size_inches(8, 6)
    plt.savefig('dos.png', dpi=300)
    #plt.show()
    plt.clf()
    plt.close()
