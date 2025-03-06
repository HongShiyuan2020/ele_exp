import os
import sys
from pathlib import Path
import numpy as np
import torch
import random

from concurrent.futures import ThreadPoolExecutor, as_completed

executor = ThreadPoolExecutor(max_workers=2)

FILE = Path(__file__).resolve()
ROOT = Path(FILE.parents[0].parent, "model/yolov5") 
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  
    sys.path.append(str(ROOT.parent.parent))

PRO_DIR = str(ROOT.parent.parent)
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  


from ultralytics.utils.plotting import Annotator, colors
from model.yolov5.models.common import DetectMultiBackend
from model.yolov5.utils.general import (
    check_img_size,
    cv2,
    non_max_suppression,
    scale_boxes,
)
from model.yolov5.utils.augmentations import (
    letterbox
)
from model.yolov5.utils.torch_utils import select_device
from ultralytics import YOLO


'''
初始化模型
'''
device = select_device("")
com_model = DetectMultiBackend("ckpt/yolov5s_component_.pt", 
                           device=device, 
                           dnn=False, 
                           data=ROOT / "data/coco128.yaml", 
                           fp16=False)
stride, names, pt = com_model.stride, com_model.names, com_model.pt
imgsz = check_img_size((640, 384), s=stride)  
bs = 1 
com_model.warmup(imgsz=(1 if pt or com_model.triton else bs, 3, *imgsz))
cube_model = YOLO(os.path.join(PRO_DIR, "ckpt/yolov8s_3000.pt"))

'''
V8与V5的检测调用接口
'''
def det_v8_img(im: np.ndarray, model, det_type="CUBE"):
    res = model.predict(im, imgsz=1600, iou=0.5, verbose=False)
    res_ans = res[0]
    data = {
        "xyxy": res_ans.boxes.xyxyn.detach().cpu().numpy(),
        "cls": res_ans.boxes.cls.detach().cpu().numpy(),
        "conf": res_ans.boxes.conf.detach().cpu().numpy()
    }
    return det_type, data

def det_one_img (
    im: np.ndarray,
    model=com_model,
    det_type="COMS",
    conf_thres=0.25,    # confidence threshold
    iou_thres=0.5,     # NMS IOU threshold
    max_det=1000,       # maximum detections per image
    classes=None,       # filter by class: --class 0, or --class 0 2 3
    agnostic_nms=True, # class-agnostic NMS
    augment=False,      # augmented inference
    visualize=False,    # visualize features
    line_thickness=3,   # bounding box thickness (pixels)
    hide_labels=False,  # hide labels
    hide_conf=False,    # hide confidences
):
    im0 = im
    im = letterbox(im, 640, stride=32, auto=True)[0]
    im = im.transpose((2, 0, 1))[::-1]
    im = np.ascontiguousarray(im)
    im = torch.from_numpy(im).to(model.device)
    im = im.half() if model.fp16 else im.float() 
    im /= 255
    if len(im.shape) == 3:
        im = im[None]

    pred = model(im, augment=augment, visualize=visualize)
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    
    res = {
        "xyxy": [],
        "conf": [],
        "cls": [],
        "name": []
    }    

    for i, det in enumerate(pred):
        if len(det):
            det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()
            for *xyxy, conf, cls in reversed(det):
                tx, ty, bx, by = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                res["xyxy"].append([tx/im0.shape[1], ty/im0.shape[0], bx/im0.shape[1], by/im0.shape[0]])
                res["cls"].append(int(cls))
                res["conf"].append(float(conf))
                res["name"].append(names[int(cls)])
    
    res["xyxy"] = np.array(res["xyxy"], dtype=np.float64)
    res["conf"] = np.array(res ["conf"], dtype=np.float64)
    res["cls"] = np.array(res["cls"])

    return det_type, res

com_idx_set = {
    4, 5, 2, 0, 6, 3, 1
}
OK_AREA = [0.5, 0.0, 1.0, 0.5]
SR_WIDS = {13, 8, 3}
BIND_IDX_SET = {
    7, 8
}
SLIDE_ID = 9

'''
选择电路元器件(电压表、电源...)
'''
def select_coms(res: list):
    coms = []
    for cls, xyxy, name, conf in zip(res["cls"], res["xyxy"], res["name"], res["conf"]):
        if int(cls) in com_idx_set:
            coms.append({
                "cls": cls,
                "xyxy": xyxy,
                "name": name,
                "conf": conf
            })
    return coms


def a_rate(xyxy):
    tx, ty, bx, by = xyxy
    com_s = abs(bx-tx)*abs(ty-by)
    xmin = max(tx, OK_AREA[0])
    ymin = max(ty, OK_AREA[1])
    xmax = min(bx, OK_AREA[2])
    ymax = min(by, OK_AREA[3])
    over_s = (ymax-ymin)*(xmax-xmin)
    if ymax-ymin < 0 or xmax-xmin < 0:
        over_s = 0
    rate_s = over_s/com_s
    
    return rate_s

'''
判断是否整理完成
'''
def tidy_up_ok(coms, cubes=None):
    ready_coms = []
    no_ready_coms = []
    ready_cubes = []
    no_ready_cubes = []
    
    for com in coms:
        rate_s = a_rate(com["xyxy"])
        if rate_s > 0.5:
            ready_coms.append(com)
        else:
            no_ready_coms.append(com)
    
    for cube in cubes:
        rate_s = a_rate(cube)
        if rate_s > 0.5:
            ready_cubes.append(cube)
        else:
            no_ready_cubes.append(cube)
    
    return len(no_ready_coms) == 0 and len(no_ready_cubes) == 0, ready_coms, no_ready_coms, ready_cubes, no_ready_cubes

'''
整理代码对外接口
'''
def tidy_det(img):
    im0, res = det_one_img(img, com_model)
    res_cube = cube_model.predict(img, imgsz=1600, iou=0.4, verbose=False)
    res_cube = res_cube[0].boxes.xyxyn.detach().cpu().tolist()
    isok, coms , _, cs, ncs  = tidy_up_ok(select_coms(res), res_cube)
    
    return isok

def compute_iou_matrix(boxes1: np.ndarray, boxes2: np.ndarray) -> np.ndarray:
    """
    计算两个检测框集合之间的 IOU 矩阵。

    :param boxes1: (N, 4) 形状的 ndarray, 其中每行是 [left, top, right, bottom]
    :param boxes2: (M, 4) 形状的 ndarray, 其中每行是 [left, top, right, bottom]
    :return: (N, M) 形状的 IOU 矩阵
    """
    if len(boxes1) == 0 or len(boxes2) == 0:
        return np.array([])
    N = boxes1.shape[0]
    M = boxes2.shape[0]
    
    # 计算交集框的坐标
    inter_left = np.maximum(boxes1[:, None, 0], boxes2[None, :, 0])
    inter_top = np.maximum(boxes1[:, None, 1], boxes2[None, :, 1])
    inter_right = np.minimum(boxes1[:, None, 2], boxes2[None, :, 2])
    inter_bottom = np.minimum(boxes1[:, None, 3], boxes2[None, :, 3])
    
    # 计算交集区域
    inter_width = np.clip(inter_right - inter_left, 0, None)
    inter_height = np.clip(inter_bottom - inter_top, 0, None)
    inter_area = inter_width * inter_height
    
    # 计算各自的面积
    area1 = (boxes1[:, 2] - boxes1[:, 0]) * (boxes1[:, 3] - boxes1[:, 1])
    area2 = (boxes2[:, 2] - boxes2[:, 0]) * (boxes2[:, 3] - boxes2[:, 1])
    
    # 计算并集面积
    union_area = area1[:, None] + area2[None, :] - inter_area
    
    # 计算 IOU
    iou_matrix = inter_area / np.clip(union_area, 1e-6, None)  # 避免除零错误
    
    return iou_matrix




 
def get_all_dets(img: np.ndarray):
    '''
    获取所有cubes和coms的检测结果
    '''
    tasks = []
    tasks.append(executor.submit(det_one_img, img.copy(), com_model))
    tasks.append(executor.submit(det_v8_img, img.copy(), cube_model))

    res = dict()
    
    for future in as_completed(tasks):
        data = future.result()
        res[data[0]] = data
    
    return res["CUBE"][1], res["COMS"][1]





def rand_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)
cubes_c = []
coms_c = []
for i in range(30):
    cubes_c.append(rand_color())
    coms_c.append(rand_color())
def plot_dets(img, cubes, coms):
    img = img.copy()
    H, W, C = img.shape
    
            
    for [tx, ty, bx, by], name, idx in zip(coms["xyxy"], coms["name"], coms["cls"]):
        img = cv2.rectangle(img, [int(tx*W), int(ty*H)], [int(bx*W), int(by*H)], coms_c[int(idx)], 6)
        img = cv2.putText(img, f"{name}-{idx}", [int(tx*W), int(ty*H)-20], cv2.FONT_HERSHEY_SIMPLEX, 2, coms_c[int(idx)], 6)
    for [tx, ty, bx, by], idx in  zip(cubes["xyxy"], cubes["cls"]):
        img = cv2.rectangle(img, [int(tx*W), int(ty*H)], [int(bx*W), int(by*H)], cubes_c[int(idx)], 6)
        img = cv2.putText(img, f"{int(idx)}", [int(tx*W), int(ty*H)-20], cv2.FONT_HERSHEY_SIMPLEX, 2, cubes_c[int(idx)], 6)

    return img



def filter_dets(cubes, coms):
    '''
    过滤cubes和coms
    '''
    new_coms = {
        "xyxy": [],
        "cls": [],
        "conf": [],
        "name": []
    }    
    new_binds = {
        "xyxy": [],
        "cls": [],
        "conf": [],
        "name": [],
        "parent": []
    }
    new_slides = {
        "xyxy": [],
        "cls": [],
        "conf": [],
        "name": []
    }
    
    # 对coms进行分类
    for idx, [xyxy, cls, conf, name] in enumerate(zip(coms["xyxy"], coms["cls"], coms["conf"], coms["name"])):
        if int(cls) in com_idx_set:
            new_coms["xyxy"].append(xyxy)
            new_coms["cls"].append(int(cls))
            new_coms["conf"].append(conf)
            new_coms["name"].append(name)
            continue
        if int(cls) in BIND_IDX_SET:
            new_binds["xyxy"].append(xyxy)
            new_binds["cls"].append(int(cls))
            new_binds["conf"].append(conf)
            new_binds["name"].append(name)
            continue
        if int(cls) == SLIDE_ID:
            new_slides["xyxy"].append(xyxy)
            new_slides["cls"].append(int(cls))
            new_slides["conf"].append(conf)
            new_slides["name"].append(name)
    new_coms["xyxy"] = np.array(new_coms["xyxy"], dtype=np.float64)
    new_coms["conf"] = np.array(new_coms ["conf"], dtype=np.float64)
    new_coms["cls"] = np.array(new_coms["cls"])
    new_binds["xyxy"] = np.array(new_binds["xyxy"], dtype=np.float64)
    new_binds["conf"] = np.array(new_binds ["conf"], dtype=np.float64)
    new_binds["cls"] = np.array(new_binds["cls"])
    new_slides["xyxy"] = np.array(new_slides["xyxy"], dtype=np.float64)
    new_slides["conf"] = np.array(new_slides ["conf"], dtype=np.float64)
    new_slides["cls"] = np.array(new_slides["cls"])
    
    
    new_cubes = {
        "xyxy": [],
        "cls": [],
        "conf": [],
        "parent": []
    }
    
    # 过滤掉和com无交集的cude
    # 过滤掉重叠度过高的cube
    cube_pos, com_pos = cubes["xyxy"], new_coms["xyxy"]
    com_pos[:, 0] -= 0.005
    com_pos[:, 1] -= 0.005
    com_pos[:, 2] += 0.005
    com_pos[:, 3] += 0.005
    iou_comcube = compute_iou_matrix(cube_pos, com_pos)
    if len(iou_comcube) != 0:
        iou_comcube_maxarg = iou_comcube.argmax(axis=-1)
        iou_cc = compute_iou_matrix(cube_pos, cube_pos)
        iou_cc[range(len(iou_cc)), range(len(iou_cc))] = 0
        iou_cc_maxv = iou_cc.max(axis=-1)

        covered_cube = set()

        for idx, max_idx in enumerate(iou_comcube_maxarg):
            iou_rate = iou_comcube[idx][max_idx]
            if iou_rate < 1e-6:
                continue
            if iou_cc_maxv[idx] > 0.2:
                if idx in covered_cube:
                    continue
                else:
                    covered_cube.add(idx)
                    for over_idx, cc_rate in enumerate(iou_cc[idx]):
                        if cc_rate > 0.2:
                            covered_cube.add(over_idx)
                            
            new_cubes["cls"].append(cubes["cls"][idx])
            new_cubes["xyxy"].append(cubes["xyxy"][idx])
            new_cubes["conf"].append(cubes["conf"][idx])
            new_cubes["parent"].append(max_idx)
            
    new_cubes["cls"] = np.array(new_cubes["cls"])
    new_cubes["xyxy"] = np.array(new_cubes["xyxy"])
    new_cubes["conf"] = np.array(new_cubes["conf"])
    new_cubes["parent"] = np.array(new_cubes["parent"])
    
    return new_coms, new_binds, new_slides, new_cubes

def get_connes(new_coms, new_binds, new_slides, new_cubes, im):
    
    new_cubes["bind"] = []
    new_binds["parent"] = []
    
    # 获取bind所属的com
    iou_bindcoms = compute_iou_matrix(new_binds["xyxy"], new_coms["xyxy"])
    if len(iou_bindcoms) != 0:
        iou_bindcoms_arg = iou_bindcoms.argmax(axis=-1)
        new_binds["parent"] = np.array(iou_bindcoms_arg)


    # 获取对应的连接元组
    connestions = dict()
    iou_comcom = compute_iou_matrix(new_coms["xyxy"], new_coms["xyxy"])
    if len(iou_comcom) != 0:
        pass
    iou_bindcube = compute_iou_matrix(new_cubes["xyxy"], new_binds["xyxy"])
    if len(iou_bindcube) != 0:
        iou_bindcube_max = iou_bindcube.argmax(axis=-1)
        iou_bindcube_val = iou_bindcube.max(axis=-1)
        
        bind_cp = (new_binds["xyxy"][:, :2] + new_binds["xyxy"][:, 2:])/2 
        cube_cp = (new_cubes["xyxy"][:, :2] + new_cubes["xyxy"][:, 2:])/2

        cube_cp = cube_cp[:, None, :]
        bind_cp = bind_cp[None, :, :]
        
        dis = np.sqrt(((bind_cp - cube_cp)**2).sum(axis=-1))
        dis_min_val = dis.min(axis=-1)
        dis_min_arg = dis.argmin(axis=-1)
        
        for idx, [max_arg, max_val] in enumerate(zip(iou_bindcube_max, iou_bindcube_val)):
            k = int(new_cubes["cls"][idx])
            if k not in connestions:
                connestions[k] = []
            
            connestions[k].append([new_cubes["parent"][idx], new_coms["cls"][new_cubes["parent"][idx]]])
            
            if max_val < 1e-6:
                if len(connestions[k]) < 4:
                    if dis_min_val[idx] < 0.03:
                        connestions[k].append([dis_min_arg[idx], new_binds["cls"][dis_min_arg[idx]]])
                    else:
                        connestions[k].append([-1, -1])
            else:
                if len(connestions[k]) < 4:
                    connestions[k].append([max_arg, new_binds["cls"][max_arg]])
        
        new_connections = dict()
        for ck in connestions:
            if len(connestions[ck]) == 4:
                new_connections[ck] = connestions[ck]
        
    return new_coms, new_binds, new_cubes, new_slides, new_connections         



def get_conn_ans(coms, binds, connestions, cubes):
    '''
    获取最终结果
    '''

    coms_types = [0, 1, 1, 1, 1, 1, 0]
    com_to_idx = {
        "B": 0,
        "SO": 1,
        "SC": 2,
        "SR": 3,
        "R": 4,
        "A": 5,
        "V": 6
    }
    idx_to_com = ["B", "SO", "SC", "SR", "R", "A", "V"]
    
    cur_com = "B"
    cur_bp  = "pos"    
    dir_ect = "P"
    end_flag = False
    visited_b = False    
    visited_com = set()
        
    V_lines = dict()
    Visited_Lines = set()
    
    for conn in connestions:
        [com_f, com_ft], [bp_f, bp_ft], [com_t, com_tt], [bp_t, bp_tt] = connestions[conn]
        if com_ft == 6 or com_tt == 6:
            V_lines[conn] = connestions[conn]

    if len(V_lines) != 2:
        return False

    for vline in V_lines:
        del connestions[vline]

    while not end_flag:
        print(cur_com)
        if cur_com == "B":
            if visited_b:
                if sum(coms_types) != 1:
                    return False
                end_flag = True
                break
            visited_b = True
            for conn in connestions:
                if conn in Visited_Lines:
                    continue
                [com_f, com_ft], [bp_f, bp_ft], [com_t, com_tt], [bp_t, bp_tt] = connestions[conn]
                if com_ft == 0:
                    cur_com = idx_to_com[com_tt]
                    Visited_Lines.add(conn)
                    break
                elif com_tt == 0:
                    cur_com = idx_to_com[com_ft]
                    Visited_Lines.add(conn)
                    break
            continue
        else:
            if (coms_types[1] == 0 or coms_types[2] == 0) and (cur_com == "SO" or cur_com == "SC"):
                return False
            if coms_types[com_to_idx[cur_com]] == 0:
                return False
            for conn in connestions:
                if conn in Visited_Lines:
                    continue
                [com_f, com_ft], [bp_f, bp_ft], [com_t, com_tt], [bp_t, bp_tt] = connestions[conn]
                if com_ft == com_to_idx[cur_com]:
                    coms_types[com_to_idx[cur_com]] -= 1
                    cur_com = idx_to_com[com_tt]
                    Visited_Lines.add(conn)
                    break
                elif com_tt == com_to_idx[cur_com]:
                    coms_types[com_to_idx[cur_com]] -= 1
                    cur_com = idx_to_com[com_ft]
                    Visited_Lines.add(conn)
                    break
            continue
    
    others = []
    for conn in V_lines:
        [com_f, com_ft], [bp_f, bp_ft], [com_t, com_tt], [bp_t, bp_tt] = V_lines[conn]
        if com_ft == 6:
            others.append(com_tt)
        else:
            others.append(com_ft)
        
    if others[0] == 4 and others[1] == 4:
        return True
    
    return False

def conn_det(img: np.ndarray):
    cubes, coms = get_all_dets(img)
    new_coms, new_binds, new_slides, new_cubes  = filter_dets(cubes, coms)
    new_coms, new_binds, new_cubes, new_slides, connestions = get_connes(new_coms, new_binds, new_slides, new_cubes, img)
    res = get_conn_ans(new_coms, new_binds, connestions, new_cubes)        
    return res


def sr_det(new_coms, new_binds, new_slides, new_cubes):
    com_xyxy = []
    for idx, c in enumerate(new_coms["cls"]):
        if c == 3:
            com_xyxy = new_coms["xyxy"][idx]
            break
        
    if len(new_slides["xyxy"]) == 0 or len(com_xyxy) == 0 or len(new_cubes["xyxy"]) == 0 or len(new_binds["xyxy"]) == 0:
        return np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0])

    slide_xy = (new_slides["xyxy"][0][:2]+new_slides["xyxy"][0][2:])/2
    
    iou_bindscoms = compute_iou_matrix(com_xyxy[None, :], new_binds["xyxy"])[0]
    tr_bind = []
    tl_bind = []
    for idx, val in enumerate(iou_bindscoms):
        if val > 1e-6:
            if new_binds["cls"][idx] == 7:
                if len(tr_bind) == 0:
                    tr_bind = (new_binds["xyxy"][idx][:2] + new_binds["xyxy"][idx][2:])/2
                else:
                    cent = (new_binds["xyxy"][idx][:2] + new_binds["xyxy"][idx][2:])/2
                    dis  = np.sqrt(((cent - tr_bind)**2).sum()) 
                    if dis > 0.05:
                        tl_bind = cent
    
    if len(tl_bind) == 0 or len(tr_bind) == 0:
        return np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0])
    
    iou_cubecom = compute_iou_matrix(com_xyxy[None, :], new_cubes["xyxy"])
    iou_bindcube = compute_iou_matrix(new_cubes["xyxy"], new_binds["xyxy"])
    iou_bindcube_maxarg = iou_bindcube.argmax(axis=-1)
    iou_cubecom_maxarg = iou_cubecom.argmax()

    if iou_cubecom[0][iou_cubecom_maxarg] <= 1e-6:
        return np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0])

    under_cube = []
    for idx, c in enumerate(new_cubes["xyxy"]):
        if iou_cubecom[0][idx] > 1e-6:
            max_bind_idx = iou_bindcube_maxarg[idx]
            if iou_bindcube[idx][max_bind_idx] >= 1e-6: 
                if new_binds["cls"][max_bind_idx] == 8:
                    under_cube = new_binds["xyxy"][max_bind_idx]
                    break
    
    if len(under_cube) == 0:
        return np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0]), np.array([0.0, 0.0])


    under_cube = (under_cube[:2] + under_cube[2:])/2
    
    return slide_xy, tr_bind, tl_bind, under_cube

def sr_det_ans(slide_xy, tr_bind, tl_bind, under_cube):
    if (slide_xy + tr_bind + tl_bind + under_cube).sum() < 0.01:
        return True

    dis_ru = np.sqrt(((tr_bind-under_cube)**2).sum())
    dis_lu = np.sqrt(((tl_bind-under_cube)**2).sum())
    
    less_p = None
    grea_p = None
    
    if dis_lu < dis_ru:
        less_p = tl_bind
        grea_p = tr_bind
    else:
        less_p = tr_bind
        grea_p = tl_bind
        
    ans_rate = np.sqrt(((slide_xy - less_p)**2).sum()) / np.sqrt(((slide_xy - grea_p)**2).sum())
    return ans_rate > 1.6

def sr_det_ans_final(img):
    cubes, coms = get_all_dets(img)
    new_coms, new_binds, new_slides, new_cubes  = filter_dets(cubes, coms)
    ss, tr, tl, uc = sr_det(new_coms, new_binds, new_slides, new_cubes)
    return sr_det_ans(ss, tr, tl, uc)


if __name__ == "__main__":
    im = cv2.imread(r"labeling-data\02_0_20\images\01_20250121_11-00_00_23.jpg")
    cubes, coms = get_all_dets(im)
    new_coms, new_binds, new_slides, new_cubes  = filter_dets(cubes, coms)
    ss, tr, tl, uc = sr_det(new_coms, new_binds, new_slides, new_cubes)
    im0 = plot_dets(im, new_cubes, coms)
    H, W, C = im0.shape
    im0 = cv2.line(im0, [int(ss[0]*W), int(ss[1]*H)], [int(tr[0]*W), int(tr[1]*H)], (0, 225, 0), 3)
    im0 = cv2.line(im0, [int(ss[0]*W), int(ss[1]*H)], [int(tl[0]*W), int(tl[1]*H)], (255, 0, 0), 3)
    im0 = cv2.line(im0, [int(ss[0]*W), int(ss[1]*H)], [int(uc[0]*W), int(uc[1]*H)], (0, 0, 255), 3)
    im0 = cv2.resize(im0, [1280, 720])
    print(np.sqrt(((uc - ss)**2).sum()))
    cv2.imshow("TTT", im0)
    cv2.waitKey(0)