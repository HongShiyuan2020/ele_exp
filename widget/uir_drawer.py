'''
电图绘制程序
:@author syhong
'''

import sys
import os
import pathlib
import numpy as np
import math

'''
环境配置
'''
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from axwid import CustomCoordinateAxes

def get_u(I: np.ndarray, R: np.ndarray):
    return (I/R).sum()/(1/R**2).sum()


def get_r(I: np.ndarray, U: np.ndarray):
    return (I*U).sum()/(I**2).sum()


class AxSetingDlg(QtWidgets.QDialog):
    
    sunmited = pyqtSignal(str, str, float, str, str, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.lay = QtWidgets.QVBoxLayout()
        xname_label = QtWidgets.QLabel("横轴名称")
        self.xname_com_box = QtWidgets.QComboBox()
        self.xname_com_box.addItem("电压")
        self.xname_com_box.addItem("电流")
        self.xname_com_box.addItem("电阻")
        xunit_label = QtWidgets.QLabel("横轴单位")
        self.xunit_com_box = QtWidgets.QComboBox()
        self.xunit_com_box.addItem("V")
        self.xunit_com_box.addItem("A")
        self.xunit_com_box.addItem("Ω")
        x_hlay = QtWidgets.QHBoxLayout()
        x_hlay.addWidget(xname_label)
        x_hlay.addWidget(self.xname_com_box)
        x_hlay.addStretch()
        x_hlay.addWidget(xunit_label)
        x_hlay.addWidget(self.xunit_com_box)
        x_hlay.addStretch()
        self.lay.addLayout(x_hlay)

        self.x_label_max = QtWidgets.QLabel("横轴最大值")
        self.x_slide_max = QtWidgets.QSlider()
        self.x_slide_max.setMaximum(200)
        self.x_slide_max.setMinimum(1)
        self.x_slide_max.setOrientation(Qt.Orientation.Horizontal)
        self.x_slide_max.valueChanged.connect(self.changeLabelXV)
        self.x_label_maxv = QtWidgets.QLabel("0")
        self.x_slide_max.setFixedWidth(400)

        x_max_lay = QtWidgets.QHBoxLayout()
        x_max_lay.addWidget(self.x_label_max)
        x_max_lay.addWidget(self.x_slide_max)
        x_max_lay.addWidget(self.x_label_maxv)
        self.lay.addLayout(x_max_lay)

        yname_label = QtWidgets.QLabel("纵轴名称")
        self.yname_com_box = QtWidgets.QComboBox()
        self.yname_com_box.addItem("电压")
        self.yname_com_box.addItem("电流")
        self.yname_com_box.addItem("电阻")
        yunit_label = QtWidgets.QLabel("纵轴单位")
        self.yunit_com_box = QtWidgets.QComboBox()
        self.yunit_com_box.addItem("V")
        self.yunit_com_box.addItem("A")
        self.yunit_com_box.addItem("Ω")
        y_hlay = QtWidgets.QHBoxLayout()
        y_hlay.addWidget(yname_label)
        y_hlay.addWidget(self.yname_com_box)
        y_hlay.addStretch()
        y_hlay.addWidget(yunit_label)
        y_hlay.addWidget(self.yunit_com_box)
        y_hlay.addStretch()
        self.lay.addLayout(y_hlay)
        
        self.y_label_max = QtWidgets.QLabel("纵轴最大值")
        self.y_slide_max = QtWidgets.QSlider()
        self.y_slide_max.setMaximum(200)
        self.y_slide_max.setMinimum(1)
        self.y_slide_max.setOrientation(Qt.Orientation.Horizontal)
        self.y_slide_max.valueChanged.connect(self.changeLabelYV)
        self.y_label_maxv = QtWidgets.QLabel("0")
        self.y_slide_max.setFixedWidth(400)
        
        y_max_lay = QtWidgets.QHBoxLayout()
        y_max_lay.addWidget(self.y_label_max)
        y_max_lay.addWidget(self.y_slide_max)
        y_max_lay.addWidget(self.y_label_maxv)
        self.lay.addLayout(y_max_lay)
        
        self.btn_hlay = QtWidgets.QHBoxLayout()
        self.btn_hlay.addStretch()
        self.btn_sub = QtWidgets.QPushButton()
        self.btn_sub.setText("提交")
        self.btn_sub.clicked.connect(self.onSubmit)
        self.btn_hlay.addWidget(self.btn_sub)
        
        self.lay.addLayout(self.btn_hlay)
        self.setLayout(self.lay)

    def changeLabelXV(self, val):
        self.x_label_maxv.setText(f"{float(val)/10}")
        
    def changeLabelYV(self, val):
        self.y_label_maxv.setText(f"{float(val)/10}")
    
    def onSubmit(self):
        self.sunmited.emit(self.xname_com_box.currentText(), self.xunit_com_box.currentText(), self.x_slide_max.value()/10,
                           self.yname_com_box.currentText(), self.yunit_com_box.currentText(), self.y_slide_max.value()/10)
        self.close()
    
class UIRDrawView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(UIRDrawView, self).__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        x = event.pos().x()
        y = event.pos().y()
        self.parent().view_mousemove(float(x), float(y))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        x = event.pos().x()
        y = event.pos().y()
        self.parent().view_mousepress(float(x), float(y))
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        x = event.pos().x()
        y = event.pos().y()
        self.parent().view_mouserelease(float(x), float(y))

'''
绘图Qt组件
'''
class UIRDrawer(QtWidgets.QWidget):
    GRID_WIDTH = 30
    submited = pyqtSignal(bool, QtGui.QPixmap)
    
    def __init__(self, tx_label="电压", ty_label="电流", txl=[1.0, 2.0, 3.0], tyl=[0.1, 0.18, 0.32], parent=None):
        super(UIRDrawer, self).__init__(parent)
        self.tx_label = tx_label
        self.ty_label = ty_label
        self.txl = txl
        self.tyl = tyl
        
        self.init_self()
        self.init_state()
        self.init_widgets()

    def init_state(self):
        self.axis_obj = None
        self.cur_item = None
        self.is_pressed = False
        self.line_pts = []
        self.data_pts = []
        self.draw_type = "None"
        self.o_point = [0.0, 0.0]
        self.axx_scale = 30.0
        self.axy_scale = 30.0
        
    def init_self(self):
        self.move(500, 100)

    def init_widgets(self):
        self.btn_axis = QtWidgets.QPushButton("绘制坐标轴")
        self.btn_axis.clicked.connect(self.on_axis_selected)
        self.btn_pts  = QtWidgets.QPushButton("绘制数据点")
        self.btn_pts.clicked.connect(self.on_point_selected)
        self.btn_curve      = QtWidgets.QPushButton("绘制曲线")
        self.btn_curve.clicked.connect(self.on_curve_selected)
        self.btn_reset       = QtWidgets.QPushButton("重置")
        self.btn_reset.clicked.connect(self.on_reset_selected)
        self.btn_submit  = QtWidgets.QPushButton("提交")
        self.btn_submit.clicked.connect(self.on_submit_clicked)
        
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = UIRDrawView(self)
        self.view.setFixedSize(800, 800)
        self.scene.setSceneRect(0, 0, self.view.width()-2, self.view.height()-2)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setScene(self.scene)
        
        self.grid_line_color = QtGui.QColor()
        self.grid_line_color.setRgb(230, 230, 230)
        self.draw_grid()
        
        self.vmain_layout = QtWidgets.QVBoxLayout()
        self.hbtns_layout = QtWidgets.QHBoxLayout()
        self.hbtns_submit_layout = QtWidgets.QHBoxLayout()

        self.hbtns_layout.addWidget(self.btn_axis)
        self.hbtns_layout.addWidget(self.btn_pts)
        self.hbtns_layout.addWidget(self.btn_curve)
        self.hbtns_layout.addWidget(self.btn_reset)
        
        self.pt_pos_label = QtWidgets.QLabel()
        self.hbtns_submit_layout.addWidget(self.pt_pos_label)
        self.hbtns_submit_layout.addStretch()
        self.hbtns_submit_layout.addWidget(self.btn_submit)
        self.btn_submit.clicked.connect(self.handleSubmit)
        
        self.vmain_layout.addItem(self.hbtns_layout)
        self.vmain_layout.addWidget(self.view)
        self.vmain_layout.addItem(self.hbtns_submit_layout)
                
        self.setLayout(self.vmain_layout)

    def handleSubmit(self):
        pixmap = QtGui.QPixmap(self.view.viewport().rect().size())
        pixmap.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(pixmap)
        painter.setViewport(self.view.viewport().rect())
        painter.setWindow(self.view.rect())
        self.view.render(painter)
        painter.end()

        if self.axis_obj:
            xname    = self.axis_obj.x_name
            yname    = self.axis_obj.y_name
            pts      = self.data_pts
            line_pts = np.array(self.line_pts)
            tx_pts = None
            ty_pts = None
            
            if len(pts) != len(self.txl) or len(pts) != len(self.tyl):
                self.submited.emit(False, pixmap)
                self.close()
                return            

            if xname == yname:
                self.submited.emit(False, pixmap)
                self.close()
                return        
            
            if xname in self.tx_label:
                tx_pts = self.txl
            if yname in self.tx_label:
                ty_pts = self.txl
            if xname in self.ty_label:
                tx_pts = self.tyl
            if yname in self.ty_label:
                ty_pts = self.tyl
            
            if not tx_pts or not ty_pts:
                self.submited.emit(False, pixmap)
                self.close()
                return  
            
            txy_pts = []
            for tx, ty in zip(tx_pts, ty_pts):
                txy_pts.append([tx, ty])
            
            txy_pts.sort()
            pts.sort()
            
            diff = 0
            for [tx, ty], [x, y] in zip(txy_pts, pts):
                diff_v = math.sqrt(((tx-x)*self.axx_scale)**2+((ty-y)*self.axy_scale)**2)
                if diff_v > 30:
                    self.submited.emit(False, pixmap)            
                    self.close()
                    return
                diff += diff_v
            diff /= len(pts)
            
            pts = np.array(pts)
            txy_pts = np.array(txy_pts)
                        
            if xname == "电压" or yname == "电压":
                r = get_r(pts[:, 0], pts[:, 1])

                xarr = line_pts[:, 0]
                y_hat = r*xarr
                
                path = QtGui.QPainterPath()
                x, y = self.ax2pixel(xarr[0], y_hat[0])
                path.moveTo(x, y)
                for x, y in zip(xarr[1:], y_hat[1:]):
                    ax, ay = self.ax2pixel(x, y)
                    path.lineTo(ax, ay)
                item = QtWidgets.QGraphicsPathItem()
                item.setPath(path)
                self.scene.addItem(item)
                
                diff = (np.abs(line_pts[:, 1] - y_hat)*self.axy_scale).mean()
                if diff > 20:
                    self.submited.emit(False, pixmap)            
                    self.close()
                    return
                                
            elif xname == "电阻" or yname == "电阻":
                u = get_u(pts[:, 0], pts[:, 1])
                
                xarr = line_pts[:, 0]
                y_hat = u/xarr
                path = QtGui.QPainterPath()
                x, y = self.ax2pixel(xarr[0], y_hat[0])
                path.moveTo(x, y)
                for x, y in zip(xarr[1:], y_hat[1:]):
                    ax, ay = self.ax2pixel(x, y)
                    path.lineTo(ax, ay)
                item = QtWidgets.QGraphicsPathItem()
                item.setPath(path)
                self.scene.addItem(item)    
                
                diff = (np.abs(line_pts[:, 1] - y_hat)*self.axy_scale).mean()
                if diff > 50:
                    self.submited.emit(False, pixmap)            
                    self.close()
                    return

        self.submited.emit(True, pixmap)            
        self.close()
            
    def pixel2ax(self, x, y):
        return (x - self.o_point[0])/self.axx_scale, (self.o_point[1] - y)/self.axy_scale

    def ax2pixel(self, x, y):
        return x*self.axx_scale+self.o_point[0], self.o_point[1]-y*self.axy_scale

    def draw_grid(self):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setColor(self.grid_line_color)
        for r in range(0, self.view.height() // UIRDrawer.GRID_WIDTH):
            self.scene.addLine(0, r*UIRDrawer.GRID_WIDTH, self.scene.width(), r*UIRDrawer.GRID_WIDTH, pen).setZValue(-2)
        for c in range(0, self.view.width() // UIRDrawer.GRID_WIDTH):
            self.scene.addLine(c*UIRDrawer.GRID_WIDTH, 0, c*UIRDrawer.GRID_WIDTH, self.scene.height(), pen).setZValue(-2)
        
    def setAxis(self, xname, xunit, xmax, yname, yunit, ymax):
        self.cur_item = CustomCoordinateAxes()
        self.cur_item.x_name = xname
        self.cur_item.unit_x = xunit
        self.cur_item.scale_x = (self.cur_item.pix_xlen)//(self.cur_item.skip)*(self.cur_item.skip)/xmax
        self.cur_item.y_name = yname
        self.cur_item.unit_y = yunit
        self.cur_item.scale_y = (self.cur_item.pix_ylen)//(self.cur_item.skip)*(self.cur_item.skip)/ymax
        self.axx_scale = self.cur_item.scale_x
        self.axy_scale = self.cur_item.scale_y
        self.cur_item.draw()
        self.scene.addItem(self.cur_item)
    
    def on_axis_selected(self):
        self.btn_axis.setEnabled(False)
        dlg = AxSetingDlg()
        dlg.sunmited.connect(self.setAxis)
        dlg.exec_()
        self.draw_type = "AX"

    def on_point_selected(self):
        self.draw_type = "PT"
        self.btn_pts.setEnabled(False)
        self.cur_item = QtWidgets.QGraphicsEllipseItem(0, 0, 8, 8)
        pen = QtGui.QPen()
        pen.setWidth(4)
        pen.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        self.cur_item.setPen(pen)
        self.cur_item.setZValue(1)
        self.scene.addItem(self.cur_item)
    
    def on_curve_selected(self):
        self.draw_type = "CR"
        self.btn_curve.setEnabled(False)
    
    def on_reset_selected(self):
        self.scene.clear()
        self.cur_item = None
        self.is_pressed = False
        self.line_pts = []
        self.draw_type = "None"
        self.btn_axis.setEnabled(True)
        self.btn_pts.setEnabled(True)
        self.btn_curve.setEnabled(True)
        self.draw_grid()
    
    def on_submit_clicked(self):
        pass
    
    def view_mousemove(self, x, y):
        if self.draw_type == "CR":
            if self.is_pressed:
                path = self.cur_item.path()        
                path.lineTo(x, y)
                self.cur_item.setPath(path)
                ax, ay = self.pixel2ax(x, y)
                self.line_pts.append([ax, ay])
        elif self.draw_type == "PT":
            self.cur_item.setPos(x-4, y-4)
            axx, axy = self.pixel2ax(x, y)
            self.pt_pos_label.setText(f"({axx:2.2f}, {axy:2.2f})")
        elif self.draw_type == "AX":
            self.cur_item.setPos((x+self.GRID_WIDTH/2)//self.GRID_WIDTH*self.GRID_WIDTH, (y+self.GRID_WIDTH/2)//self.GRID_WIDTH*self.GRID_WIDTH)
        
    def view_mousepress(self, x, y):
        if self.draw_type == "CR":
            self.is_pressed = True
            self.cur_item = QtWidgets.QGraphicsPathItem()
            pen = QtGui.QPen()
            pen.setWidth(3)
            pen.setColor(QtGui.QColor(0, 150, 255))
            self.cur_item.setPen(pen)
            path = self.cur_item.path()        
            path.moveTo(x, y)
            path.lineTo(x, y)
            self.cur_item.setPath(path)
            self.scene.addItem(self.cur_item)
        elif self.draw_type == "PT":
            pass
        elif self.draw_type == "AX":
            pass

    def view_mouserelease(self, x, y):
        self.is_pressed = False
        
        if self.draw_type == "CR":        
            self.draw_type = "None"
            self.btn_curve.setEnabled(True)
        elif self.draw_type == "PT":
            axx, axy = self.pixel2ax(x, y)
            self.data_pts.append([axx, axy])
            self.draw_type = "None"
            self.btn_pts.setEnabled(True)
            self.cur_item = None
        elif self.draw_type == "AX":
            self.axis_obj = self.cur_item
            self.cur_item = None
            self.draw_type = "None"
            self.btn_axis.setEnabled(True)
            self.o_point = [(x+self.GRID_WIDTH/2)//self.GRID_WIDTH*self.GRID_WIDTH, 
                            (y+self.GRID_WIDTH/2)//self.GRID_WIDTH*self.GRID_WIDTH]

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = UIRDrawer()
    w.show()
    sys.exit(app.exec_())
    
    