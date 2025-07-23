from . import * # 从 task/__init__.py 添加基础模块
def pre_absorption(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"
    absorption_path = work_path + os.sep + "absorption"
    if os.path.exists(absorption_path):
        warnings.warn("吸收光谱的计算路径已存在，之前的结果将被覆盖！")
        os.chdir(absorption_path)
        check_vasp_file()
        print("吸收光谱计算的输入文件已创建！")

        return absorption_path

    os.mkdir(absorption_path)

    ### POSCAR
    poscar = work_path + os.sep + "POSCAR"

    if os.path.exists(relax_path) and check_relax_or_scf(relax_path):

        poscar = relax_path + os.sep + "CONTCAR"

    else:
        # warnings.warn("The relax not been executed or not been converged, we will use uploaded POSCAR for absorption!")
        warnings.warn("结构优化已失败、未执行或未收敛，将使用上传的POSCAR文件进行吸收光谱计算！")

    """
    自动生成 VASP 吸收光谱计算的 INCAR 文件到指定目录。
    参数:
        work_path (str): 生成INCAR文件的工作目录，默认为'./absorption'
    """

    check_poscar(poscar)
    structure = read_poscar(poscar)
    os.chdir(absorption_path)

    # ### POSCAR
    structure.to_file("POSCAR")

    ########### ############
    '''生成INCAR，需要设置一个NBANDS'''

    def get_incar_absorption():
        from pymatgen.io.vasp.inputs import Incar
        from pymatgen.core import Structure
        from pymatgen.core.periodic_table import Element

        def get_nbands():
            structure = Structure.from_file("POSCAR")

            # 总电子数
            total_electrons = 0
            for site in structure:
                total_electrons += Element(site.specie).Z
            # NBANDS估算
            nbands = int((total_electrons / 2) * 1.6)  # 1.6为经验系数
            return nbands

        nbands = get_nbands()
        absorption_incar_dict = {
            "ISTART": 1,
            "ISPIN": 1,
            "LREAL": False,
            "LWAVE": True,
            "LCHARG": True,
            "ADDGRID": True,
            "LASPH": True,
            "PREC": "Accurate",

            "ISMEAR": 0,
            "SIGMA": 0.01,  # 注意：后面的值覆盖了前面的 ISMEAR、SIGMA
            "LORBIT": 11,
            "NEDOS": 2000,  # 后面的 NEDOS 覆盖前面的
            "NELM": 60,
            "EDIFF": 1e-8,  # 后面的 EDIFF 覆盖前面的
            "ALGO": "Exact",
            "LOPTICS": True,
            "CSHIFT": 0.100,
            "NBANDS": nbands
        }
        incar = Incar(absorption_incar_dict)

        # 转为字典
        incar.write_file('INCAR')

    ########### ############
    # 写入 INCAR 文件到指定目录
    get_incar_absorption()

    # print(f"INCAR 已生成于: {os.path.join(work_path, 'INCAR')}")
    ### KPOINTS
    exec_linux_command("(echo 102; echo 2; echo 0.02) | vaspkit >> vaspkit.log", pr.hint_kpoints)
    ### POTCAR
    #exec_linux_command("(echo 103) | vaspkit >> vaspkit.log")
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    return absorption_path


def post_absorption(work_path='./absorption'):

    def polt_absorption(
            data_path='./ABSORPTION.dat',
            figsize=(10, 6),
            color='r',
            xlim=(0, None),
            ylim=(-0.2, None),
            xlabel='Energy (eV)',
            ylabel='Absorption (cm$^{-1}$)',
            title='Absorption Spectrum',
            average_columns=None,
            save_path='absorption.png',
            show=False
    ):
        """
        绘制吸收光谱图。

        参数:
            data_path (str): 数据文件路径
            figsize (tuple): 图像大小
            color (str): 曲线颜色
            xlim (tuple): x 轴范围
            ylim (tuple): y 轴范围
            xlabel (str): x 轴标签
            ylabel (str): y 轴标签
            title (str): 图像标题
            average_columns (list or None): 若指定，则对这些列取平均作为吸收强度
            save_path (str or None): 若指定，则保存图片到该路径
            show (bool): 是否显示图像
        """
        import numpy as np
        import matplotlib.pyplot as plt

        # 读取数据
        try:
            data = np.loadtxt(data_path)
        except Exception as e:
            print(f"读取数据失败: {e}")
            return

        energy = data[:, 0]
        absorption = data[:, 1]

        plt.figure(figsize=figsize)
        plt.plot(energy, absorption, color=color, label='Absorption')

        plt.xlim(*xlim)
        plt.ylim(*ylim)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()
        plt.legend()

        if save_path:
            plt.savefig(save_path, dpi=300)
        if show:
            plt.show()
        else:
            plt.close()

    dem = get_dem()
    '''计算吸收光谱'''
    absorption_3d_from_vaspkit = "(echo 711; echo 1) | vaspkit >> vaspkit.log"
    absorption_2d_from_vaspkit = "(echo 710; echo 1) | vaspkit >> vaspkit.log"
    if dem == '3D':
        dem_in = 1
        exec_linux_command(absorption_3d_from_vaspkit)
        polt_absorption()
        print('吸收光谱绘制完成， 见 absorption.png')

    elif dem == '2D':
        dem_in = 2
        exec_linux_command(absorption_2d_from_vaspkit)
        polt_absorption()
        print('吸收光谱绘制完成， 见 absorption.png')
    else:
        print('只支持2D、3D材料的吸收光谱，请检查POSCAR')

