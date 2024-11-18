from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
import pyqtgraph as pg
import numpy as np

class SpeedGauge(QWidget):
    """速度儀表元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_speed = 0
        self.speed_limit = 90
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 速度顯示
        self.speed_label = QLabel("0")
        self.speed_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.speed_label)
        
        # 單位顯示
        unit_label = QLabel("km/h")
        unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(unit_label)
        
    def set_speed(self, speed: float):
        """設置當前速度"""
        self.current_speed = speed
        self.speed_label.setText(f"{speed:.1f}")
        
        # 根據速度設置顏色
        if speed > self.speed_limit:
            self.speed_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #e74c3c;
                }
            """)
        else:
            self.speed_label.setStyleSheet("""
                QLabel {
                    font-size: 48px;
                    font-weight: bold;
                    color: #2c3e50;
                }
            """)
        
    def set_limit(self, limit: float):
        """設置速度限制"""
        self.speed_limit = limit
        self.set_speed(self.current_speed)  # 更新顯示

class EventIndicator(QWidget):
    """事件指示元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # ATP狀態指示
        self.atp_indicator = QLabel("ATP正常")
        self.atp_indicator.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
        """)
        layout.addWidget(self.atp_indicator)
        
        # 緊急煞車指示
        self.brake_indicator = QLabel("煞車正常")
        self.brake_indicator.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
        """)
        layout.addWidget(self.brake_indicator)
        
        # PRS狀態指示
        self.prs_indicator = QLabel("PRS正常")
        self.prs_indicator.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
        """)
        layout.addWidget(self.prs_indicator)
        
    def set_atp_status(self, status: str, is_error: bool = False):
        """設置ATP狀態"""
        self.atp_indicator.setText(status)
        self.atp_indicator.setStyleSheet(f"""
            QLabel {{
                padding: 5px;
                border-radius: 3px;
                background-color: {"#e74c3c" if is_error else "#2ecc71"};
                color: white;
            }}
        """)
        
    def set_brake_status(self, status: str, is_active: bool = False):
        """設置煞車狀態"""
        self.brake_indicator.setText(status)
        self.brake_indicator.setStyleSheet(f"""
            QLabel {{
                padding: 5px;
                border-radius: 3px;
                background-color: {"#f39c12" if is_active else "#2ecc71"};
                color: white;
            }}
        """)
        
    def set_prs_status(self, status: str, is_error: bool = False):
        """設置PRS狀態"""
        self.prs_indicator.setText(status)
        self.prs_indicator.setStyleSheet(f"""
            QLabel {{
                padding: 5px;
                border-radius: 3px;
                background-color: {"#e74c3c" if is_error else "#2ecc71"};
                color: white;
            }}
        """)

class LocationDisplay(QWidget):
    """位置顯示元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 當前位置
        location_frame = QFrame()
        location_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        location_layout = QHBoxLayout()
        
        location_layout.addWidget(QLabel("當前位置:"))
        self.location_label = QLabel("0.000")
        self.location_label.setStyleSheet("font-weight: bold;")
        location_layout.addWidget(self.location_label)
        location_layout.addWidget(QLabel("km"))
        
        location_frame.setLayout(location_layout)
        layout.addWidget(location_frame)
        
        # 上一站/下一站
        station_frame = QFrame()
        station_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        station_layout = QHBoxLayout()
        
        self.prev_station = QLabel("---")
        self.next_station = QLabel("---")
        
        station_layout.addWidget(QLabel("上一站:"))
        station_layout.addWidget(self.prev_station)
        station_layout.addWidget(QLabel("下一站:"))
        station_layout.addWidget(self.next_station)
        
        station_frame.setLayout(station_layout)
        layout.addWidget(station_frame)
        
    def set_location(self, location: float):
        """設置當前位置"""
        self.location_label.setText(f"{location:.3f}")
        
    def set_stations(self, prev: str, next: str):
        """設置站點資訊"""
        self.prev_station.setText(prev)
        self.next_station.setText(next)

class TimeDisplay(QWidget):
    """時間顯示元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # 系統時間
        self.sys_time = QLabel()
        self.sys_time.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        layout.addWidget(self.sys_time)
        
        # 相對時間
        self.rel_time = QLabel()
        self.rel_time.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(self.rel_time)
        
    def set_time(self, sys_time: str, rel_time: str = None):
        """設置時間"""
        self.sys_time.setText(sys_time)
        if rel_time:
            self.rel_time.setText(f"(+{rel_time})")
        else:
            self.rel_time.clear()

class ProgressBar(QWidget):
    """進度條元件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.progress = 0
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 進度條
        self.progress_frame = QFrame()
        self.progress_frame.setMinimumWidth(200)
        self.progress_frame.setFixedHeight(20)
        self.progress_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #ecf0f1;
            }
        """)
        layout.addWidget(self.progress_frame)
        
        # 進度文字
        self.label = QLabel("0%")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
    def set_progress(self, value: int):
        """設置進度值(0-100)"""
        self.progress = max(0, min(100, value))
        self.label.setText(f"{self.progress}%")
        
        # 更新進度條顏色
        color = "#3498db"  # 基本藍色
        if self.progress > 90:
            color = "#2ecc71"  # 綠色
        elif self.progress > 75:
            color = "#f1c40f"  # 黃色
            
        width = int(self.progress_frame.width() * self.progress / 100)
        self.progress_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #ecf0f1;
            }}
            QFrame::after {{
                content: "";
                position: absolute;
                left: 0;
                top: 0;
                width: {width}px;
                height: 100%;
                background-color: {color};
                border-radius: 8px;
            }}
        """)
        
    def paintEvent(self, event):
        """重繪進度條"""
        super().paintEvent(event)
        width = int(self.progress_frame.width() * self.progress / 100)
        self.progress_frame.setFixedWidth(width)
