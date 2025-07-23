#!/bin/bash
#SBATCH -J vasp
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH -p sdicnormal

module purge
module load compiler/intel/2017.5.239       mpi/intelmpi/2017.4.239
export PATH=~/apprepo/vasp/5.4.4-intelmpi2017_optcell/app/bin:$PATH
source /public/home/huangah/miniconda3/bin/activate pymatgen-ase
export MKL_DEBUG_CPU_TYPE=5 #加速代码
export MKL_CBWR=AVX2 #使cpu默认支持avx2
export I_MPI_PIN_DOMAIN=numa #内存位置与cpu位置绑定，加速内存读取。对于内存带宽要求高的计算提速明显
WORK_DIR=./
python main.py -i $WORK_DIR --pre_relax relax
python main.py -i $WORK_DIR --run_vasp relax
python main.py -i $WORK_DIR --post_vasp relax
echo "Relax is done"
