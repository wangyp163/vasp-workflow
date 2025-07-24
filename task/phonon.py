from core.utils import *
from core.Function import *
from core.parameter_function import *

def pre_phonon(work_path):
    print("使用密度泛函微扰理论（DFPT）计算声子谱（phonon）")
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"
    phonon_path = work_path + os.sep + "phonon"

    if os.path.exists(phonon_path):
        warnings.warn("声子谱计算的路径已存在，之前的结果将被覆盖！")
        os.chdir(phonon_path)
        check_vasp_file()
        print("声子谱计算的输入文件已创建！")
        return phonon_path

    os.mkdir(phonon_path)
    ### POSCAR
    poscar = work_path + os.sep + "POSCAR"
    if os.path.exists(relax_path) and check_relax_or_scf(relax_path):
        poscar = relax_path + os.sep + "CONTCAR"
    else:
        warnings.warn("结构优化计算已失败、未执行或未收敛，我们将使用上传的POSCAR文件进行声子谱计算！")

    check_poscar(poscar)
    structure = read_poscar(poscar)

    os.chdir(phonon_path)
    ### POSCAR
    structure.to_file("POSCAR")
    dem = get_dem("POSCAR")
    ##声子谱能带的配置文件
    phonopy_kpath = None
    phonopy_enlarge = None
    phonopy_dem = None
    if dem[0] == "1":
        phonopy_kpath = pr.phonopy_kpath_1d
        phonopy_enlarge = pr.phonopy_enlarge1d
        phonopy_dem = pr.dem1
    elif dem[0] == "2":
        phonopy_kpath = pr.phonopy_kpath_2d
        phonopy_enlarge = pr.phonopy_enlarge2d
        phonopy_dem = pr.dem2
    else:
        phonopy_kpath = pr.phonopy_kpath_3d
        phonopy_enlarge = pr.phonopy_enlarge3d
        phonopy_dem = pr.dem3
    exec_linux_command(phonopy_kpath, pr.hint_phonopy_kpath)

    structure.to_file(pr.poscar_unit)

    exec_linux_command(phonopy_enlarge, pr.hint_phonopy)
    copyfile(pr.sposcar, "POSCAR")

    ## INCAR
    exec_linux_command(pr.phonopy_incar, pr.hint_incar)
    os.system('echo "NSW = 1" >> INCAR')
    os.system('echo "NELM = 100" >> INCAR')
    os.system('echo "NELMDL = -5" >> INCAR')
    os.system('echo "ENCUT = 500" >> INCAR')

    ## POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)

    ## KPOINTS
    exec_linux_command(pr.kpoints_scf_from_vaspkit, pr.hint_kpoints)

    ## 修改声子谱能带的配置文件
    band_conf = {}
    with open("KPATH.phonopy", "r") as f:
        for index, each in enumerate(f.readlines()):
            each_strip = each.strip()
            if each_strip != "" and each_strip[0] != "#":
                each_strip = each_strip.split("=")
                band_conf[each_strip[0].strip()] = each_strip[1].strip()

    del band_conf["NPOINTS"]
    del band_conf["TETRAHEDRON"]
    del band_conf["PDOS"]
    del band_conf["BAND_CONNECTION"]
    band_conf["DIM"] = phonopy_dem
    band_conf["PRIMITIVE_AXES"] = "Auto"
    band_conf["BAND_POINTS"] = str(101)
    with open(pr.phonopy_kpath_name, "w") as f:
        for each in band_conf.keys():
            f.write(each + " = " + band_conf[each])
            f.write("\n")
    check_vasp_file()
    print("声子谱计算的输入文件已创建！")

    return phonon_path

def post_phonon():
    ## 获取声子谱能带和态密度
    exec_linux_command(pr.phonopy_get_force, pr.hint_phonopy_get_force)
    exec_linux_command(pr.phonopy_get_band, pr.hint_phonopy_get_band)
    os.system(pr.phonopy_get_data)