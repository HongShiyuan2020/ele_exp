import cv2 as cv
import os
import random

def read_locations(file_path: str):
    config = dict()
    with open(file_path, "r", encoding="utf-8") as fin:
        tmp_lines = fin.readlines()
        tmp_key = None
        for line in tmp_lines:
            line = line.strip()
            if line:
                if line.endswith(":"):
                    config[line[:-1]] = []
                    tmp_key = line[:-1]
                else:
                    config[tmp_key] += line.split(" ")

    return config


def get_sec(loc: str):
    return int(loc[-2:]) + int(loc[-5:-3])*60 + int(loc[:2])*3600

def get_frames(loc_path: str, video_dir: str, save_dir: str, sample_radius: float):
    localtions = read_locations(loc_path)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for name in localtions:
        cap = cv.VideoCapture( os.path.join(video_dir, f"{name}.mp4"))
        fps = cap.get(cv.CAP_PROP_FPS)

        if cap.isOpened():
            for loc in localtions[name]:
                sec = get_sec(loc)
                sec += random.randint(-sample_radius, sample_radius)
                cap.set(cv.CAP_PROP_POS_FRAMES, int(sec*fps))
                ret, frame = cap.read()
                if not ret:
                    continue
                cv.imwrite(os.path.join(save_dir, f"{name}-{sec:07d}.jpg"), frame)

            cap.release()

import argparse

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loc-path", type=str, default="record.txt")
    parser.add_argument("--video-dir", type=str)
    parser.add_argument("--save-dir", type=str)
    parser.add_argument("--sample-radius", type=int)

    return parser.parse_args()

if __name__ == "__main__":
    get_frames(**vars(parse_arg()))