from . import * # 从 task/__init__.py 添加基础模块
from pymatgen.io.vasp.sets import MPStaticSet

def pre_bader(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"

    bader_path = work_path + os.sep + "bader"
    poscar = work_path + os.sep + "POSCAR"
    if os.path.exists(bader_path):
        warnings.warn("bader电荷计算路径已存在，之前的计算结果将被覆盖！")
        os.chdir(bader_path)
        check_vasp_file()
        print("bader电荷计算的输入文件已创建！")
        return bader_path


    else:
        os.mkdir(bader_path)
        if os.path.exists(relax_path) and check_relax_or_scf(relax_path):
            poscar = relax_path + os.sep + "CONTCAR"
        else:
            warnings.warn("结构优化（RELAX）已失败、未执行或未收敛，我们将使用上传的POSCAR文件进行bader电荷计算！")


    check_poscar(poscar)
    structure = read_poscar(poscar)
    os.chdir(bader_path)
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
    exec_linux_command(pr.kpoints_dos_from_vaspkit, pr.hint_kpoints)
    ### POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    check_vasp_file()
    ### 修改INCAR
    os.system('echo "LAECHG =.TRUE." >> INCAR')
    os.system('echo "LELF = .TRUE." >> INCAR')
    print("bader电荷计算的输入文件已创建！")
    return bader_path



def post_bader(work_path='./bader'):
    os.system("chgsum.pl AECCAR0 AECCAR2 >> bader.log")
    # 得到ACF.dat、BCF.dat等包含价电信息的文件,ACF.dat为数据文件，bader电荷无法画图
    os.system("bader CHGCAR -ref CHGCAR_sum >> bader.log")
    os.system("grep ZVAL  POTCAR > potcar.log")
    with open("POSCAR", "r") as f:
        content = f.readlines()
        elements = content[5].strip().split()
        numbers = content[6].strip().split()
    elements_list = []
    for index,element in enumerate(elements):
        for i in range(int(numbers[index])):
            elements_list.append("{}{}".format(element, i+1))

    psu_electron = []
    with open("potcar.log", "r") as f:
        for index, each in enumerate(f.readlines()):
            ZVAL_data = each.strip().split()
            ZVAL = ZVAL_data[ZVAL_data.index("ZVAL")+2]
            for i in range(int(numbers[index])):
                psu_electron.append(float(ZVAL))

    bader_electron = []
    with open("ACF.dat", "r") as f:
        ACF = f.readlines()
        ACF_data = ACF[2:2+len(elements_list)]
        for each in ACF_data:
            bader_electron.append(float(each.strip().split()[4]))

    data = []
    col = ["原子种类","原子序号","赝势电荷", "bader_charge", "电荷变化"]
    for index in range(len(elements_list)):
        data.append([elements_list[index], index+1,psu_electron[index],bader_electron[index],bader_electron[index] - psu_electron[index]])

    df = pd.DataFrame(data, columns=col)

    # 保存为 结果为CSV 文件
    df.to_csv('bader.csv',
              index=False,  # 不保存行索引
              sep=',',  # 分隔符，默认为逗号
              na_rep='nan',  # 缺失值表示为 'nan'
              float_format='%.8f',  # 浮点数保留两位小数
              encoding='utf-8')  # 编码格式
    #print(df)
    os.system("cat bader.csv")
