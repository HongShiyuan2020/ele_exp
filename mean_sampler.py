import cv2 as cv
import os
import random

def get_sec(loc: str):
    return int(loc[-2:]) + int(loc[-5:-3])*60 + int(loc[:2])*3600

def get_frames(video_path: str, save_dir: str):

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    cap = cv.VideoCapture(os.path.join(video_path))
    fps = cap.get(cv.CAP_PROP_FPS)
    frame_cnt = cap.get(cv.CAP_PROP_FRAME_COUNT)

    if cap.isOpened():
        for fc in range(0, int(frame_cnt), int(fps*3)):
            cap.set(cv.CAP_PROP_POS_FRAMES, fc)
            ret, frame = cap.read()
            if not ret:
                continue
            cv.imwrite(os.path.join(save_dir, f"{video_path[video_path.rfind('/')+1:video_path.rfind('.')]}-{fc}.jpg"), frame)

        cap.release()


if __name__ == "__main__":
    get_frames("labeling-data/record_03/01_20250319_163025.mp4", "labeling-data/03_01")