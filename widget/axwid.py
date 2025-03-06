from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsScene, QGraphicsView
import PyQt5.QtWidgets as QtW
from PyQt5.QtGui import QPainter, QPen, QFont, QBrush, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPointF


class CustomCoordinateAxes(QGraphicsItemGroup):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化属性
        self.origin_pos = [0.0, 0.0]
        self.scale_x = 30.0   
        self.scale_y = 30.0   # 纵轴缩放比例
        self.x_name = "电流"  # 横轴名称
        self.y_name = "电压"  # 纵轴名称
        self.unit_x = "A"    # 横轴单位
        self.unit_y = "V"    # 纵轴单位
        
        self.pix_xlen = 650
        self.pix_ylen = 650
        self.skip = 60
        
        self.pen = QPen()
        self.pen.setWidth(3)
        
        # self.create_axisx()  # 创建坐标轴
        # self.create_axisy()  # 创建坐标轴
    
    def create_axisx(self):
        self.xline = QtW.QGraphicsLineItem(self.origin_pos[0], self.origin_pos[1], self.origin_pos[0]+self.pix_xlen, self.origin_pos[1])
        self.xline.setPen(self.pen)
        pp = QPainterPath()
        pp.moveTo(self.origin_pos[0]+self.pix_xlen-14, self.origin_pos[1]-8)
        pp.lineTo(self.origin_pos[0]+self.pix_xlen, self.origin_pos[1])
        pp.lineTo(self.origin_pos[0]+self.pix_xlen-14, self.origin_pos[1]+8)
        self.x_arrow = QtW.QGraphicsPathItem(pp)
        self.x_arrow.setPen(self.pen)
        for x_tick in range(int(self.origin_pos[0]), int(self.origin_pos[0])+int(self.pix_xlen), self.skip):
            tick_line = QtW.QGraphicsLineItem(x_tick, self.origin_pos[1], x_tick, self.origin_pos[1]-10)
            pen = QPen()
            pen.setWidth(2)
            tick_line.setPen(pen)
            font = QFont()
            font.setBold(True)
            ax, ay = self.pixel2ax(x_tick, 0)
            text_item = QtW.QGraphicsTextItem(f"{ax:.02f}")
            text_item.setFont(font)
            text_item.setPos(x_tick-14, self.origin_pos[1])
            self.addToGroup(tick_line)
            self.addToGroup(text_item)
            
        ax_label = QtW.QGraphicsTextItem(f"{self.x_name}/{self.unit_x}")
        font = QFont()
        font.setBold(True)
        ax_label.setFont(font)
        ax_label_w = ax_label.boundingRect().width()
        ax_label.setPos(self.origin_pos[0]+self.pix_xlen/2-ax_label_w/2, self.origin_pos[1]+24)
        
        self.addToGroup(ax_label)
        self.addToGroup(self.xline)
        self.addToGroup(self.x_arrow)
    
    def create_axisy(self):
        self.yline = QtW.QGraphicsLineItem(self.origin_pos[0], self.origin_pos[1], self.origin_pos[0], self.origin_pos[1]-self.pix_ylen)
        self.yline.setPen(self.pen)
        pp = QPainterPath()
        pp.moveTo(self.origin_pos[0]-8, self.origin_pos[1]-self.pix_ylen+14)
        pp.lineTo(self.origin_pos[0], self.origin_pos[1]-self.pix_ylen)
        pp.lineTo(self.origin_pos[0]+8, self.origin_pos[1]-self.pix_ylen+14)
        self.y_arrow = QtW.QGraphicsPathItem(pp)
        self.y_arrow.setPen(self.pen)
        for y_tick in range(int(self.origin_pos[1]), int(self.origin_pos[1])-int(self.pix_xlen), -self.skip):
            tick_line = QtW.QGraphicsLineItem(self.origin_pos[0], y_tick, self.origin_pos[0]+10, y_tick)
            pen = QPen()
            pen.setWidth(2)
            tick_line.setPen(pen)
            font = QFont()
            font.setBold(True)
            ax, ay = self.pixel2ax(0, y_tick)
            text_item = QtW.QGraphicsTextItem(f"{ay:.02f}")
            text_item.setFont(font)
            font_w = text_item.boundingRect().width()
            text_item.setPos(self.origin_pos[0]-4-font_w, y_tick-14)
            
            self.addToGroup(tick_line)
            self.addToGroup(text_item)
            
        ay_label = QtW.QGraphicsTextItem(f"{self.y_name}/{self.unit_y}")
        font = QFont()
        font.setBold(True)
        ay_label.setFont(font)
        ay_label_w = ay_label.boundingRect().width()
        ay_label.setRotation(-90)
        ay_label.setPos(self.origin_pos[0]-80, self.origin_pos[1]-self.pix_ylen/2+ay_label_w/2)
        
        self.addToGroup(ay_label)
        self.addToGroup(self.yline)
        self.addToGroup(self.y_arrow)
        
        cc = QtW.QGraphicsEllipseItem(-5, -5, 10, 10)
        self.addToGroup(cc)
    
    def draw(self):
        self.create_axisx()
        self.create_axisy()
    
    def pixel2ax(self, x, y):
        return (x - self.origin_pos[0])/self.scale_x, (self.origin_pos[1] - y)/self.scale_y
    
# 示例用法
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    view.setGeometry(100, 100, 800, 600)
    
    axes = CustomCoordinateAxes()
    scene.addItem(axes)
    
    view.show()
    sys.exit(app.exec_())