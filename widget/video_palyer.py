'''
视频播放组件显示检测结果
'''

import sys
import cv2
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import requests 
import base64
import time

import numpy as np
import random
import os

FRAME_URL = "http://127.0.0.1:8000/frame"

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

def plot_dets(img, cubes, coms, srs):
    img = img.copy()
    H, W, C = img.shape
    
    cubes_lines = dict()
    for cls, xyxy in zip(cubes["cls"], cubes["xyxy"]):
        if int(cls) in cubes_lines:
            cubes_lines[int(cls)].append(xyxy)
            txty = cubes_lines[int(cls)][0]
            img = cv2.line(img, [int((xyxy[0]+xyxy[2])/2*W), int((xyxy[1]+xyxy[3])/2*H)], 
                     [int((txty[0]+txty[2])/2*W), int((txty[1]+txty[3])/2*H)], 
                     (0, 255, 0), 6)
        else:
            cubes_lines[int(cls)] = []
            cubes_lines[int(cls)].append(xyxy)
            
    for [tx, ty, bx, by], name, idx in zip(coms["xyxy"], coms["name"], coms["cls"]):
        img = cv2.rectangle(img, [int(tx*W), int(ty*H)], [int(bx*W), int(by*H)], coms_c[int(idx)], 6)
        img = cv2.putText(img, f"{name}", [int(tx*W), int(ty*H)-20], cv2.FONT_HERSHEY_SIMPLEX, 2, coms_c[int(idx)], 6)
    for [tx, ty, bx, by], idx in  zip(cubes["xyxy"], cubes["cls"]):
        img = cv2.rectangle(img, [int(tx*W), int(ty*H)], [int(bx*W), int(by*H)], cubes_c[int(idx)], 6)
        img = cv2.putText(img, f"{int(idx)}", [int(tx*W), int(ty*H)-20], cv2.FONT_HERSHEY_SIMPLEX, 2, cubes_c[int(idx)], 6)
    
    ss, tr, tl, uc = srs["ss"], srs["tr"], srs["tl"], srs["uc"]
    img = cv2.line(img, [int(ss[0]*W), int(ss[1]*H)], [int(tr[0]*W), int(tr[1]*H)], (255, 225, 0), 6)
    img = cv2.line(img, [int(ss[0]*W), int(ss[1]*H)], [int(tl[0]*W), int(tl[1]*H)], (255, 255, 0), 6)
    img = cv2.line(img, [int(ss[0]*W), int(ss[1]*H)], [int(uc[0]*W), int(uc[1]*H)], (0, 0, 255), 6)
    
    return img

class DetThread(QThread):
    det_chageed = pyqtSignal(dict, dict, object, dict)
    
    def __init__(self, parent = None):
        super(DetThread, self).__init__(parent)
        self.session = requests.Session()
        self.new_coms = {"xyxy": [], "cls": [], "name": []}
        self.new_cubes = {"xyxy": [], "cls": []}
        self.srs = {"ss": [0.0, 0.0], "tr": [0.0, 0.0], "tl": [0.0, 0.0], "uc": [0.0, 0.0]}
        self.flag = True
        self.frame = None
        self.frame_flag = False
                
    def run(self):
        while self.flag:
            if self.frame_flag:
                try:
                    self.new_coms, self.new_cubes, self.srs = self.post_det(self.frame)
                except:
                    self.new_coms = {"xyxy": [], "cls": [], "name": []}
                    self.new_cubes = {"xyxy": [], "cls": []}
                    self.srs = {"ss": [0.0, 0.0], "tr": [0.0, 0.0], "tl": [0.0, 0.0], "uc": [0.0, 0.0]}
            else:
                self.msleep(500)
            self.det_chageed.emit(self.new_coms, self.new_cubes, self, self.srs)    
                
    def post_det(self, frame: np.ndarray):
        fs = cv2.resize(frame, [1600, 928])
        h, w, c = fs.shape
        b64 = base64.b64encode(fs.tobytes()).decode("utf-8")
        res = self.session.post(FRAME_URL, json={"img": b64, "w": w, "h": h, "c": c}, headers={"Content-Type": "application/json"})
        res = res.json()
        return res["coms"], res["cubes"], res["srs"]             

class VideoCaptureThread(QThread):
    frame_chageed = pyqtSignal(np.ndarray, QPixmap)

    def __init__(self, parent = None, url=""):
        super(VideoCaptureThread, self).__init__(parent)
        self.parent = parent
        self.flag = True
        self.url  = url
        self.w_width  = 1100
        self.w_height = 620
        self.pause = True
        self.once = False
        self.skip = 20
        self.idx = 0
        self.cuframe = None
        self.session = requests.Session()
        self.new_coms = {"xyxy": [], "cls": [], "name": []}
        self.new_cubes = {"xyxy": [], "cls": []}
        self.srs = {"ss": [0.0, 0.0], "tr": [0.0, 0.0], "tl": [0.0, 0.0], "uc": [0.0, 0.0]}

    def run(self):
        self.cap = cv2.VideoCapture(self.url)
        if not self.cap.isOpened():
            print("Error: Could not open video.")
            exit(-1)
        
        while self.flag:
            if self.pause:
                self.update_frame()
            self.msleep(1)
        
        if self.cap:
            self.cap.release()
        
    def update_det(self, coms, cubes, det, srs):
        self.new_coms = coms
        self.new_cubes = cubes
        self.srs = srs
        if self.idx != 0:
            det.frame = self.cuframe
            det.frame_flag = True
    
    def update_frame(self):
        ret, frame = self.cap.read()

        if ret:
            self.cuframe = frame
            frame_plot = plot_dets(frame, self.new_cubes, self.new_coms, self.srs)
            frame_rgb = cv2.cvtColor(frame_plot, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, [self.w_width, self.w_height])
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(q_img)
            
            self.frame_chageed.emit(frame, pix)
            self.idx += 1

    
    def pause_toggle(self):
        self.pause = not self.pause

    def post_det(self, frame: np.ndarray):
        fs = cv2.resize(frame, [1600, 928])
        h, w, c = fs.shape
        b64 = base64.b64encode(fs.tobytes()).decode("utf-8")
        res = self.session.post(FRAME_URL, json={"img": b64, "w": w, "h": h, "c": c}, headers={"Content-Type": "application/json"})
        res = res.json()
        return res["coms"], res["cubes"]        


class VideoPlayer(QWidget):
    def __init__(self, url: str):
        super().__init__()

        # State
        self.video_thread = None
        self.det_thread = None
        self.cur_frame = None
        self.setContentsMargins(0, 0, 0, 0)
        # 创建标签用于显示视频帧
        self.frame_label = QLabel(self)
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setText("Frame will appear here")

        # 创建布局
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.frame_label)

        # 创建主窗口的中心部件
        self.setLayout(layout)
        self.w_width  = 1100
        self.w_height = 620

        self.setStyleSheet("""
            QWidget {
                background-color: #777777;
            }
            QLabel {
                background-color: #000000;
            }
        """)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # 将 OpenCV 帧转换为 QImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.cur_frame = frame_rgb.copy()
            frame_rgb = cv2.resize(frame_rgb, [self.w_width, self.w_height])
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_label.setPixmap(QPixmap.fromImage(q_img))

    def update_frame_slot(self, curimg, pix):
        self.cur_frame = curimg.copy()
        self.frame_label.setPixmap(pix)


    def set_input(self, url: str):
        self.video_thread = VideoCaptureThread(self, url)
        self.video_thread.frame_chageed.connect(self.update_frame_slot)
        self.video_thread.start()
        
        self.det_thread = DetThread(self)
        self.det_thread.det_chageed.connect(self.video_thread.update_det)
        self.det_thread.start()        

    def stop_stream(self):
        self.video_thread.flag = False

    def get_curframe(self):
        frame = cv2.resize(self.cur_frame, [1600, 928])
        return frame

    def closeEvent(self, event):
        self.stop_stream()
        event.accept()
        
    def pause_toggle(self):
        self.video_thread.pause_toggle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer("rtsp://admin:@192.168.4.13")
    player.show()
    sys.exit(app.exec_())