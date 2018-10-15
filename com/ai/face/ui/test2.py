from face_collect import Collect
import os
from compare import Compare
import numpy as np

current_path = os.getcwd()  # 获取当前路径
collect = Collect()
compare = Compare()
_128descriptor_1 = collect.collect(current_path + "\\faces\\153801937511.jpg")
# _128descriptor_1_list = _128descriptor_1.split(",")
# _128descriptor_1_list = [float(i) for i in _128descriptor_1_list]
nd1 = np.array(_128descriptor_1)
# for i, num in enumerate(_128descriptor_1_list):
#     nd1 = np.append(nd1, num)

print(nd1)
_128descriptor_2 = collect.collect(current_path + "\\faces\\u=943953645,848572230&fm=200&gp=0.jpg")
# _128descriptor_2_list = _128descriptor_2.split(",")
# _128descriptor_2_list = [float(i) for i in _128descriptor_2_list]
nd2 = np.array(_128descriptor_2)
# for i, num in enumerate(_128descriptor_2_list):
#     nd2 = np.append(nd2, num)
print(nd2)
compare.compare(nd1, nd2)