'''
进度条
'''


from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QApplication, QWidget, QProgressBar
import sys

class ProgressTip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phases = {
            "start": {
                "title": "开始实验"
            },
            "question": {
                "title": "情景导入"
            },
            "evidence": {
                "title": "设计思考"
            },
            "analysis": {
                "title": "实验验证"
            },
            "discussion": {
                "title": "总结思考"
            },
            "evaluation": {
                "title": "结果评价"
            },
            "end": {
                "title": "试验结束",
                "pos": 100
            },
            "list": ["start", "question", "evidence", "analysis", "discussion", "evaluation"]
        }
        cnt = 100.0 / (len(self.phases["list"]))
        for idx,  pha in enumerate(self.phases["list"]):
            self.phases[pha]["pos"] = idx*cnt
        self.cur_phase = "start"
        self.init_ui()
    
    def init_ui(self):
        self.lay = QVBoxLayout()
        self.hlabellay = QHBoxLayout()
        
        for pha in self.phases["list"]:
            label = QLabel(self.phases[pha]["title"])
            self.hlabellay.addWidget(label)
            self.hlabellay.addStretch()
            label.setStyleSheet('''
                                QLabel {font-size: 22px}
                                ''')
        end_label = QLabel(self.phases["end"]["title"])
        end_label.setStyleSheet('''
                            QLabel {font-size: 22px}
                            ''')
        self.hlabellay.addWidget(end_label)


        
        self.progress_bar = QProgressBar()
        
        self.progress_bar.setStyleSheet('''
                                        QProgressBar {
                                            background: rgb(255, 255, 255);
                                            margin: 0px 43px 0px 43px;
                                        }
                                        
                                        QProgressBar::chunk {
                                            background-color: #2196F3;  /* 蓝色 */

                                        }
                                       
                                        ''')
        self.curStepLabel = QLabel(f"当前阶段：{'开始实验'}")
        self.curStepLabel.setStyleSheet('''
                        QLabel {font-size: 22px}
                        ''')
        self.lay.addStretch()
        self.lay.addWidget(self.curStepLabel)
        self.lay.addStretch()
        self.lay.addLayout(self.hlabellay)
        self.lay.addWidget(self.progress_bar)
        self.lay.addStretch()
        self.setLayout(self.lay)
    
    
    def setPhase(self, pha):
        self.curStepLabel.setText(f"当前阶段：{self.phases[pha]['title']}")
        self.progress_bar.setValue(self.phases[pha]["pos"])
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ProgressTip()
    w.show()
    w.setPhase("end")
    sys.exit(app.exec_())