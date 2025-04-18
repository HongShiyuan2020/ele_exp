# coding:utf-8

from flask import Flask, request, stream_with_context, Response
from utility2_stream import ChatProcess, APIGetException
from utility3 import get_all_dets, filter_dets, sr_det, det_zero_adjust
import json
import os
import numpy as np
import base64
import cv2
import time

SERVER_DIR = os.path.dirname(__file__)

app = Flask(__name__, static_url_path="/sum_page", static_folder=os.path.join(SERVER_DIR, "sum_pages"))

file_path = os.path.join(SERVER_DIR, '1_config.json')
with open(file_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

process_map = dict()
# process_map = {
    # "192.168.4.13": ChatProcess(config)
# }
# process_map["192.168.4.13"].setCurrentStep(9)

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


@app.get("/register")
def register_videoip():
    args = request.args
    video_ip = args.get("video_ip")
    if video_ip in process_map:
        process_map[video_ip].init_state()
        return {
            "type": "REGISTER_OK"
        }
    else:
        process_map[video_ip] = ChatProcess(config)
        return {
            "type": "REGISTER_OK"
        }

@app.get("/stream/ciget")
def stream_ciget():
    video_ip = request.args.get("video_ip")
    return Response(stream_with_context(process_map[video_ip].streamOtherTip()), content_type="text/plain")
        
    
@app.get("/stream/ciok")
def stream_ciok():
    video_ip = request.args.get("video_ip")
    return Response(stream_with_context(process_map[video_ip].streamOtherOK()), content_type="text/plain")

@app.get("/stream/cierr")
def stream_cierr():
    video_ip = request.args.get("video_ip")    
    return Response(stream_with_context(process_map[video_ip].streamOtherErr()), content_type="text/plain")

@app.get("/stream/qget")
def stream_qget():
    video_ip = request.args.get("video_ip")
    return Response(stream_with_context(process_map[video_ip].streamGetQuestion()), content_type="text/plain")
    
@app.get("/stream/qok")
def stream_qok():
    video_ip = request.args.get("video_ip")
    return Response(stream_with_context(process_map[video_ip].streamGetQuesOK()), content_type="text/plain")

@app.get("/stream/qretry")
def stream_qretry():
    video_ip = request.args.get("video_ip")
    return Response(stream_with_context(process_map[video_ip].streamGetQuesRetry()), content_type="text/plain")

@app.get("/stream/qerr")
def stream_qerr():
    video_ip = request.args.get("video_ip")
    return Response(stream_with_context(process_map[video_ip].streamGetQuesEr()), content_type="text/plain")

@app.post("/uploadimg")
def upload_img():
    data = request.get_json()
    video_ip = data["video_ip"]
    process_map[video_ip].processUIRImg(data)
    return {"type": "UPLOAD_OK"}
 
@app.post("/frame")
def get_dets():
    
    time.sleep(0.2)
    
    try:
        req_in = request.get_json()
        process = process_map[req_in["video_ip"]]
        img = req_in["img"]
        w, h, c = req_in["w"], req_in["h"], req_in["c"]
        
        img_b64 = base64.b64decode(img)
        nparr = np.frombuffer(img_b64, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        cubes, coms = get_all_dets(img, 0)
        new_coms, new_binds, new_slides, new_cubes = filter_dets(cubes, coms)
        ss, tr, tl, uc = sr_det(new_coms, new_binds, new_slides, new_cubes)
        
        if not process.zero_ajust:
            process.zero_ajust = det_zero_adjust(coms)
        
        
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
            },
            "srs": {
                "ss": ss.tolist(),
                "tr": tr.tolist(),
                "tl": tl.tolist(),
                "uc": uc.tolist()
            }
        }
    except:
        return {
            "coms": {
                "xyxy": [],
                "cls": [],
                "name": []
            },
            "cubes": {
                "xyxy": [],
                "cls": [],
                "parent": []
            },
            "srs": {
                "ss": [0.0, 0.0],
                "tr": [0.0, 0.0],
                "tl": [0.0, 0.0],
                "uc": [0.0, 0.0]
            }
        }
    

'''
: 和大模型的对接接口
'''
@app.post("/chat")
def get_chat():
    req_in      = request.get_json()
    video_ip    = req_in.get("video_ip", "none")
    if not isinstance(req_in, dict) or "answer" not in req_in:
        req_in  = None
    comment     = process_map[video_ip].next(req_in)
    print(comment)
    return comment

if __name__ == "__main__":
    app.run("0.0.0.0", 8000)

