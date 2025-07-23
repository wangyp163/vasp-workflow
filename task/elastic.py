from . import * # 从 task/__init__.py 添加基础模块

def pre_elastic(work_path):
    os.chdir(work_path)
    relax_path = work_path + os.sep + "relax"
    elastic_path = work_path + os.sep + "elastic"
    if os.path.exists(elastic_path):
        warnings.warn("弹性计算路径已存在，之前的结果将被覆盖！")
        os.chdir(elastic_path)
        check_vasp_file()
        print("弹性计算的输入文件已创建！")

        return elastic_path

    os.mkdir(elastic_path)

    ### POSCAR
    poscar = work_path + os.sep + "POSCAR"

    if os.path.exists(relax_path) and check_relax_or_scf(relax_path):

        poscar = relax_path + os.sep + "CONTCAR"

    else:
        #warnings.warn("The relax not been executed or not been converged, we will use uploaded POSCAR for elastic!")
        warnings.warn("结构优化已失败、未执行或未收敛，将使用上传的POSCAR文件进行弹性计算！")

    """
    自动生成 VASP 弹性常数计算的 INCAR 文件到指定目录。
    参数:
        work_path (str): 生成INCAR文件的工作目录，默认为'./elastic'
    """

    check_poscar(poscar)
    structure = read_poscar(poscar)
    os.chdir(elastic_path)

    # ### POSCAR
    structure.to_file("POSCAR")

    # 写入 INCAR 文件到指定目录
    exec_linux_command(pr.incar_elastic_from_vaspkit, pr.hint_incar)

    # print(f"INCAR 已生成于: {os.path.join(work_path, 'INCAR')}")
    ### KPOINTS
    exec_linux_command("(echo 102; echo 2; echo 0.04) | vaspkit >> vaspkit.log", pr.hint_kpoints)
    ### POTCAR
    exec_linux_command(pr.potcar_from_vaspkit, pr.hint_potcar)
    return elastic_path


def post_elastic(work_path='./elastic'):
    exec_linux_command('echo "AUTO_PLOT = .TRUE." >> ~/.vaspkit')
    dem = get_dem()
    '''计算弹性模量'''
    elastic_from_vaspkit = "(echo 203) | vaspkit >> elastic.dat"
    exec_linux_command(elastic_from_vaspkit)
    elastc_tensor_cp = "(cp ELASTIC_TENSOR ELASTIC_TENSOR.in)"
    exec_linux_command(elastc_tensor_cp)
    #判断是3D结构还是2D结构
    if dem == '3D':
        dem_in = 1
    if dem == '2D':
        dem_in = 2

    '''体弹性模量'''
    b_modulus_from_vaspkit = f"(echo 204; echo {dem_in}; echo 1) | vaspkit >> vaspkit.log"
    #print('体弹性模量图绘制完成： Bulk_Modulus.jpg')

    '''杨氏模量'''
    y_modulus_from_vaspkit = f"(echo 204; echo {dem_in}; echo 2)| vaspkit >> vaspkit.log"
    #print('杨氏模量图绘制完成： Young_Modulus.jpg')

    '''3D剪切模量'''
    s_modulus_min_3d_from_vaspkit = f"(echo 204; echo {dem_in}; echo 3) | vaspkit >> vaspkit.log"
    #print('剪切模量图绘制完成， Shear_Modulus_Min.jpg')
    s_modulus_max_3d_from_vaspkit = f"(echo 204; echo {dem_in}; echo 4) | vaspkit >> vaspkit.log"
    #print('剪切模量图绘制完成， Shear_Modulus_Max.jpg')

    '''2D剪切模量'''
    s_modulus_2d_from_vaspkit = f"(echo 204; echo {dem_in}; echo 1 0 0 ;echo 3) | vaspkit >> vaspkit.log"

    '''3D泊松比'''
    p_ratio_min_3d_from_vaspkit = f"(echo 204; echo {dem_in}; echo 5) | vaspkit >> vaspkit.log"
    #print('泊松比图绘制完成， Poisson_Ratio_Min.jpg')
    p_ratio_max_3d_from_vaspkit = f"(echo 204; echo {dem_in}; echo 6) | vaspkit >> vaspkit.log"
    #print('泊松比图绘制完成， Poisson_Ratio_Max.jpg')

    '''2D泊松比'''
    p_ratio_2d_from_vaspkit = f"(echo 204; echo {dem_in}; echo 1 0 0 ;echo 4) | vaspkit >> vaspkit.log"

    exec_linux_command(b_modulus_from_vaspkit)
    print('体弹性模量图绘制完成： Bulk_Modulus.jpg')
    exec_linux_command(y_modulus_from_vaspkit)
    print('杨氏模量图绘制完成： Young_Modulus.jpg')
    if dem == '3D':
        exec_linux_command(s_modulus_min_3d_from_vaspkit)
        print('剪切模量图绘制完成， Shear_Modulus_Min.jpg')
        exec_linux_command(s_modulus_max_3d_from_vaspkit)
        print('剪切模量图绘制完成， Shear_Modulus_Max.jpg')
        exec_linux_command(p_ratio_min_3d_from_vaspkit)
        print('泊松比图绘制完成， Poisson_Ratio_Min.jpg')
        exec_linux_command(p_ratio_max_3d_from_vaspkit)
        print('泊松比图绘制完成， Poisson_Ratio_Max.jpg')
    elif dem == '2D':
        exec_linux_command(s_modulus_2d_from_vaspkit)
        print('剪切模量图绘制完成， Shear_Modulus_Min.jpg')
        exec_linux_command(p_ratio_2d_from_vaspkit)
        print('泊松比图绘制完成， Poisson_Ratio_Min.jpg')
    else:
        print('只支持2D、3D材料的弹性模量分析，请检查POSCAR')

    exec_linux_command("sed -i '$d' ~/.vaspkit")
