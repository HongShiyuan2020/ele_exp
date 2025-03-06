'''
主界面
'''

import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtNetwork
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSizePolicy, QFrame, QListWidget

import video_palyer
import chatwidget
import sys

from toolips import ProgressTip

import os
PRO_ROOT = os.path.dirname(os.path.dirname(__file__))


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.height__ = 56
        self.parent = parent  # 保存父窗口的引用
        self.setFixedHeight(self.height__)  # 设置标题栏高度
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 去除布局边距

        # 标题标签
        self.title_label = QLabel("基于大模型的中学物理探究实验系统", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # 关闭按钮
        self.close_button = QPushButton("×", self)
        self.close_button.setFixedSize(self.height__, self.height__)
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.close_button)
        layout.setSpacing(0)

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
                font-size: 28px;
                margin: 0;
            }
            QPushButton {
                background-color: #2c3e50;
                font-size: 36px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff0000;
            }
            QFrame {
                border-radius: 0px;
            }
        """)



class MainWnd(QWidget):
    def __init__(self):
        super().__init__()
        self.init_attr()
        self.init_ui()

    def init_attr(self):
        self.setContentsMargins(0, 0, 0, 0)


    def init_ui(self):
        self.wnd_layout = QVBoxLayout()

        self.topbar = CustomTitleBar(self)
        self.video_player = video_palyer.VideoPlayer("")
        self.video_player.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_player.setMinimumHeight(800)
        self.video_vbox_lay = QVBoxLayout()
        self.video_vbox_lay.addWidget(self.video_player)
        self.progress_frame = QFrame()
        self.progress = ProgressTip()
        self.progress_lay = QVBoxLayout()
        self.progress_lay.addWidget(self.progress)
        self.progress_frame.setLayout(self.progress_lay)
        self.video_vbox_lay.addWidget(self.progress_frame)
        self.progress_frame.setObjectName("progr_frame")
        self.progress_frame.setStyleSheet('''
                                          #progr_frame {
                                              background-color: #eeeeee;
                                              margin: 10px;
                                              border: 1px solid rgb(100, 100, 189);
                                          }
                                          ''')
        
        
        self.left_frame = QFrame()
        self.video_vbox_lay.setContentsMargins(0, 0, 0, 0)
        self.left_frame.setLayout(self.video_vbox_lay)
        
        
        self.chat_list = chatwidget.ChatWidget(self)
        self.chat_list.setFixedWidth(800)
        self.chat_list.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.chat_vbox_lay = QVBoxLayout()
        self.chat_vbox_lay.setContentsMargins(0, 0, 0, 0)
        self.chat_vbox_lay.addWidget(self.chat_list)
        self.right_frame = QFrame()
        self.right_frame.setLayout(self.chat_vbox_lay)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.left_frame)
        self.main_layout.addWidget(self.right_frame)

        self.wnd_layout.addWidget(self.topbar)
        self.wnd_layout.addLayout(self.main_layout)
        self.wnd_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.wnd_layout)  
        self.setObjectName("main_wnd")
        self.setStyleSheet("""
        #main_wnd {
            background-color: #ffffff;
        }
        """)
    
    def close(self):
        if self.video_player and self.video_player.video_thread:
            self.video_player.stop_stream()
        return super().close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWnd()
    w.showFullScreen()
    sys.exit(app.exec_())