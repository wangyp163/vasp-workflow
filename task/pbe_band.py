from core.utils import *
from core.Function import *
from core.parameter_function import *

def pre_vasp_PBE_band(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"
    scf_path = work_path + os.sep + "scf"
    PBE_band_path = work_path + os.sep + "PBE_band"
    incar_status = False
    poscar = work_path + os.sep + "POSCAR"
    if os.path.exists(PBE_band_path):
        warnings.warn("PBE 能带计算路径已存在，之前的计算结果将被覆盖！")
        if os.path.exists(scf_path) and check_relax_or_scf(scf_path):
            ## 判断前一步自洽的状态
            chgcar = scf_path + os.sep + "CHGCAR"
            os.chdir(PBE_band_path)
            copyfile(chgcar, "CHGCAR")
            check_vasp_file()
            print("PBE 能带计算的输入文件已创建！")
            return PBE_band_path
        else:
            return PBE_band_path

    else:
        os.mkdir(PBE_band_path)
        if os.path.exists(scf_path) and check_relax_or_scf(scf_path):
            ## 判断前一步自洽的状态
            poscar = scf_path + os.sep + "POSCAR"
            chgcar = scf_path + os.sep + "CHGCAR"
            incar =  scf_path + os.sep + "INCAR"
            incar_status = True
            os.chdir(PBE_band_path) ## 切换目录，下面把scf的文件，复制到PBE_band
            copyfile(chgcar, "CHGCAR")
            copyfile(incar, "INCAR")
            os.system('echo "ICHARG =  11" >> INCAR')
        else:
            warnings.warn("自洽场计算（SCF）已失败、未执行或未收敛，我们将不会使用电荷密度文件（CHGCAR）进行PBE 能带计算！")
            if os.path.exists(relax_path) and check_relax_or_scf(relax_path):
                poscar = relax_path + os.sep + "CONTCAR"
            else:
                #warnings.warn("The relax not been executed or not been converged, we will use uploaded POSCAR for PBE_band!")
                warnings.warn("结构优化（RELAX）已失败、未执行或未收敛，我们将使用上传的 POSCAR 文件进行 PBE 能带计算！")

    check_poscar(poscar)
    structure = read_poscar(poscar)
    os.chdir(PBE_band_path)
    ### POSCAR
    structure.to_file("POSCAR")
    dem = get_dem("POSCAR")
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
    if dem[0] == "1":
        exec_linux_command(pr.kpoints_1d_band_from_vaspkit, pr.hint_kpoints)
    elif dem[0] == "2":
        exec_linux_command(pr.kpoints_2d_band_from_vaspkit, pr.hint_kpoints)
    else:
        exec_linux_command(pr.kpoints_bulk_band_from_vaspkit, pr.hint_kpoints)
    exec_linux_command(pr.copy_kpath_to_kpoints, pr.hint_cp)
    ### POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    check_vasp_file()
    print("PBE 能带计算的输入文件已创建！")
    return PBE_band_path

def plot_PBE_band():
    # ------------------- Data Read ----------------------
    group_labels = []
    xtick = []
    with open('KLABELS', 'r') as reader:
        lines = reader.readlines()[1:]
    for i in lines:
        s = i.encode('utf-8')  # .decode('latin-1')
        if len(s.split()) == 2 and not s.decode('utf-8', 'ignore').startswith('*'):
            klabel = str(s.decode('utf-8', 'ignore').split()[0])
            for j in range(len(pr.Greek_alphabets)):
                if (klabel.find(pr.Greek_alphabets[j].upper()) >= 0):
                    latex_exp = r'' + '$\\' + str(pr.Greek_alphabets[j]) + '$'
                    klabel = klabel.replace(str(pr.Greek_alphabets[j].upper()), str(latex_exp))
            if (klabel.find('_') > 0):
                n = klabel.find('_')
                klabel = klabel[:n] + '$' + klabel[n:n + 2] + '$' + klabel[n + 2:]
            group_labels.append(klabel)
            xtick.append(float(s.split()[1]))
    datas = np.loadtxt('BAND.dat', dtype=np.float64)

    # --------------------- PLOTs ------------------------
    axe = plt.subplot(111)
    axe.axhline(y=0, xmin=0, xmax=1, linestyle='--', linewidth=0.5, color='0.5')
    for i in xtick[1:-1]:
        axe.axvline(x=i, ymin=0, ymax=1, linestyle='--', linewidth=0.5, color='0.5')

    nspin = datas.shape[1] - 1
    for i in range(nspin):
        axe.plot(datas[:, 0], datas[:, i + 1], linewidth=1.0, color=pr.colormaps[i], label=pr.spin_labels[i], linestyle=pr.line_style[i])
    if (nspin > 1):
        axe.legend(loc='best', shadow=False, labelspacing=0.1)
    axe.set_ylabel(r'$\mathrm{Energy}$ (eV)', fontdict=pr.font)
    axe.set_xticks(xtick)
    plt.yticks(fontsize=pr.font['size'] - 2)
    axe.set_xticklabels(group_labels, rotation=0, fontsize=pr.font['size'] - 2)
    axe.set_xlim((xtick[0], xtick[-1]))
    plt.ylim((-20, 20))  # set y limits manually
    fig = plt.gcf()
    fig.set_size_inches(8, 6)
    plt.savefig('band.png', dpi=300)
    plt.clf()
    plt.close()
    #plt.show()
