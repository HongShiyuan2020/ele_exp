idx_map = [
    5, 9, 8, 3, 2, 6, 7, 1, 4, 1
] # [6, 40] {1, 2, 3}

idx_map1 = [
    4, 5, 8, 9, 1, 7, 3, 2, 6, 1
] # [4, 5]

idx_map2 = [
    8, 1, 3, 5, 2, 7, 9, 6, 4, 1
] # [41, 160]

idx_map3 = [
    5, 8, 1, 6, 3, 4, 2, 9, 7, 1
] # [161, 235]

import os

def re_idx(labels_dir: str, map: list, f_idx: list):
    f_names = os.listdir(labels_dir)
    f_names.sort()
    for idx, f_name in enumerate(f_names):
        data = []
        lines = []
        with open(os.path.join(labels_dir, f_name), "r", encoding="utf-8") as fin:
            lines = fin.readlines()
        
        for line in lines:
            if line != "\n":
                data.append(f"{str(map[f_idx[idx]][int(line[0])])}{line[1:]}")
        print(idx)
        print(f_name)

        with open(os.path.join(labels_dir, f_name), "w", encoding="utf-8") as fout:
            fout.writelines(data)


idx_xre = [0] * 235
for i in range(235):
    if i <= 2 or (i >= 5 and i <= 39):
        idx_xre[i] = 0
    if i >= 3 and i <= 4:
        idx_xre[i] = 1
    if i >= 40 and i <= 159:
        idx_xre[i] = 2
    if i >= 160 and i <= 234:
        idx_xre[i] = 3

re_idx("/home/hongsy/Downloads/LabelImg/labels", [
    idx_map, idx_map1, idx_map2, idx_map3
], idx_xre)