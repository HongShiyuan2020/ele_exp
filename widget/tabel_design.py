import sys
import json

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QLabel, QWidget, QSpacerItem, QSizePolicy, QTextBrowser
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
from dialogtwo import Ui_Dialog
from widgetOne import Ui_MainWidget

class Block:
    def __init__(self, block_type, value):
        self.type = block_type  # 类型：label 或 input
        self.value = value      # 值：标签的文本或输入框的内容

    def __repr__(self):
        return f"Block(type={self.type}, value={self.value})"
    
    def dump(self):
        return {
            "type": self.type,
            "value": self.value
        }

UI_TABLE = [
    [[1, "序号"], [1, "电流"], [1, "电压"]],
    [[1, "1"], [2, ""], [2, ""]],
    [[1, "2"], [2, ""], [2, ""]],
    [[1, "3"], [2, ""], [2, ""]]
]

IR_TABLE = [
    [[1, "序号"], [1, "电流"], [1, "电阻"]],
    [[1, "1"], [2, ""], [2, ""]],
    [[1, "2"], [2, ""], [2, ""]],
    [[1, "3"], [2, ""], [2, ""]]
]


def setInput(button):
    layout = button.parent().layout()

    # 替换按钮为 QLineEdit
    line_edit = QLineEdit(button.parent())
    line_edit.setFixedSize(189, 60)
    line_edit.setText("")
    line_edit.setMinimumSize(button.size())
    line_edit.setAlignment(QtCore.Qt.AlignCenter)  # 设置文字居中

    # 设置字体大小
    font = QFont()
    font.setPointSize(11)  # 设置字号为 11，可以根据需要调整
    line_edit.setFont(font)

    layout.replaceWidget(button, line_edit)
    button.deleteLater()  # 删除原按钮

def setLabel(button, input_text):
    layout = button.parent().layout()
    # 替换按钮为 QLabel
    label = QtWidgets.QLabel(button.parent())
    label.setText(input_text if input_text else "")  # 如果未输入，显示“默认文本”
    # label.setText(input_text)  # 如果未输入，显示“默认文本”
    label.setAlignment(QtCore.Qt.AlignCenter)  # 文本居中对齐
    label.setMinimumSize(button.size())

    layout.replaceWidget(button, label)
    button.deleteLater()  # 删除原按钮

class TableDesignWidget(QWidget):

    submited = pyqtSignal(list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWidget()  # Ui_MainWindow 可以重命名为 Ui_MainWidget 更贴切
        self.ui.setupUi(self)

        self.current_button = None  # 记录当前被点击的按钮
        self.bind_all_buttons()

        self.saved_table_data = None  # 用于存储保存后的表格数据

        # 绑定“确定”按钮事件
        self.ui.btn_confirm.clicked.connect(self.hide_custom_buttons)
        self.ui.btn_confirm_3.clicked.connect(self.hide_custom_buttons)
        self.ui.btn_confirm_3.clicked.connect(self.onSubmit)

    def setUITable(self):
        layout = self.ui.gridLayout
        for row in range(len(UI_TABLE)):
            for col in range(len(UI_TABLE[0])):
                widget = layout.itemAtPosition(row, col).widget()
                item = UI_TABLE[row][col]
                if item[0] == 1:
                    setLabel(widget, item[1])
                elif item[0] == 2:
                    setInput(widget)

    def setIRTable(self):
        layout = self.ui.gridLayout
        for row in range(len(IR_TABLE)):
            for col in range(len(IR_TABLE[0])):
                widget = layout.itemAtPosition(row, col).widget()
                item = IR_TABLE[row][col]
                if item[0] == 1:
                    setLabel(widget, item[1])
                elif item[0] == 2:
                    setInput(widget)
                
                
    def onSubmit(self):
        s, md = self.get_markdown_and_state()
        self.submited.emit(s, md)

    def hide_custom_buttons(self):
        layout = self.ui.gridLayout  # 获取表格的 QGridLayout
        # 遍历布局中的所有控件
        for row in range(layout.rowCount()):
            for col in range(layout.columnCount()):
                widget = layout.itemAtPosition(row, col).widget()  # 获取当前单元格的控件
                if widget and isinstance(widget, QtWidgets.QPushButton):  # 判断是否为按钮
                    if widget.text() == "自定义":  # 检查按钮的文本是否为“自定义”
                        widget.hide()  # 隐藏按钮

                        # 添加一个占位控件，保持布局结构
                        spacer = QSpacerItem(193, 60, QSizePolicy.Minimum, QSizePolicy.Minimum)
                        layout.addItem(spacer, row, col)

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
        dialog = TablePickDlg(self)
        dialog.exec_()

    # 将 Markdown 表格转换为 HTML 表格
    def markdown_to_html(self, markdown):
        lines = markdown.strip().split('\n')
        html = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                border: 1px solid #000;
                padding: 8px;
                text-align: left;
            }
        </style>
        <table>
        """
        for i, line in enumerate(lines):
            if i == 0:
                html += "<thead>"
            elif i == 1:
                continue  # 跳过分隔线
            elif i == 2:
                html += "<tbody>"
            
            if line.startswith('|'):
                cells = line.split('|')[1:-1]  # 去掉开头和结尾的空格
                html += "<tr>"
                for cell in cells:
                    if i == 0:
                        html += f"<th>{cell.strip()}</th>"
                    else:
                        html += f"<td>{cell.strip()}</td>"
                html += "</tr>"
            
            if i == 0:
                html += "</thead>"
        html += "</tbody></table>"
        return html
    
    def get_markdown_and_state(self):
        tabel_data = self.get_table_state()
        md_lines = []
        for r in tabel_data:
            line = "|  "
            for c in r:
                if c["value"] != "":
                    line += f'{c["value"]}  |'
                else:
                    line += '   ____  |'
            line += "\n"
            md_lines.append(line)
            
        head_line = ""
        if len(tabel_data) != 0:    
            head_line = md_lines[0] + "| "
            for c in tabel_data[0]:
                head_line += " :---: |"
            head_line += "\n"

        for l in md_lines[1:]:
            head_line += l
            
        return tabel_data, self.markdown_to_html(head_line)

    def get_table_state(self):
        layout = self.ui.gridLayout  # 获取表格的 QGridLayout
        row_count = layout.rowCount()  # 行数
        col_count = layout.columnCount()  # 列数
        table_data = []  # 用于存储整个表格的状态

        lidx = 10
        ridx = 0
        tidx = 10
        bidx = 0
        
        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                widget = layout.itemAtPosition(row, col).widget()  # 获取单元格中的控件
                if widget:
                    if isinstance(widget, QLabel):
                        row_data.append(Block("label", widget.text()).dump())  # 标签
                        if col > ridx:
                            ridx = col
                        if col < lidx:
                            lidx = col
                        if row > bidx:
                            bidx = row
                        if row < tidx:
                            tidx = row
                    elif isinstance(widget, QLineEdit):
                        row_data.append(Block("input", widget.text()).dump())  # 输入框
                        if col > ridx:
                            ridx = col
                        if col < lidx:
                            lidx = col
                        if row > bidx:
                            bidx = row
                        if row < tidx:
                            tidx = row
                    else:
                        row_data.append(Block("empty", "").dump())  # 未识别的控件
                else:
                    row_data.append(Block("empty", "").dump())  # 空单元格
            table_data.append(row_data)

            if lidx == 10:
                lidx = 0
            if tidx == 10:
                tidx = 0
        
        new_table_data = []
        for r in table_data[tidx:bidx+1]:
            new_table_data.append(r[lidx:ridx+1])
        
        return new_table_data

class TablePickDlg(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.v_btn = QtWidgets.QPushButton("设为电压标签")
        self.v_btn.setFixedSize(200, 100)
        self.v_btn.clicked.connect(lambda : self.set_w_label("电压"))
        self.a_btn = QtWidgets.QPushButton("设为电流标签")
        self.a_btn.setFixedSize(200, 100)
        self.a_btn.clicked.connect(lambda : self.set_w_label("电流"))
        self.o_btn = QtWidgets.QPushButton("设为电阻标签")
        self.o_btn.setFixedSize(200, 100)
        self.o_btn.clicked.connect(lambda : self.set_w_label("电阻"))
        self.n_btn = QtWidgets.QPushButton("设为序号标签")
        self.n_btn.setFixedSize(200, 100)
        self.n_btn.clicked.connect(lambda : self.set_w_label("序号"))
        self.i_btn = QtWidgets.QPushButton("设为输入框")
        self.i_btn.setFixedHeight(100)
        self.i_btn.clicked.connect(lambda : self.set_w_input())
        
        self.idx_label = QtWidgets.QLabel("1")
        self.idx_slide = QtWidgets.QSlider()
        self.idx_slide.setMaximum(10)
        self.idx_slide.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.idx_slide.setMinimum(1)
        self.idx_slide.valueChanged.connect(self.change_label)

        self.idx_btn = QtWidgets.QPushButton("设置序号")        
        self.idx_btn.setFixedHeight(100)
        self.idx_btn.clicked.connect(lambda : self.set_w_slide_label())
        
        self.lay = QtWidgets.QGridLayout()
        self.lay.addWidget(self.v_btn, 0, 0)
        self.lay.addWidget(self.a_btn, 0, 1)
        self.lay.addWidget(self.o_btn, 0, 2)
        self.lay.addWidget(self.n_btn, 0, 3)
        self.lay.addWidget(self.i_btn, 1, 0, 1, 4)
        self.lay.addWidget(self.idx_label, 2, 0, 1, 1, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lay.addWidget(self.idx_slide, 2, 1, 1, 3)
        self.lay.addWidget(self.idx_btn, 3, 0, 1, 4)
        self.setLayout(self.lay)        

    def change_label(self, val):
        self.idx_label.setText(str(val))

    def set_w_slide_label(self):
        idx = str(self.idx_slide.value())
        self.set_w_label(idx)

    def set_w_label(self, label_text):
        main_window = self.parent()
        button = main_window.current_button

        if button:
            layout = button.parent().layout()
            label = QtWidgets.QLabel(button.parent())
            label.setText(label_text)  # 如果未输入，显示“默认文本”
            label.setAlignment(QtCore.Qt.AlignCenter)  # 文本居中对齐
            label.setMinimumSize(button.size())
            layout.replaceWidget(button, label)
            button.deleteLater()  # 删除原按钮
        self.accept()  # 关闭对话框
    
    def set_w_input(self):
        main_window = self.parent()  # 获取主窗口实例
        button = main_window.current_button  # 获取当前被点击的按钮

        if button:
            layout = button.parent().layout()
            line_edit = QLineEdit(button.parent())
            line_edit.setFixedSize(189, 60)
            line_edit.setText("")
            line_edit.setMinimumSize(button.size())
            line_edit.setAlignment(QtCore.Qt.AlignCenter)  # 设置文字居中
            font = QFont()
            font.setPointSize(11)  # 设置字号为 11，可以根据需要调整
            line_edit.setFont(font)
            layout.replaceWidget(button, line_edit)
            button.deleteLater()  # 删除原按钮
        self.accept()  # 关闭对话框s
    
    

tabel_test = "| 序号 | 电压 | 电流 | \n | :---: | :---: | :---: | \n | 1 | __ | __ | \n | 2 | __ | __ | \n | 3 | __ | __ | "
style = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #ddd;
        }
    </style>
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TableDesignWidget()
    w.show()
    sys.exit(app.exec_())

