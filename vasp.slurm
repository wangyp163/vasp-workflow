#!/bin/bash
#SBATCH -J vasp
#SBATCH -N 1
#SBATCH --ntasks-per-node=64
#SBATCH -p sdicnormal

module purge
module load compiler/intel/2017.5.239       mpi/intelmpi/2017.4.239
export PATH=~/apprepo/vasp/5.4.4-intelmpi2017_optcell/app/bin:$PATH
source /public/home/jsyadmin/L4/wangyp/miniconda3/bin/activate qe-aiagent
export MKL_DEBUG_CPU_TYPE=5 #加速代码
export MKL_CBWR=AVX2 #使cpu默认支持avx2
export I_MPI_PIN_DOMAIN=numa #内存位置与cpu位置绑定，加速内存读取。对于内存带宽要求高的计算提速明显

WORK_DIR=./
main="/public/home/jsyadmin/L4/wangyp/vasp/benchmark/vasp-workflow/main.py"

# 结构优化
python $main -i $WORK_DIR -p pre -t relax
python $main -i $WORK_DIR -p run -t relax
python $main -i $WORK_DIR -p post -t relax
echo "Relax is done!"

# 自洽计算
python $main -i $WORK_DIR -p pre -t scf 
python $main -i $WORK_DIR -p run -t scf
python $main -i $WORK_DIR -p post -t scf
echo "Scf is done!"

# 计算态密度
python $main -i $WORK_DIR -p pre -t dos
python $main -i $WORK_DIR -p run -t dos
python $main -i $WORK_DIR -p post -t dos
echo "Dos is done!"

# 计算PBE能带
python $main -i $WORK_DIR -p pre -t PBE_band 
python $main -i $WORK_DIR -p run -t PBE_band
python $main -i $WORK_DIR -p post -t PBE_band
echo "PBE_band is done!"

# 计算弹性模量
python $main -i $WORK_DIR -p pre -t elastic 
python $main -i $WORK_DIR -p run -t elastic
python $main -i $WORK_DIR -p post -t elastic
echo "Elastic is done!"

# 计算吸收光谱
python $main -i $WORK_DIR -p pre -t absorption
python $main -i $WORK_DIR -p run -t absorption
python $main -i $WORK_DIR -p post -t absorption
echo "Elastic is done!"

#计算bader电荷
python $main -i $WORK_DIR -p pre bader
python $main -i $WORK_DIR -p run bader
python $main -i $WORK_DIR -p post bader
#计算phonon
python $main -i $WORK_DIR -p pre -t phonon
python $main -i $WORK_DIR -p run -t phonon
python $main -i $WORK_DIR -p post -t phonon