'''
电路图绘制程序
:@author syhong
'''



import sys
import os
import pathlib


'''
环境配置
'''

FILE_ABS_PATH = pathlib.Path(__file__).resolve()
WIDGET_ROOT = pathlib.Path(FILE_ABS_PATH.parent)
if str(WIDGET_ROOT) not in sys.path:
    sys.path.append(str(WIDGET_ROOT))
PROJ_ROOT = pathlib.Path(WIDGET_ROOT.parent)
if str(PROJ_ROOT) not in sys.path:
    sys.path.append(str(PROJ_ROOT))

from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from state.ele_device_state import EleState, EleDevice, EleBindPos, EleLine

##################################################################################


'''
电路组件
'''

class EleBindPosItem(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, x: float, y: float, w: float, h: float, parent=None, parent_id=-1, id=-1, name=EleBindPos.BP_P):
        super(EleBindPosItem, self).__init__(x, y, w, h, parent)
        self.id = id
        self.name = name
        self.parent_id = parent_id

class EleBatteryItemMain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None, id=-1):
        super(EleBatteryItemMain, self).__init__(parent)
        self.id = id
        self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/B.png"))
        self.name = EleDevice.DEVICE_B
        self.width = 60
        self.height = 60
        self.setPixmap(self.img)

class EleBatteryItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, id=-1):
        super(EleBatteryItem, self).__init__(parent)
        self.id = id
        self.name = EleDevice.DEVICE_B
        self.bp1 = self.id*4
        self.bp2 = self.id*4 + 1
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.main_item = EleBatteryItemMain(id=self.id) 
        self.bp1_item  = EleBindPosItem(-3, 30-4, 6, 6, id=self.bp1, name=EleBindPos.BP_N, parent_id=self.id) 
        self.bp2_item  = EleBindPosItem(57, 30-4, 6, 6, id=self.bp2, name=EleBindPos.BP_P, parent_id=self.id)
        self.bp1_item.setZValue(1)
        self.bp2_item.setZValue(1)

        self.addToGroup(self.main_item)
        self.addToGroup(self.bp1_item)
        self.addToGroup(self.bp2_item)

class EleResistanceItemMain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None, id=-1):
        super(EleResistanceItemMain, self).__init__(parent)
        self.id = id
        self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/R.png"))
        self.name = EleDevice.DEVICE_R
        self.width = 60
        self.height = 60
        self.setPixmap(self.img)

class EleResistanceItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, id=-1):
        super(EleResistanceItem, self).__init__(parent)
        self.id = id
        self.name = EleDevice.DEVICE_R
        self.bp1 = self.id*4
        self.bp2 = self.id*4 + 1
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.main_item = EleResistanceItemMain(id=self.id) 
        self.bp1_item  = EleBindPosItem(-3, 30-4, 6, 6, id=self.bp1, name=EleBindPos.BP_N, parent_id=self.id) 
        self.bp2_item  = EleBindPosItem(57, 30-4, 6, 6, id=self.bp2, name=EleBindPos.BP_P, parent_id=self.id)
        self.bp1_item.setZValue(1)
        self.bp2_item.setZValue(1)

        self.addToGroup(self.main_item)
        self.addToGroup(self.bp1_item)
        self.addToGroup(self.bp2_item)

class EleSwitchItemMain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None, id=-1):
        super(EleSwitchItemMain, self).__init__(parent)
        self.id = id
        self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/S_O.png"))
        self.name = EleDevice.DEVICE_S
        self.width = 120
        self.height = 60
        self.setPixmap(self.img)

class EleSwitchItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, id=-1):
        super(EleSwitchItem, self).__init__(parent)
        self.id = id
        self.name = EleDevice.DEVICE_S
        self.bp1 = self.id*4
        self.bp2 = self.id*4 + 1
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.main_item = EleSwitchItemMain(id=self.id) 
        self.bp1_item  = EleBindPosItem(-3, 30-4, 6, 6, id=self.bp1, name=EleBindPos.BP_P, parent_id=self.id) 
        self.bp2_item  = EleBindPosItem(117, 30-4, 6, 6, id=self.bp2, name=EleBindPos.BP_N, parent_id=self.id)
        self.bp1_item.setZValue(1)
        self.bp2_item.setZValue(1)

        self.addToGroup(self.main_item)
        self.addToGroup(self.bp1_item)
        self.addToGroup(self.bp2_item)

class EleAmmeterItemMain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None, id=-1, high_r=False):
        super(EleAmmeterItemMain, self).__init__(parent)
        self.id = id
        if not high_r:
            self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/A_06.png"))
        else:
            self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/A_30.png"))

        self.name = EleDevice.DEVICE_A
        self.width = 120
        self.height = 60
        self.setPixmap(self.img)

class EleAmmeterItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, id=-1, high_r=False):
        super(EleAmmeterItem, self).__init__(parent)
        self.id = id
        self.name = EleDevice.DEVICE_A
        self.bp1 = self.id*4
        self.bp2 = self.id*4 + 1
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.main_item = EleAmmeterItemMain(id=self.id, high_r=high_r) 
        self.bp1_item  = EleBindPosItem(-3,  30-3, 6, 6, id=self.bp1, name=EleBindPos.BP_N, parent_id=self.id) 
        if not high_r:
            self.bp2_item  = EleBindPosItem(117, 30-3, 6, 6, id=self.bp2, name=EleBindPos.BP_VA_PLOW, parent_id=self.id)
        else:
            self.bp2_item  = EleBindPosItem(117, 30-3, 6, 6, id=self.bp2, name=EleBindPos.BP_VA_PHIGH, parent_id=self.id)

        self.bp1_item.setZValue(1)
        self.bp2_item.setZValue(1)

        self.addToGroup(self.main_item)
        self.addToGroup(self.bp1_item)
        self.addToGroup(self.bp2_item)

class EleVoltmeterItemMain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None, id=-1, high_r=False):
        super(EleVoltmeterItemMain, self).__init__(parent)
        self.id = id
        if not high_r:
            self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/V_30.png"))
        else:
            self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/V_150.png"))
        self.name = EleDevice.DEVICE_V
        self.width = 120
        self.height = 60
        self.setPixmap(self.img)

class EleVoltmeterItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, id=-1, high_r=False):
        super(EleVoltmeterItem, self).__init__(parent)
        self.id = id
        self.name = EleDevice.DEVICE_V
        self.bp1 = self.id*4
        self.bp2 = self.id*4 + 1
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.main_item = EleVoltmeterItemMain(id=self.id, high_r=high_r) 
        self.bp1_item  = EleBindPosItem(-3,  30-3, 6, 6, id=self.bp1, name=EleBindPos.BP_N, parent_id=self.id) 
        if not high_r:
            self.bp2_item  = EleBindPosItem(117, 30-3, 6, 6, id=self.bp2, name=EleBindPos.BP_VA_PLOW, parent_id=self.id)
        else:
            self.bp2_item  = EleBindPosItem(117, 30-3, 6, 6, id=self.bp2, name=EleBindPos.BP_VA_PHIGH, parent_id=self.id)
        self.bp1_item.setZValue(1)
        self.bp2_item.setZValue(1)

        self.addToGroup(self.main_item)
        self.addToGroup(self.bp1_item)
        self.addToGroup(self.bp2_item)

class EleSRItemMain(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None, id=-1):
        super(EleSRItemMain, self).__init__(parent)
        self.id = id
        self.img = QtGui.QPixmap(os.path.join(PROJ_ROOT, "widget/res/SR_.png"))
        self.name = EleDevice.DEVICE_SR
        self.width = 120
        self.height = 60
        self.setPixmap(self.img)

class EleSRItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, parent=None, id=-1):
        super(EleSRItem, self).__init__(parent)
        self.id = id
        self.name = EleDevice.DEVICE_SR
        self.bp1 = self.id*4
        self.bp2 = self.id*4 + 1
        self.bp3 = self.id*4 + 2

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.main_item = EleSRItemMain(id=self.id) 
        self.bp1_item  = EleBindPosItem(-3,  30-3, 6, 6, id=self.bp1, name=EleBindPos.BP_SR_NL, parent_id=self.id) 
        self.bp2_item  = EleBindPosItem(117, 30-3, 6, 6, id=self.bp2, name=EleBindPos.BP_SR_NR, parent_id=self.id)
        self.bp3_item  = EleBindPosItem(57,  -3,   6, 6, id=self.bp3, name=EleBindPos.BP_SR_P,  parent_id=self.id)

        self.bp1_item.setZValue(1)
        self.bp2_item.setZValue(1)
        self.bp3_item.setZValue(1)

        self.addToGroup(self.main_item)
        self.addToGroup(self.bp1_item)
        self.addToGroup(self.bp2_item)
        self.addToGroup(self.bp3_item)


class EleView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None, ctr_w=None):
        super(EleView, self).__init__(parent)
        self.setMouseTracking(True)
        self.ctr_w = ctr_w

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        x = event.pos().x()
        y = event.pos().y()
        self.ctr_w.move_event(float(x), float(y))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        x = event.pos().x()
        y = event.pos().y()
        self.ctr_w.press_event(float(x), float(y), event.button())




'''
绘图Qt组件
'''
class EleDrawer(QtWidgets.QWidget):

    GRID_WIDTH = 30

    submited = pyqtSignal(EleState, QtGui.QPixmap)


    def __init__(self, parent=None):
        super(EleDrawer, self).__init__(parent)
        self.init_self()
        self.init_state()
        self.init_widgets()

    def init_state(self):
        self.ele_state = EleState(dict(), dict(), dict())
        self.cur_target_item = None
        self.pressed_btn = None
        self.is_line = False
        self.line_from = None
        self.line_to   = None
        self.line_path = None
        self.device_next_id = 0
        self.line_next_id = 0
        self.bps_next_id = 0

    def init_self(self):
        self.resize(1200, 900)

    def init_widgets(self):
        self.btn_battery = QtWidgets.QPushButton("电源")
        self.btn_battery.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/B.png")))
        self.btn_battery.clicked.connect(self.on_battery_btn_clicked)

        self.btn_switch  = QtWidgets.QPushButton("开关")
        self.btn_switch.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/S.png")))
        self.btn_switch.clicked.connect(self.on_switch_btn_clicked)

        self.btn_sr      = QtWidgets.QPushButton("滑动变阻器")
        self.btn_sr.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/SR.png")))
        self.btn_sr.clicked.connect(self.on_sr_btn_clicked)

        self.btn_r       = QtWidgets.QPushButton("电阻")
        self.btn_r.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/R.png")))
        self.btn_r.clicked.connect(self.on_r_btn_clicked)

        self.btn_a       = QtWidgets.QPushButton("电流表0.6A")
        self.btn_a.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/A.png")))
        self.btn_a.clicked.connect(self.on_a_btn_clicked)

        self.btn_a30       = QtWidgets.QPushButton("电流表3A")
        self.btn_a30.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/A.png")))
        self.btn_a30.clicked.connect(self.on_a30_btn_clicked)

        self.btn_v       = QtWidgets.QPushButton("电压表3V")
        self.btn_v.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/V.png")))
        self.btn_v.clicked.connect(self.on_v_btn_clicked)

        self.btn_v150       = QtWidgets.QPushButton("电压表15V")
        self.btn_v150.setIcon(QtGui.QIcon(os.path.join(PROJ_ROOT, "widget/res/V.png")))
        self.btn_v150.clicked.connect(self.on_v150_btn_clicked)

        self.btn_line    = QtWidgets.QPushButton("导线")
        self.btn_line.clicked.connect(self.on_line_btn_clicked)

        self.btn_delete  = QtWidgets.QPushButton("删除")
        self.btn_delete.clicked.connect(self.on_delete_btn_clicked)

        self.btn_reset   = QtWidgets.QPushButton("重置")
        self.btn_reset.clicked.connect(self.on_reset_btn_clicked)
        
        self.btn_submit  = QtWidgets.QPushButton("提交")
        self.btn_submit.clicked.connect(self.on_submit_btn_clicked)
        
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = EleView(self, self)
        self.scene.setSceneRect(0, 0, self.view.width(), self.view.height())
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setScene(self.scene)
        self.grid_line_color = QtGui.QColor()
        self.grid_line_color.setRgb(230, 230, 230)
        self.draw_grid()

        self.vmain_layout = QtWidgets.QVBoxLayout()
        self.hbtns_layout = QtWidgets.QHBoxLayout()
        self.hbtns_submit_layout = QtWidgets.QHBoxLayout()
        self.hbtns_layout.addWidget(self.btn_battery)
        self.hbtns_layout.addWidget(self.btn_switch)
        self.hbtns_layout.addWidget(self.btn_sr)
        self.hbtns_layout.addWidget(self.btn_r)
        self.hbtns_layout.addWidget(self.btn_a)
        self.hbtns_layout.addWidget(self.btn_a30)
        self.hbtns_layout.addWidget(self.btn_v)
        self.hbtns_layout.addWidget(self.btn_v150)
        self.hbtns_layout.addWidget(self.btn_line)
        self.hbtns_layout.addWidget(self.btn_delete)
        self.hbtns_layout.addWidget(self.btn_reset)
        self.hbtns_submit_layout.addStretch()
        self.hbtns_submit_layout.addWidget(self.btn_submit)
        self.vmain_layout.addItem(self.hbtns_layout)
        self.vmain_layout.addWidget(self.view)
        self.vmain_layout.addItem(self.hbtns_submit_layout)
        self.setLayout(self.vmain_layout)

    def draw_grid(self):
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setColor(self.grid_line_color)
        for r in range(0, self.height() // EleDrawer.GRID_WIDTH):
            self.scene.addLine(0, r*EleDrawer.GRID_WIDTH, self.width(), r*EleDrawer.GRID_WIDTH, pen).setZValue(-2)
        for c in range(0, self.width() // EleDrawer.GRID_WIDTH):
            self.scene.addLine(c*EleDrawer.GRID_WIDTH, 0, c*EleDrawer.GRID_WIDTH, self.height(), pen).setZValue(-2)

    def on_a30_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleAmmeterItem(id=self.device_next_id, high_r=True)
        self.device_next_id += 1
        self.btn_a30.setEnabled(False)
        self.pressed_btn = self.btn_a30
        self.scene.addItem(self.cur_target_item)

    def on_v150_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleVoltmeterItem(id=self.device_next_id, high_r=True)
        self.device_next_id += 1
        self.btn_v150.setEnabled(False)
        self.pressed_btn = self.btn_v150
        self.scene.addItem(self.cur_target_item)

    def on_battery_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleBatteryItem(id=self.device_next_id)
        self.device_next_id += 1
        self.btn_battery.setEnabled(False)
        self.pressed_btn = self.btn_battery
        self.scene.addItem(self.cur_target_item)
        
    def on_switch_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleSwitchItem(id=self.device_next_id)
        self.device_next_id += 1
        self.btn_switch.setEnabled(False)
        self.pressed_btn = self.btn_switch
        self.scene.addItem(self.cur_target_item)

    def on_sr_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleSRItem(id=self.device_next_id)
        self.device_next_id += 1
        self.btn_sr.setEnabled(False)
        self.pressed_btn = self.btn_sr
        self.scene.addItem(self.cur_target_item)

    def on_r_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleResistanceItem(id=self.device_next_id)
        self.device_next_id += 1
        self.btn_r.setEnabled(False)
        self.pressed_btn = self.btn_r
        self.scene.addItem(self.cur_target_item)

    def on_a_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleAmmeterItem(id=self.device_next_id)
        self.device_next_id += 1
        self.btn_a.setEnabled(False)
        self.pressed_btn = self.btn_a
        self.scene.addItem(self.cur_target_item)

    def on_v_btn_clicked(self):
        self.reset_other_btn()
        self.cur_target_item =EleVoltmeterItem(id=self.device_next_id)
        self.device_next_id += 1
        self.btn_v.setEnabled(False)
        self.pressed_btn = self.btn_v
        self.scene.addItem(self.cur_target_item)

    def on_delete_btn_clicked(self):
        self.reset_other_btn()

    def on_reset_btn_clicked(self):
        self.reset_other_btn()
        self.ele_state = EleState(dict(), dict(), dict())
        self.scene.clear()
        self.device_next_id = 0
        self.line_next_id = 0

    def on_submit_btn_clicked(self):
        self.reset_other_btn()
        pixmap = QtGui.QPixmap(self.view.viewport().rect().size())
        pixmap.fill(Qt.GlobalColor.white)
        painter = QtGui.QPainter(pixmap)
        painter.setViewport(self.view.viewport().rect())
        painter.setWindow(self.view.rect())
        self.view.render(painter)
        painter.end()

        self.submited.emit(self.ele_state, pixmap)

    def on_line_btn_clicked(self):
        self.reset_other_btn()
        self.is_line = True
        self.btn_line.setEnabled(False)
        self.pressed_btn = self.btn_line   
        self.cur_target_item = QtWidgets.QGraphicsEllipseItem(-2, -2, 4, 4)
        self.line_path = QtWidgets.QGraphicsPathItem()
        pen = QtGui.QPen()
        pen.setWidth(3)
        self.line_path.setPen(pen)
        self.cur_target_item.setZValue(-1)
        self.line_path.setZValue(-1)
        self.scene.addItem(self.cur_target_item)
        self.scene.addItem(self.line_path)

    def reset_other_btn(self):
        self.line_from = None
        self.line_to = None
        self.is_line = False
        if self.pressed_btn != None:
            self.pressed_btn.setEnabled(True)
            self.pressed_btn = None
            if self.cur_target_item != None:
                self.scene.removeItem(self.cur_target_item)
                self.cur_target_item = None
            if self.line_path != None:
                self.scene.removeItem(self.line_path)
                self.line_path = None
                
    def mousePressEvent(self, a0):
        super().mousePressEvent(a0)
        item = self.view.itemAt(a0.pos())

    def move_event(self, x: float, y: float):
        if not self.is_line and self.cur_target_item != None:
            self.cur_target_item.setPos((x//EleDrawer.GRID_WIDTH)*EleDrawer.GRID_WIDTH
                                        , (y//EleDrawer.GRID_WIDTH)*EleDrawer.GRID_WIDTH)
            return
        
        if self.is_line and self.cur_target_item != None:
            self.cur_target_item.setPos(((x+EleDrawer.GRID_WIDTH//2)//EleDrawer.GRID_WIDTH)*EleDrawer.GRID_WIDTH
                                        , ((y+EleDrawer.GRID_WIDTH//2)//EleDrawer.GRID_WIDTH)*EleDrawer.GRID_WIDTH)
            
    def press_event(self, x: float, y: float, btn: Qt.MouseButton):
        # 右键取消当前绘制过程
        if btn == Qt.MouseButton.RightButton:
            self.reset_other_btn()
            return
        
        # 如果正在绘制器件
        if not self.is_line and self.cur_target_item != None: 
            bp3_id = -1
            if isinstance(self.cur_target_item, EleSRItem):
                bp3_id = self.cur_target_item.bp3

            self.ele_state.components[self.cur_target_item.id] = EleDevice(
                self.cur_target_item.id, 
                self.cur_target_item.name,
                self.cur_target_item.bp1, self.cur_target_item.bp2, bp3_id
            )

            for item in self.cur_target_item.childItems():
                if isinstance(item, EleBindPosItem):
                    self.ele_state.bps[item.id] = EleBindPos(
                        item.id,
                        item.name,
                        item.parent_id
                    )

            self.cur_target_item = None
            self.pressed_btn.setEnabled(True)
            self.pressed_btn = None
            # print(self.ele_state.dump())
            return

        # 如果正在绘制连线
        if self.is_line and self.cur_target_item != None:
            ix = ((x+EleDrawer.GRID_WIDTH//2)//EleDrawer.GRID_WIDTH)*EleDrawer.GRID_WIDTH
            iy = ((y+EleDrawer.GRID_WIDTH//2)//EleDrawer.GRID_WIDTH)*EleDrawer.GRID_WIDTH
            
            if not self.line_from:
                self.line_from = [ix, iy, self.view.itemAt(int(ix), int(iy))]
                path = self.line_path.path()
                path.moveTo(ix, iy)
                self.line_path.setPath(path)
            else:
                path = self.line_path.path()
                path.lineTo(ix, iy)
                self.line_path.setPath(path)
                to_item = self.view.itemAt(int(ix), int(iy))
                if isinstance(to_item, EleBindPosItem):
                    from_id = -1
                    from_parent_id = -1
                    if isinstance(self.line_from[-1], EleBindPosItem):
                        from_id = self.line_from[-1].id
                        from_parent_id = self.line_from[-1].parent_id

                    self.ele_state.lines[self.line_next_id] = EleLine(
                        self.line_next_id,
                        from_id,
                        to_item.id,
                        from_parent_id,
                        to_item.parent_id
                    )
                    self.line_next_id += 1
                    self.line_path = None
                    self.reset_other_btn()                    

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.scene.setSceneRect(0, 0, self.view.width(), self.view.height())

    def keyPressEvent(self, a0):
        super().keyPressEvent(a0)
        if self.cur_target_item != None:
            if a0.key() == Qt.Key.Key_R:
                self.cur_target_item.setRotation((self.cur_target_item.rotation()+90)%360)




'''
测试代码
'''
class TestDiag(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        w = EleDrawer()
        w.submited.connect(self.handle_submit)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(w)
        
        self.setLayout(vlayout)
        self.resize(700, 700)
        self.show()

    def handle_submit(self, ele_state: EleState, pixmap: QtGui.QPixmap):
        pixmap.save(os.path.join(PROJ_ROOT, "temp/demo.png"), "png")
        ele_json = ele_state.dump()
        with open(os.path.join(PROJ_ROOT, "temp/demo.json"), "w", encoding="utf-8") as fout:
            fout.write(ele_json)        
        self.destroy()
        exit(0)

if __name__ == "__main__":
    app =QtWidgets.QApplication(sys.argv)
    diag = TestDiag()
    sys.exit(app.exec_())