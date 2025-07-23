# README

本脚本是利用vaspkit实现结构优化、自洽计算、态密度计算、PBE的能带计算，声子谱计算磁矩计算，弹性性质计算（弹性模量，泊松比，剪切模量，吸收光谱，**需要提供一个工作路径，工作路径下面一定得有一个叫`POSCAR`的文件。**

## 注意

1. **本脚本是强烈依赖工作路径下面的文件夹就行判断是否要依赖前一步的结果做后续计算的，因此请不要随意更改文件夹的名字。**
2. **如果要删除文件夹里面的文件，如要删除scf文件夹里面的文件，请一定不要删除vasp的INCAR，POSCAR，POTCAR，KPOINTS文件。如果要删除，请删除整个scf文件夹，否则会持续不断的报错。**
3. **本脚本只能处理一个POSCAR文件，如果用户重新上传一个新的POSCAR，请重新使用一个新的路径进行计算，否则会出现严重的后果。**
4. **在计算弹性性质的时候，需要打开`~/.vaspkit`里面的`AUTO_PLOT`设置为`.TRUE.`，我做后处理里面设置了自动添加为`TRUE`，并且后处理完成后再设置为`FALSE`。在计算其他性质的时候遇到了，vaspkit的报错，可以检查这个文件里面的`AUTO_PLOT`是否为`FALSE`。只有计算弹性性质的时候，需要设置为`TRUE`，其余的时候必须设置为`FALSE`。**

## 依赖

```shell
requirements
   - vasp-5.4.4
   - vaspkit-1.5.1(需配置好赝势路径)
   - bader-1.0.5
   - vtstscripts-1033
   - python
   - pymatgen
   - ase 
   - matplotlib
   - numpy
   - phonopy
   - pandas
```

## 函数说明

```shell
-i work_path：指定工作路径。例如：-i /public/home/huangah/work

--pre_xxx name ：生成输入文件。例如：--pre_relax relax

--run_vasp name ：运行vasp，在执行pre_xxx函数之后，run_vasp函数之前需要提示用户修改或者查看4个输入文件。例如：--run_vasp relax

--post_vasp name ：检查vasp是否运行成功，是否收敛，如果不成功直接报错，不收敛也是直接报错。 --post_vasp relax
```

## 计算链路

以下是计算链接，推荐按照这个路径走，如果不想按照这个路径走，走每条路径的子树也是可以的。

比如想做能带计算，就可以走下面几条路径：

1. 结构优化->自洽->能带
2. 自洽->能带
3. 能带

```shell
目标     链路

结构优化：结构优化

自洽：结构优化->自洽

态密度：结构优化->自洽->态密度

能带：结构优化->自洽->能带

声子谱：结构优化->声子谱

磁矩：结构优化->自洽（磁矩）

弹性常数：结构优化->弹性常数

吸收光谱：结构优化->吸收光谱

bader电荷：结构优化->bader电荷
```

## 示例

```shell
# 结构优化
python main.py -i $WORK_DIR --pre_relax relax
python main.py -i $WORK_DIR --run_vasp relax
python main.py -i $WORK_DIR --post_vasp relax

# 重新进行优化
python main.py -i $WORK_DIR --pre_re_relax relax
python main.py -i $WORK_DIR --run_vasp relax
python main.py -i $WORK_DIR --post_vasp relax

# 自洽计算
python main.py -i $WORK_DIR --pre_scf scf
python main.py -i $WORK_DIR --run_vasp scf
python main.py -i $WORK_DIR --post_vasp scf

# 计算态密度
python main.py -i $WORK_DIR --pre_dos dos
python main.py -i $WORK_DIR --run_vasp dos
python main.py -i $WORK_DIR --post_vasp dos

# 计算PBE能带
python main.py -i $WORK_DIR --pre_PBE_band PBE_band
python main.py -i $WORK_DIR --run_vasp PBE_band
python main.py -i $WORK_DIR --post_vasp PBE_band

# 计算声子
python main.py -i $WORK_DIR --pre_phonon phonon
python main.py -i $WORK_DIR --run_vasp phonon
python main.py -i $WORK_DIR --post_vasp phonon

# 计算磁矩
python main.py -i $WORK_DIR --pre_magnetic magnetic
python main.py -i $WORK_DIR --run_vasp magnetic
python main.py -i $WORK_DIR --post_vasp magnetic

# 计算弹性性质
python main.py -i $WORK_DIR --pre_elastic elastic
python main.py -i $WORK_DIR --run_vasp elastic
python main.py -i $WORK_DIR --post_vasp elastic

# 计算吸收光谱
python main.py -i $WORK_DIR --pre_absorption absorption
python main.py -i $WORK_DIR --run_vasp absorption
python main.py -i $WORK_DIR --post_vasp absorption

# 计算bader电荷
python main.py -i $WORK_DIR --pre_bader bader
python main.py -i $WORK_DIR --run_vasp bader
python main.py -i $WORK_DIR --post_vasp bader
```
