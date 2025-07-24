#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/7/23 18:16
# @Author : Wangyp

from core.utils import *
from . import parameter_function as pr
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.core.structure import Structure
from ase.io import read


class VASP_ERROR(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
        
def exec_linux_command(command, hint = "Command "):
    status = os.system(command)
    if status != 0:
        raise VASP_ERROR("错误:" + hint + "出错!")
    #print(hint + "已完成!")

def get_ispin(structure=None,magnetic_elements=None):
    """
    根据结构自动判断是否需要自旋极化，并生成对应的 VASP 输入文件。
    Si、C 等常见非磁性元素会自动设为 ISPIN=1，不添加 MAGMOM；
    有磁性元素时 ISPIN=2，并自动加 MAGMOM。
    """
    if magnetic_elements is None:
        magnetic_elements = {
            "Fe", "Co", "Ni", "Mn", "Cr", "V", "Cu", "Gd", "Eu",
            "Tb", "Dy", "Er", "Ho", "Nd", "Sm", "Pr", "Ce","O"
        }
    elements_in_structure = {str(site.specie) for site in structure}
    #print(elements_in_structure)

    if elements_in_structure & magnetic_elements:
        ispin = 2
        auto_ispin = True
    else:
        ispin = 1
        auto_ispin = False
    return ispin, auto_ispin

def check_vasp_file():
    required_files = ["INCAR", "POSCAR", "KPOINTS", "POTCAR"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        raise VASP_ERROR(f"错误：{','.join(missing_files)}文件缺失。")

def read_poscar(poscar):
    try:
        structure = Structure.from_file(poscar)
    except:
        raise VASP_ERROR("错误：POSCAR 文件格式错误或不存在！")
    return structure

def check_poscar(poscar):
    if not os.path.exists(poscar):
        raise VASP_ERROR("错误：POSCAR 文件不存在！")

def check_vasp_converge():
    vasp_run_ = Vasprun("vasprun.xml", parse_dos=False, parse_eigen=False)

    e_converged = vasp_run_.converged_electronic
    ionic_converged = vasp_run_.converged_ionic
    all_converged = vasp_run_.converged
    final_energy = vasp_run_.final_energy

    return e_converged, ionic_converged, all_converged, final_energy

def check_vasp():
    exec_linux_command(pr.vasp_success, pr.hit_grep_time)
    with open(pr.ourcar_log, "r") as f:
        data = f.readline()
        data = int(data.strip())
        if data > 0:
            return True
        else:
            return False

def check_relax_or_scf(work_path):
    os.chdir(work_path)
    status = check_vasp()
    if status == True:
        e_converged, ionic_converged, all_converged, final_energy = check_vasp_converge()
        if all_converged:
            return True
    return False

def get_dem(poscar = "POSCAR"):
    atoms = read(poscar)
    from ase.geometry.dimensionality import analyze_dimensionality
    intervals = analyze_dimensionality(atoms, method='RDA')
    m = intervals[0]
    return m.dimtype
