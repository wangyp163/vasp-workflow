from . import * # 从 task/__init__.py 添加基础模块

def get_magnetic_moments(oszicar_path="OSZICAR"):
    mag_step = []
    mag_reult = []
    count = 1
    with open(oszicar_path, "r") as f:
        for each in f.readlines():
            if "mag" in each:
                mag_step.append(count)
                mag_reult.append(each[each.find("mag"):])
                count += 1

    if not mag_step:
        warnings.warn("未找到磁矩数据。请确认计算是否包含自旋极化。")
        return

    print("magnetization:")
    with open("magnetic.log", "w") as f:
        f.write("magnetization:\n")
        for index in range(len(mag_step)):
            data = "step{} : {}".format(mag_step[index], mag_reult[index].strip())
            f.write(data + "\n")
            print(data)
        data_final = "final : {}".format(mag_reult[-1])
        f.write("\n")
        f.write(data_final)
        print()
        print(data_final)

def pre_magnetic(work_path):
    return pre_scf(work_path)
