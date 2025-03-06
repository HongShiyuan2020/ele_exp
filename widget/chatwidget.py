import sys
from PyQt5 import QtNetwork
from PyQt5.QtCore import QTimer, Qt, QSize, QUrl, QByteArray
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtWidgets import QTextBrowser, QDialog, QAbstractItemView, QRadioButton, QButtonGroup, QListWidgetItem, QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSizePolicy, QFrame, QListWidget
from tools.jsontopdf import json_to_pdf

import sys
import os
import json
import base64
import numpy as np

import matplotlib.pyplot as plt

def getUnit(xl):
    if "电压" in xl:
        return " V"
    elif "电流" in xl:
        return " A"
    elif "电阻" in xl:
        return " Ω"

# 设置全局字体为支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']    # 设置字体为 SimHei（黑体）
plt.rcParams['axes.unicode_minus'] = False      # 解决负号显示问题

PRO_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PRO_DIR)

from ele_drawer import EleDrawer
from state.ele_device_state import EleState
from tabel_design import TableDesignWidget

import numpy as np
import matplotlib.pyplot as plt

CHAT_URL = "http://127.0.0.1:8000/chat"

def get_u(I: np.ndarray, R: np.ndarray):
    return (I/R).sum()/(1/R**2).sum()


def get_r(I: np.ndarray, U: np.ndarray):
    return (I*U).sum()/(I**2).sum()


class StreamLabel(QLabel):
    def __init__(self, parent):
        super().__init__()
        self.parent_w = parent
        self.streamMan = QtNetwork.QNetworkAccessManager(self)
        self.streamMan.finished.connect(self.stream_finished)
        self.streamReq = QtNetwork.QNetworkRequest(QUrl("http://127.0.0.1:8000/stream"))
        self.streamRes = self.streamMan.get(self.streamReq)
        self.streamRes.readyRead.connect(self.stream_read)
        
    def stream_read(self):
        data = self.streamRes.readAll()
        self.setText(self.text() + data.data().decode("utf-8"))
        if self.width() >= 500:
            self.setFixedWidth(500)
            self.setWordWrap(True)
        self.adjustSize()
        self.parent_w.adjustItemSize()
        
    def stream_finished(self, reply):
        if reply.error():
            print(f"Stream Get Err! {reply.errorString()}")
        else:
            print("Stream End!")
        self.parent_w.parent_w.load_success()

        

class MessageBlock(QFrame):
    def __init__(self, state, parent):
        super().__init__()
        self.parent_w = parent
        self.state = state
        self.init_attr()
        self.init_ui()
   
    def init_attr(self):
        self.setMaximumWidth(600)
        self.setStyleSheet("""
            MessageBlock {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 16px;
            }
        """)

    def set_ui(self, state):
        self.state = state
        self.ws.clear()

        while self.lay.count():
            item = self.lay.takeAt(0)  # 从布局中移除组件
            widget = item.widget()
            if widget:
                widget.deleteLater()  # 删除组件并释放内存

        self.state2ui()
        self.update()

    def state2ui(self):
        for msg in self.state:
            if msg["type"] == "text":
                label = QLabel()
                label.setText(msg["data"])
                label.adjustSize()
                if label.width() >= 500:
                    label.setFixedWidth(500)
                    label.setWordWrap(True)
                else:
                    label.setWordWrap(False)
                self.lay.addWidget(label)
                self.ws.append(label)
            elif msg["type"] == "radio":
                group = QButtonGroup()
                for i, item in enumerate(msg["items"]):
                    rhlay = QHBoxLayout()
                    rhlay.setContentsMargins(0, 0, 0, 0)
                    rlabel = QLabel(f"{msg['items'][item]}")
                    rlabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                    rlabel.adjustSize()
                    if rlabel.width() > 400:
                        rlabel.setFixedWidth(400)
                        rlabel.setWordWrap(True)
                    rabtn = QRadioButton()
                    rabtn.setText(f"{item}.")
                    rhlay.addWidget(rabtn, alignment=Qt.AlignmentFlag.AlignTop)
                    rhlay.addWidget(rlabel, alignment=Qt.AlignmentFlag.AlignLeft)
                    rhlay.addStretch()
                    group.addButton(rabtn)
                    self.lay.addLayout(rhlay)
                self.ws.append(group)
            elif msg["type"] == "img":
                label = QLabel()
                img = msg["data"].scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)
                label.setPixmap(QPixmap.fromImage(img))
                self.lay.addWidget(label)
                self.ws.append(label)
            elif msg["type"] == "btn":
                btn = QPushButton()
                btn.setText(msg["title"])
                btn.clicked.connect(lambda t, m=msg: m["action"](**m["args"]))
                self.lay.addWidget(btn)
                self.ws.append(btn)
            elif msg["type"] == "table":
                broswer = QTextBrowser()
                broswer.setHtml(msg["data"])
                broswer.setStyleSheet("""
                    QTextBrowser {
                        border: none;
                    }
                """)
                self.lay.addWidget(broswer)
                self.ws.append(broswer)
            elif msg["type"] == "stream":
                label = StreamLabel(self)
                self.lay.addWidget(label)
                self.ws.append(label)
    
    def adjustItemSize(self):
        self.parent_w.adjustItemSize()
                      
    def init_ui(self):
        self.ws = []
        self.lay = QVBoxLayout()
        self.state2ui()        
        self.setLayout(self.lay)


class OneMessage(QWidget):
    def __init__(self, state, item):
        super().__init__()
        self.state = state
        self.p_item = item

        self.init_state()
        self.init_attr()
        self.init_ui()

    def init_item(self):
        self.p_item.setSizeHint(self.sizeHint())
        self.p_item.setFlags(self.p_item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
        self.update()

    def init_state(self):
        self.isload = self.state["load"]
        self.is_teacher = self.state["is_teacher"]
        if self.is_teacher:
            self.label_text = "老师"
        else:
            self.label_text = "学生"

    def init_attr(self):
        self.setStyleSheet("""
        """)
        self.load_icon = QMovie(os.path.join(PRO_DIR, "widget/res/load.gif"))
        self.load_icon.setScaledSize(QSize(36, 36))

    def init_ui(self):
        self.label = QLabel(self.label_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedWidth(56)
        self.label.setFixedHeight(56)

        if self.is_teacher:
            self.label.setStyleSheet("""
                QLabel { 
                    font-size: 18px;
                    border-radius: 28px;
                    background-color: #44A08D;
                    color: #fff;
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel { 
                    font-size: 18px;
                    border-radius: 28px;
                    background-color: #2193b0;
                    color: #fff;
                }
            """)
        
        self.message_blk = MessageBlock(self.state["message"], self)
        self.h_lay = QHBoxLayout()
        self.load_label = QLabel()
        self.load_label.setMovie(self.load_icon)
        self.load_label.setFixedSize(36, 36)

        if self.is_teacher:
            self.h_lay.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignTop)
            self.h_lay.addWidget(self.message_blk, alignment=Qt.AlignmentFlag.AlignLeft)
            if self.isload:
                self.load_icon.start()
                self.h_lay.addWidget(self.load_label)
            self.message_blk.adjustSize()
            self.h_lay.addStretch()
        else:
            self.h_lay.addStretch()
            if self.isload:
                self.load_icon.start()
                self.h_lay.addWidget(self.load_label)
            self.h_lay.addWidget(self.message_blk, alignment=Qt.AlignmentFlag.AlignRight)
            self.h_lay.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignTop)
        
        self.setLayout(self.h_lay)
    
    def load_success(self):
        if self.isload:
            self.isload = False
            self.load_icon.stop()
            self.load_label.hide()

    def adjustItemSize(self):
        self.p_item.setSizeHint(self.sizeHint())


class ChatWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent_w = parent
        self.videoplayer = self.parent_w.video_player
        self.loadingMsg = None
        self.preResType = ""
        self.fflag = True
        
        self.init_state()
        self.init_attr()
        self.init_ui()

    def resEnd(self, res):
        reply = res["reply"]
        cent = {  
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": f"{reply}"},
                {"type": "btn", "title": "重新开始", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "RESTART"}}
            ]
        }
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase("end")
        
    def resQuesOK(self, res):
        key = res["key"]
        fee = res["fee"][key]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": f"{fee}"},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "CIRCUIT_GET"}}
            ]
        }
        self.pop_item()
        self.add_message(cent)

    def resQuesRetry(self, res):
        wrong = res["wrong_answer"]
        ques = res["question"]
        opt  = res["opt"]
        fee   = res["fee"][wrong]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": f"回答错误。{fee}请再回答一次。"},
            ]
        }
        self.pop_item()
        self.add_message(cent)
        cent = {
             "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": ques},
                {"type": "radio", "items": opt},
                {"type": "btn", "title": "提交", "action": ChatWidget.actionAnswerQues, "args": {"chat_w": self, "idx": self.list_box.count()}},
            ]
        }
        self.add_message(cent)

    def resQuesGet(self, res):
        ques = res["question"]
        opt  = res["opt"]
        phase = res["phase"]
        cent = {
            "is_teacher": True, "load": False, 
            "message": [
                {"type": "text", "data": ques},
                {"type": "radio", "items": opt},
                {"type": "btn", "title": "提交", "action": ChatWidget.actionAnswerQues, "args": {"chat_w": self, "idx": self.list_box.count()-1}},
            ]
        }
        
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)

    def resQuesFailed(self, res):
        key = res["key"]
        fee = res["fee"][key]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": f"回答错误。正确答案是{key}。{fee}"},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "CIRCUIT_GET"}}
            ]
        }
        self.pop_item()
        self.add_message(cent)
    
    def resTableGet(self, res):
        reply = res["reply"]
        tabel_type = res["table_type"]
        phase = res["phase"]
        cent = {
             "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "设计表格", "action": ChatWidget.actionDesignTable, "args": {"chat_w": self, "table_type": tabel_type}},
            ]
        }
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)

    def resTableOK(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "CONN_GET"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)

    def resTableEr(self, res):
        reply = res["reply"]
        table = res["table"]

        html_t = self.table_ui_w.markdown_to_html(table["markdown"])
        
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": f"{reply}下面的表格是才是正确的哦！"},
                {"type": "table", "data":  html_t},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "CONN_GET"}},
            ]
        }

        if table["table"] == "UI":
            self.table_ui_w.setUITable()
        elif table["table"] == "IR":
            self.table_ir_w.setIRTable()
        
        self.pop_item()
        self.add_message(cent)


    def resCircuitGet(self, res):
        reply = res["reply"]
        cent = {
             "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "设计电路", "action": ChatWidget.actionDesignCircuit, "args": {"chat_w": self}},
            ]
        }
        phase = res["phase"]
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)

    def resCircuitOK(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "TABLE_GET"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)

    ## HSY
    def resCircuitEr(self, res):
        pass

    def resConnGet(self, res):
        reply = res["reply"]
        cent = {
             "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "提交电路连接图片", "action": ChatWidget.actionConnSubmit, "args": {"chat_w": self}},
            ]
        }
        phase = res["phase"]
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)
        
        # DEBUG
        # self.videoplayer.pause_toggle()

    def resConnOK(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "END"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)

    ## HSY
    def resConnEr(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "重新提交电路连接图片", "action": ChatWidget.actionConnSubmit, "args": {"chat_w": self}},
            ]
        }
        self.pop_item()
        self.add_message(cent)

    def resRecordGet(self, res):
        reply = res["reply"]
        table_type = res["table_type"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "打开表格", "action": ChatWidget.actionOpenTable, "args": {"chat_w": self, "table": table_type}},
            ]
        }
        phase = res["phase"]
        
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)

    def resRecordOK(self, res):
        reply = res["reply"]
        table = res["table_type"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "绘制曲线图", "action": ChatWidget.actionDrawCurve, "args": {"chat_w": self, "table": table}},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "TIDYUP_GET"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)
    
    def resRecordEr(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": f"{reply}"},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "TIDYUP_GET"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)
    
    def resTidyupGet(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "提交整理图片", "action": ChatWidget.actionSubmitTidyImg, "args": {"chat_w": self}},
            ]
        }
        phase = res["phase"]
        
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)
    
    def resTidyupOK(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "END"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)
    
    def resTidyupEr(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "END"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)

    def resGetSum(self, res):
        reply = res["reply"]
        phase = res["phase"]
        
        try:
            cent = {
                "is_teacher": True, "load": False, "message": [
                    {"type": "text", "data": "<h2>总结</h2>"},
                    {"type": "text", "data": f'<p>{reply["生成评价"]["overall_evaluation"]["summary"]}</p>'},
                    {"type": "text", "data": f'<p>得分：{reply["生成评价"]["overall_evaluation"]["score"]}/{reply["生成评价"]["overall_evaluation"]["max_score"]}</p>'},
                ]
            }
            cent["message"].append({"type": "btn", "title": "获取详细文档", "action": ChatWidget.actionGetSumPdf, "args": {"chat_w": self, "json_text": reply}}),
            cent["message"].append({"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "END"}})
        except:
            cent = {
                "is_teacher": True, "load": False, "message": [
                    {"type": "text", "data": f'服务端结果生成错误！'},
                ]
            }
            cent["message"].append({"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "END"}})
        
        self.pop_item()
        self.add_message(cent)
        self.parent_w.progress.setPhase(phase)

    def resAPIEr(self, res):
        reply = res["reply"]
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "text", "data": reply},
                {"type": "btn", "title": "下一步", "action": ChatWidget.actionNextStep, "args": {"chat_w": self, "next": "END"}},
            ]
        }
        self.pop_item()
        self.add_message(cent)

    '''
    Init 操作
    '''
    def init_state(self):
        self.res_action_map = {
            "END": [self.resEnd],
            "QUES_OK": [self.resQuesOK],
            "QUES_RETRY": [self.resQuesRetry],
            "QUES_GET": [self.resQuesGet],
            "QUES_FAILED": [self.resQuesFailed],
            "TABLE_GET": [self.resTableGet],
            "TABLE_OK": [self.resTableOK],
            "TABLE_ER": [self.resTableEr],
            "CIRCUIT_GET": [self.resCircuitGet],
            "CIRCUIT_OK": [self.resCircuitOK],
            "CIRCUIT_ER": [self.resCircuitEr],
            "CONN_GET": [self.resConnGet],
            "CONN_OK": [self.resConnOK],
            "CONN_ER": [self.resConnEr],
            "RECORD_GET": [self.resRecordGet],
            "RECORD_OK": [self.resRecordOK],
            "RECORD_ER": [self.resRecordEr],
            "TIDYUP_GET": [self.resTidyupGet],
            "TIDYUP_OK": [self.resTidyupOK],
            "TIDYUP_ER": [self.resTidyupEr],
            "SUM_GET": [self.resGetSum],
            "API_ER": [self.resAPIEr]
        }
        self.message_cnt = 1
        self.state = {
            "cnt": 1,
            "msgs": [
                {
                    "is_teacher": True,  "load": False, "idx": 0, "message": [
                        {"type": "btn", "title": "开始实验", "action": ChatWidget.actionStartExp, "args": { "chat_w": self, "videoplayer": self.videoplayer, "idx": 0 }},
                    ]
                }
                ,
                {
                    "is_teacher": True,  "load": True, "idx": 0, "message": [
                        {"type": "stream"},
                        {"type": "btn", "title": "开始实验", "action": ChatWidget.actionStartExp, "args": { "chat_w": self, "videoplayer": self.videoplayer, "idx": 0 }},
                    ]
                }
            ]
        }

        self.net_man = QtNetwork.QNetworkAccessManager(self)
        self.net_man.finished.connect(self.on_req_finished)

    def init_attr(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("""
          
        """)

    def add_message(self, msg):
        self.state["msgs"].append(msg)
        msg["idx"] = self.state["cnt"]
        self.state["cnt"] += 1

        item = QListWidgetItem(self.list_box)
        item_cent = OneMessage(msg, item)
        item.setSizeHint(item_cent.sizeHint())
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
        self.list_box.addItem(item)
        self.list_box.setItemWidget(item, item_cent)

        self.list_box.scrollToBottom()

        return item_cent

    def pop_item(self):
        self.state["msgs"].pop()
        self.state["cnt"] -= 1
        cnt = self.list_box.count()
        if cnt > 0:
            last_item = self.list_box.item(cnt - 1)
            last_wid = self.list_box.itemWidget(last_item)
            self.list_box.takeItem(cnt - 1)
            if last_wid:
                last_wid.deleteLater()
            del last_item
        
    def init_ui(self):

        self.circuit_design_w = EleDrawer(self)
        self.circuit_design_w.submited.connect(self.actionCirDesignSubmit)
        self.cir_des_diag = QDialog()
        self.cir_diag_lay = QVBoxLayout()
        self.cir_diag_lay.addWidget(self.circuit_design_w)
        self.cir_des_diag.setLayout(self.cir_diag_lay)

        self.table_ui_w = TableDesignWidget(self)
        self.table_ui_w.submited.connect(self.actionUITableSub)
        self.table_ui_diag = QDialog()
        self.table_ui_lay = QVBoxLayout()
        self.table_ui_lay.addWidget(self.table_ui_w)
        self.table_ui_diag.setLayout(self.table_ui_lay)

        self.table_ir_w = TableDesignWidget(self)
        self.table_ir_w.submited.connect(self.actionIRTableSub)
        self.table_ir_diag = QDialog()
        self.table_ir_lay = QVBoxLayout()
        self.table_ir_lay.addWidget(self.table_ir_w)
        self.table_ir_diag.setLayout(self.table_ir_lay)

        self.tabel_coonts = {
            "UI": self.table_ui_w,
            "IR": self.table_ir_w
        }
        
        self.tables = {
            "UI": self.table_ui_diag,
            "IR": self.table_ir_diag
        }

        self.v_lay = QVBoxLayout()
        self.list_box = QListWidget()
        self.list_box.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.list_box.setUniformItemSizes(False)
        self.list_box.setStyleSheet("""
            QListWidget {
                background-color: #eeeeee;
            }
        """)
        self.v_lay.addWidget(self.list_box)

        for m in self.state["msgs"]:
            item = QListWidgetItem(self.list_box)
            item_cent = OneMessage(m, item)
            item.setSizeHint(item_cent.sizeHint())
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable & ~Qt.ItemFlag.ItemIsEnabled)
            self.list_box.addItem(item)
            self.list_box.setItemWidget(item, item_cent)
            self.list_box.scrollToBottom()


        self.setLayout(self.v_lay)






    '''
    网络请求
    '''
    def send_post_req(self, url, data):
        send_url = QUrl(url)
        send_data = QByteArray()
        send_data.append(data)

        req = QtNetwork.QNetworkRequest(send_url)
        req.setHeader(QtNetwork.QNetworkRequest.KnownHeaders.ContentTypeHeader, 'application/json')

        self.net_man.post(req, send_data)

    def on_req_finished(self, reply):
        status_code = reply.attribute(QtNetwork.QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code == 200:
            response_data = reply.readAll().data().decode('utf-8')
            self.process_server_res(json.loads(response_data))
        else:
            pass
        reply.deleteLater()

    def process_server_res(self, res):
        if "type" in res:
            self.preResType = res["type"]
            self.res_action_map[self.preResType][0](res)



    '''
    按钮响应区
    '''
    ## HSY
    def actionGetSumPdf(chat_w, json_text):
        path = json_to_pdf(json_text, os.path.join(PRO_DIR, "sum.html"))
        cent = {
            "is_teacher": False, "load": False, "message": [
                {"type": "text", "data": f'生成完毕，保存在 <a href="file:///{path}">{path}</a>'}
            ]
        }
        chat_w.add_message(cent)
        
    def actionDrawCurve(chat_w, table):
        s = chat_w.tabel_coonts[table].get_table_state()
        
        datas = dict()
        idx2col = []
        for c in s[0]:
            datas[c["value"]] = []
            idx2col.append(c["value"])
        for row in s[1:]:
            for idx, col in enumerate(row):
                datas[idx2col[idx]].append(float(col["value"]))
        
        xl = idx2col[1]
        yl = idx2col[2]
        
        datas[xl] = np.array(datas[xl])
        datas[yl] = np.array(datas[yl])
        
        plt.clf()
        plt.xlabel(xl + getUnit(xl))
        plt.ylabel(yl + getUnit(yl))
        plt.scatter(datas[xl], datas[yl])

        xx = []
        yy = []
        
        if table == "UI":
            plt.title("UI曲线图")
            k = get_r(datas[xl], datas[yl])
            xx = np.linspace(0, datas[xl].max()*1.5, 10)
            yy = k*xx
        elif table == "IR":
            plt.title("IR曲线图")
            k = get_u(datas[xl], datas[yl])
            xx = np.linspace(datas[xl].min()/2, datas[xl].max()*1.5, 100)
            yy = k/xx
                
        plt.plot(xx, yy)
        plt.savefig(os.path.join(PRO_DIR, "temp", "ui.png"))
        
        ui_label = QLabel()
        ui_label.setPixmap(QPixmap(os.path.join(PRO_DIR, "temp", "ui.png")))
        
        cent = {
            "is_teacher": True, "load": False, "message": [
                {"type": "img", "data": QImage(os.path.join(PRO_DIR, "temp", "ui.png"))}
            ]
        }
        chat_w.add_message(cent)
        
        lay = QVBoxLayout()
        lay.addWidget(ui_label)
        
        diag = QDialog()
        diag.setLayout(lay)
        diag.exec_()
    
    def actionOpenTable(chat_w, table):
        chat_w.tables[table].setFixedHeight(650)
        chat_w.tables[table].show()
    
    def actionSubmitTidyImg(chat_w):
        frame = chat_w.videoplayer.get_curframe()
        height, width, channel = frame.shape
        qimage = QImage(frame.data, width, height, channel * width, QImage.Format.Format_BGR888)
        cent = {
            "is_teacher": False, "load": False, "message": [
                {"type": "text", "data": "这是整理后的桌面图片。"},
                {"type": "img", "data": qimage}
            ]
        }

        b64 = base64.b64encode(frame.tobytes()).decode("utf-8")
        req_body = {
            "type": "TIDYUP_SUBMIT",
            "answer": "OK",
            "data": b64,
            "w": 1600,
            "h": 928,
            "c": 3
        }

        chat_w.add_message(cent)
        chat_w.loadingMsg = chat_w.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        chat_w.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))
    
    def actionConnSubmit(chat_w):
        frame = chat_w.videoplayer.get_curframe()
        height, width, channel = frame.shape
        qimage = QImage(frame.data, width, height, channel * width, QImage.Format.Format_BGR888)
        cent = {
            "is_teacher": False, "load": False, "message": [
                {"type": "text", "data": "这是我连接的电路图"},
                {"type": "img", "data": qimage}
            ]
        }

        b64 = base64.b64encode(frame.tobytes()).decode("utf-8")

        req_body = {
            "type": "CONN_SUBMIT",
            "answer": "OK",
            "data": b64,
            "h": 928,
            "w": 1600,
            "c": 3
        }

        chat_w.add_message(cent)
        chat_w.loadingMsg = chat_w.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        chat_w.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))

    def actionUITableSub(self, table_state, md):
        req_body = {
            "type": "TABLE_SUBMIT",
            "answer": "OK",
            "table_type": "UI",
            "data": table_state
        }        

        self.add_message({
            "is_teacher": False, "load": False, "message": [
                {"type": "text", "data": "这是我设计的表格。"},
                {"type": "table", "data": md}]
        })
        self.loadingMsg = self.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        self.table_ui_diag.close()
        self.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))

    def actionIRTableSub(self, table_state, md):
        req_body = {
            "type": "TABLE_SUBMIT",
            "answer": "OK",
            "data": table_state,
            "table_type": "IR"
        }    

        self.add_message({
            "is_teacher": False, "load": False, "message": [
                {"type": "text", "data": "这是我设计的表格。"},
                {"type": "table", "data": md}]
        })
            
        self.loadingMsg = self.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        self.table_ir_diag.close()
        self.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))

    def actionDesignTable(chat_w, table_type):
        chat_w.tables[table_type].setFixedHeight(650)
        chat_w.tables[table_type].show()

    def actionCirDesignSubmit(self, ele_state, pixmap):
        cent = {
            "is_teacher": False, "load": False, "message": [
                {"type": "text", "data": "这是我设计的电路图"},
                {"type": "img", "data": pixmap.toImage()}
            ]
        }

        req_body = {
            "type": "CIRCUIT_SUBMIT",
            "answer": "OK",
            "data": ele_state.dump()
        }

        self.add_message(cent)
        self.loadingMsg = self.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        self.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))
        self.cir_des_diag.close()

    def actionDesignCircuit(chat_w):
        chat_w.cir_des_diag.setFixedHeight(650)
        chat_w.cir_des_diag.show()

    def actionNextStep(chat_w, next):
        req_body = {
            "type": next
        }
        chat_w.loadingMsg = chat_w.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        chat_w.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))

    def actionAnswerQues(chat_w, idx):
        item = chat_w.list_box.item(idx)
        wid  = chat_w.list_box.itemWidget(item).message_blk
        btn_grp = wid.ws[1]
        answer = btn_grp.checkedButton().text()[0]
        req_body = {
            "type": "QUES_ANS",
            "answer": answer
        }
        chat_w.add_message( { "is_teacher": False, "load": False, "message": [{"type": "text", "data": f"我选择 {answer}"}]})
        chat_w.loadingMsg = chat_w.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        chat_w.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))

    def actionStartExp(chat_w, videoplayer, idx):
        videoplayer.set_input("rtsp://admin:@192.168.4.13")
        # videoplayer.set_input(os.path.join(PRO_DIR, "labeling-data/02_Record/01_20250121_09.mp4"))
        req_body = {
            "type": "QUES_GET"
        }
        chat_w.add_message( { "is_teacher": False, "load": False, "message": [{"type": "text", "data": "开始吧"}]})
        chat_w.loadingMsg = chat_w.add_message( { "is_teacher": True, "load": True, "message": [{"type": "text", "data": "加载中..."}]})
        chat_w.send_post_req(CHAT_URL, 
                             json.dumps(req_body, ensure_ascii=False).encode("utf-8"))
        # chat_w.parent_w.progress.setPhase("question")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ChatWidget()
    w.show()
    sys.exit(app.exec_())