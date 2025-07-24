#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/7/23 18:16
# @Author : Wangyp


relax_parameter = {"LREAL" : False,
                   "LWAVE" : False,
                   "LCHARG" :False,
                   "ADDGRID":True,
                   "LASPH" : True,
                   "PREC": "Accurate",

                   "ISMEAR": 0,
                   "SIGMA" : 0.05,
                   "LORBIT": 11,
                   "NEDOS" : 2001,
                   "NELM" : 60,
                   "EDIFF":  1E-06,

                   "NSW" : 300,
                   "IBRION" : 2,
                   "ISIF" : 3,
                   "EDIFFG" : -1.5E-02,
                }

scf_parameter = {"LREAL" : False,
                 "LWAVE" : True,
                 "LCHARG" :True,
                 "ADDGRID":True,
                 "LASPH" : True,
                 "PREC": "Accurate",

                 "ISMEAR": 0,
                 "SIGMA" : 0.05,
                 "LORBIT": 11,
                 "NEDOS" : 2001,
                 "NELM" : 60,
                 "EDIFF":  1E-06,
                }



font = {'color': 'black',
        'weight': 'normal',
        'size': 13.0,
            }

Greek_alphabets = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda',
                   'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Pega']

colormaps = ['blue', 'red']
spin_labels = ['Spin-up', 'Spin-down']
line_style = ["-", "--"]


incar_relax_from_vaspkit = "(echo 101; echo STLR) | vaspkit >> vaspkit.log"
incar_scf_from_vaspkit = "(echo 101; echo ST) | vaspkit >> vaspkit.log"
incar_elastic_from_vaspkit = "(echo 101; echo STDC) | vaspkit >> vaspkit.log"

potcar_from_vaspkit = "(echo 103) | vaspkit >> vaspkit.log"
kpoints_scf_from_vaspkit = "(echo 102; echo 2; echo 0.04) | vaspkit >> vaspkit.log"
kpoints_dos_from_vaspkit = "(echo 102; echo 2; echo 0.03) | vaspkit >> vaspkit.log"
kpoints_bulk_band_from_vaspkit = "(echo 303) | vaspkit >> vaspkit.log"
kpoints_1d_band_from_vaspkit = "(echo 301) | vaspkit >> vaspkit.log"
kpoints_2d_band_from_vaspkit = "(echo 302) | vaspkit >> vaspkit.log"
mag = "magnetic"
poscar_unit = "POSCAR-unitcell"
dem3 = "2 2 2"
dem2 = "3 3 1"
dem1 = "4 1 1"
phonopy_enlarge3d = 'phonopy -d --dim="{}" -c {} >> phonopy_data.log'.format(dem3, poscar_unit)
phonopy_enlarge2d = 'phonopy -d --dim="{}" -c {} >> phonopy_data.log'.format(dem2, poscar_unit)
phonopy_enlarge1d = 'phonopy -d --dim="{}" -c {} >> phonopy_data.log'.format(dem1, poscar_unit)

sposcar = "SPOSCAR"
phonopy_incar = "(echo 101; echo PY) | vaspkit >> vaspkit.log"
phonopy_kpath_1d = "(echo 305; echo 1) | vaspkit >> vaspkit.log"
phonopy_kpath_2d = "(echo 305; echo 2) | vaspkit >> vaspkit.log"
phonopy_kpath_3d = "(echo 305; echo 3) | vaspkit >> vaspkit.log"

phonopy_kpath_name = "band.conf"


phonopy_get_force = "phonopy --fc vasprun.xml >> phonopy_data.log"
phonopy_get_band = "phonopy -c {} {} -p -s >> phonopy_data.log".format(poscar_unit, phonopy_kpath_name)
phonopy_get_data = "phonopy-bandplot --gnuplot > phonopy.out"



copy_kpath_to_kpoints = "cp KPATH.in KPOINTS"
PBE_band_from_vaspkit = "(echo 211) | vaspkit >> vaspkit.log"
tdos_from_vaspkit = "(echo 111; echo 1) | vaspkit >> vaspkit.log"

ourcar_log = "outcar.log"
vasp_success = 'grep "Elapsed time" OUTCAR | wc -l > {}'.format(ourcar_log)



vasp_std = 'mpirun vasp_std > vasp.log' #标准
vasp_ncl = 'mpirun vasp_ncl > vasp.log' #非共线

hint_incar = "创建 INCAR "
hint_potcar = "创建 POTCAR "
hint_kpoints = "创建 KPOINTS "
hint_vasp = "执行 VASP "
hit_grep_time = '执行 grep "Elapsed time" for OUTCAR '
hint_PBE_band = "创建 PBE_BAND "
hint_tdos = "创建 TDOS "
hint_cp = "执行 copy "

hint_phonopy = "创建 supercell "
hint_phonopy_kpath = "创建 phonopy kpath "
hint_phonopy_get_force = "创建 force by phonopy "
hint_phonopy_get_band = "创建 band by phonopy "
hint_phonopy_get_data = "创建 data by phonopy "
