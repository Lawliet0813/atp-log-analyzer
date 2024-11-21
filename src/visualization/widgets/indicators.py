# visualization/widgets/indicators.py

from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QColor, QPaintEvent, QFont
from ..core.base import BaseVisualization

class StatusLight(BaseVisualization):
    """狀態指示燈"""
    
    def __init__(self, parent=None, size: int = 16):
        super().__init__(parent)
        self.status = "normal"  # normal, warning, error
        self.blinking = False
        self.size = size
        self.setFixedSize(size, size)
        
    def set_status(self, status: str):
        """設置狀態"""
        self.status = status
        self.update()
        
    def paintEvent(self, event: QPaintEvent):
        """繪製指示燈"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 確定顏色
        colors = {
            "normal": self.theme.colors["success"],
            "warning": self.theme.colors["warning"],
            "error": self.theme.colors["danger"]
        }
        color = QColor(colors.get(self.status, self.theme.colors["info"]))
        
        # 繪製外圈
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color.darker(120))
        painter.drawEllipse(1, 1, self.size-2, self.size-2)
        
        # 繪製內圈
        painter.setBrush(color)
        painter.drawEllipse(3, 3, self.size-6, self.size-6)
        
        # 繪製高光
        painter.setBrush(color.lighter(150))
        painter.drawEllipse(4, 4, (self.size-8)//2, (self.size-8)//2)

class StatusIndicator(QWidget):
    """狀態指示器"""
    
    status_changed = pyqtSignal(str, str)  # 狀態變更信號
    
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.label = label
        self._setup_ui()
        
    def _setup_ui(self):
        """設置UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        
        # 狀態燈
        self.light = StatusLight(self)
        layout.addWidget(self.light)
        
        # 標籤
        self.label_widget = QLabel(self.label)
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | 
                                     Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.label_widget)
        
        # 狀態文字
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | 
                                     Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def set_status(self, status: str, message: Optional[str] = None):
        """設置狀態"""
        self.light.set_status(status)
        if message:
            self.status_label.setText(message)
        self.status_changed.emit(self.label, status)
        
    def clear_status(self):
        """清除狀態"""
        self.light.set_status("normal")
        self.status_label.clear()

class IndicatorGroup(QWidget):
    """指示器群組"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.indicators = {}
        self._setup_ui()
        
    def _setup_ui(self):
        """設置UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # 標題
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 指示器容器
        self.container = QVBoxLayout()
        layout.addLayout(self.container)
        
        self.setLayout(layout)
        
    def add_indicator(self, name: str, label: str) -> StatusIndicator:
        """添加指示器"""
        indicator = StatusIndicator(label, self)
        self.container.addWidget(indicator)
        self.indicators[name] = indicator
        return indicator
        
    def set_status(self, name: str, status: str, message: Optional[str] = None):
        """設置指示器狀態"""
        if name in self.indicators:
            self.indicators[name].set_status(status, message)
            
    def clear_all(self):
        """清除所有狀態"""
        for indicator in self.indicators.values():
            indicator.clear_status()

class SystemStatusPanel(QWidget):
    """系統狀態面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.groups = {}
        self._setup_ui()
        
    def _setup_ui(self):
        """設置UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 系統狀態群組
        self.add_group("system", "系統狀態")
        systems = {
            "atp": "ATP系統",
            "mmi": "MMI界面",
            "prs": "PRS通訊"
        }
        for name, label in systems.items():
            self.groups["system"].add_indicator(name, label)
            
        # 運行狀態群組
        self.add_group("operation", "運行狀態")
        operations = {
            "speed": "速度狀態",
            "brake": "煞車系統",
            "signal": "號誌狀態"
        }
        for name, label in operations.items():
            self.groups["operation"].add_indicator(name, label)
            
        # 添加群組到佈局
        for group in self.groups.values():
            layout.addWidget(group)
            
        self.setLayout(layout)
        
    def add_group(self, name: str, title: str) -> IndicatorGroup:
        """添加指示器群組"""
        group = IndicatorGroup(title, self)
        self.groups[name] = group
        return group
        
    def set_status(self, group: str, name: str, status: str, 
                   message: Optional[str] = None):
        """設置狀態"""
        if group in self.groups:
            self.groups[group].set_status(name, status, message)
            
    def clear_all(self):
        """清除所有狀態"""
        for group in self.groups.values():
            group.clear_all()
