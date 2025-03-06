# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
# from GUIfive import Ui_MainWindow  # 导入主窗口生成的 UI 类
# from dialogtwo import Ui_Dialog       # 导入对话框生成的 UI 类
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)
#
#         # 为 btn11 按钮绑定点击事件
#         self.ui.btn11.clicked.connect(self.open_dialog)
#
#     def open_dialog(self):
#         # 创建 QDialog 对象
#         dialog = QDialog()
#         dialog_ui = Ui_Dialog()
#         dialog_ui.setupUi(dialog)
#
#         # 显示对话框窗口
#         dialog.exec_()
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec_())
