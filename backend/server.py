# coding:utf-8
from flask import Flask, request, stream_with_context, Response
from utility2 import ChatProcess, APIGetException
from utility3 import get_all_dets, filter_dets
import json
import os
import time
import numpy as np
import base64
import cv2

app = Flask(__name__)

SERVER_DIR = os.path.dirname(__file__)
file_path = os.path.join(SERVER_DIR, '1_config.json')
with open(file_path, 'r', encoding='utf-8') as file:
    config = json.load(file)
process = ChatProcess(config)
# process.setCurrentStep(9)

'''
'''

@app.errorhandler(500)
def handle_500_err(e):
    return {
        "type": "API_ER",
        "reply": "服务器内部错误"
    }

@app.errorhandler(APIGetException)
def handle_apierror(e):
    return {
        "type": "API_ER",
        "reply": "大模型API调用失败"
    }

@app.get("/stream")
def get_cube_loc():
    return Response(stream_with_context(process.nextStream()), content_type="text/plain")
    
@app.post("/frame")
def get_dets():
    req_in = request.get_json()
    img = req_in["img"]
    w, h, c = req_in["w"], req_in["h"], req_in["c"]
    img = np.frombuffer(base64.b64decode(img), dtype=np.uint8).reshape(h, w, c)
    cubes, coms = get_all_dets(img)
    new_coms, new_binds, new_slides, new_cubes = filter_dets(cubes, coms)

    return {
        "coms": {
            "xyxy": coms["xyxy"].tolist(),
            "cls": coms["cls"].tolist(),
            "name": coms["name"]
        },
        "cubes": {
            "xyxy": new_cubes["xyxy"].tolist(),
            "cls": new_cubes["cls"].tolist(),
            "parent": new_cubes["parent"].tolist()
        }
    }


'''
: 和大模型的对接接口
'''
@app.post("/chat")
def get_chat():
    req_in = request.get_json()
    if not isinstance(req_in, dict) or "answer" not in req_in:
        req_in = None

    comment = process.next(req_in)
    print(comment)
    time.sleep(0.4)

    return comment

if __name__ == "__main__":
    app.run("0.0.0.0", 8000)

