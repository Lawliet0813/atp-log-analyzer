# src/visualization/custom_widgets.py

class SpeedGauge(QWidget):
    """速度儀表元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.warning_threshold = 80
        self.critical_threshold = 90
        self.setup_ui()
        
    def setup_ui(self):
        """設置UI"""
        self.setMinimumSize(200, 200)
        
    def set_value(self, value: float):
        """設置速度值"""
        self.value = value
        self.update()
        
    def paintEvent(self, event):
        """繪製儀表板"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 計算尺寸和位置
        width = self.width()
        height = self.height()
        center = QPoint(width/2, height/2)
        radius = min(width, height)/2 - 10
        
        # 繪製外圈
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(center, radius, radius)
        
        # 繪製刻度
        self._draw_scales(painter, center, radius)
        
        # 繪製指針
        self._draw_needle(painter, center, radius)
        
        # 繪製數值
        self._draw_value(painter, center)

class EventTimeline(QWidget):
    """事件時間軸元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = []
        self.start_time = None
        self.end_time = None
        
    def set_events(self, events: List[Dict]):
        """設置事件數據"""
        self.events = sorted(events, key=lambda x: x['timestamp'])
        if self.events:
            self.start_time = self.events[0]['timestamp']
            self.end_time = self.events[-1]['timestamp']
        self.update()
        
    def paintEvent(self, event):
        """繪製時間軸"""
        if not self.events:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 繪製主軸線
        width = self.width()
        height = self.height()
        y = height/2
        
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawLine(10, y, width-10, y)
        
        # 繪製事件點
        total_duration = (self.end_time - self.start_time).total_seconds()
        for event in self.events:
            # 計算X位置
            rel_time = (event['timestamp'] - self.start_time).total_seconds()
            x = 10 + (width-20) * (rel_time/total_duration)
            
            # 根據事件類型設置顏色
            if event['severity'] == 'CRITICAL':
                color = QColor('#e74c3c')
            elif event['severity'] == 'HIGH':
                color = QColor('#f39c12')
            else:
                color = QColor('#3498db')
                
            # 繪製事件點
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), 5, 5)
