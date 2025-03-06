import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLineEdit, QLabel
from PyQt5.QtGui import QFont
from dialogtwo import Ui_Dialog
from GUIfive import Ui_MainWindow

class Block:
    def __init__(self, block_type, value):
        self.type = block_type  # 类型：label 或 input
        self.value = value      # 值：标签的文本或输入框的内容

    def __repr__(self):
        return f"Block(type={self.type}, value={self.value})"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.current_button = None  # 记录当前被点击的按钮
        self.bind_all_buttons()

        self.saved_table_data = None  # 用于存储保存后的表格数据

        # 绑定“确定”按钮事件
        self.ui.btn_confirm.clicked.connect(self.save_table_state)

    def bind_all_buttons(self):
        # 遍历所有的按钮
        for i in range(1, 7):  # 按照命名规则绑定按钮
            for j in range(1, 6):
                button_name = f"btn{i}{j}"
                button = getattr(self.ui, button_name, None)  # 动态获取按钮对象
                if button:
                    button.clicked.connect(lambda _, b=button: self.open_dialog(b))

    def open_dialog(self, button):
        self.current_button = button  # 记录当前被点击的按钮

        # 创建并显示对话框
        dialog = CustomDialog(self)
        dialog.exec_()

    def get_table_state(self):
        layout = self.ui.gridLayout  # 获取表格的 QGridLayout
        row_count = layout.rowCount()  # 行数
        col_count = layout.columnCount()  # 列数

        table_data = []  # 用于存储整个表格的状态

        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                widget = layout.itemAtPosition(row, col).widget()  # 获取单元格中的控件
                if widget:
                    if isinstance(widget, QLabel):
                        row_data.append(Block("label", widget.text()))  # 标签
                    elif isinstance(widget, QLineEdit):
                        row_data.append(Block("input", widget.text()))  # 输入框
                    else:
                        row_data.append(Block("empty", ""))  # 未识别的控件
                else:
                    row_data.append(Block("empty", ""))  # 空单元格
            table_data.append(row_data)

        return table_data

    def save_table_state(self):
        table_data = self.get_table_state()  # 获取当前表格状态

        # 输出到控制台（调试用）
        for row in table_data:
            print(row)

        # 保存到类属性以供其他部分使用
        self.saved_table_data = table_data
        print("表格状态已保存！")

class CustomDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # 绑定“设置为数据输入框”按钮点击事件
        self.ui.pushButton.clicked.connect(self.set_to_input)
        self.ui.pushButton_2.clicked.connect(self.set_to_label)  # 绑定点击事件

    def set_to_input(self):
        main_window = self.parent()  # 获取主窗口实例
        button = main_window.current_button  # 获取当前被点击的按钮

        if button:
            # 获取按钮的父布局
            layout = button.parent().layout()

            # 替换按钮为 QLineEdit
            line_edit = QLineEdit(button.parent())
            line_edit.setText("")
            line_edit.setMinimumSize(button.size())
            line_edit.setAlignment(QtCore.Qt.AlignCenter)  # 设置文字居中

            # 设置字体大小
            font = QFont()
            font.setPointSize(11)  # 设置字号为 11，可以根据需要调整
            line_edit.setFont(font)

            layout.replaceWidget(button, line_edit)
            button.deleteLater()  # 删除原按钮

        self.accept()  # 关闭对话框

    def set_to_label(self):
        main_window = self.parent()  # 获取主窗口实例
        button = main_window.current_button  # 获取当前被点击的按钮

        if button:
            # 获取输入框的文本
            input_text = self.ui.textEdit.toPlainText()

            # 获取按钮的父布局
            layout = button.parent().layout()

            # 替换按钮为 QLabel
            label = QtWidgets.QLabel(button.parent())
            label.setText(input_text if input_text else "")  # 如果未输入，显示“默认文本”
            # label.setText(input_text)  # 如果未输入，显示“默认文本”
            label.setAlignment(QtCore.Qt.AlignCenter)  # 文本居中对齐
            label.setMinimumSize(button.size())

            layout.replaceWidget(button, label)
            button.deleteLater()  # 删除原按钮

        self.accept()  # 关闭对话框


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
