# visualization/plots/gauge_plot.py

from math import pi, sin, cos
from typing import Optional, Tuple
import numpy as np
from ..core.base import BaseVisualization
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QRadialGradient, QFont, QPainterPath

class GaugePlot(BaseVisualization):
    """優化的儀表板元件"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        # 速度相關屬性
        self.current_speed = 0.0
        self.target_speed = 0.0
        self.speed_limit = 90.0
        self.warning_threshold = 80.0
        
        # 視覺相關屬性
        self.min_speed = 0
        self.max_speed = 120
        self.major_ticks = 10  # 主刻度間隔
        self.minor_ticks = 2   # 副刻度間隔
        self.start_angle = 225  # 起始角度
        self.end_angle = -45   # 結束角度
        
        # 動畫相關屬性
        self.animation_duration = 200  # 毫秒
        self.animation_step = 0
        
        self._setup_gauge()
        
    def _setup_gauge(self):
        """設置儀表板"""
        # 設置最小尺寸
        self.setMinimumSize(200, 200)
        self.setSizePolicy(
            QWidget.SizePolicy.Expanding,
            QWidget.SizePolicy.Expanding
        )
        
    def _calculate_point(self, center: QPointF, radius: float, 
                        angle: float) -> QPointF:
        """計算角度對應的點座標"""
        x = center.x() + radius * cos(angle * pi / 180)
        y = center.y() + radius * sin(angle * pi / 180)
        return QPointF(x, y)
        
    def _speed_to_angle(self, speed: float) -> float:
        """將速度轉換為角度"""
        speed_range = self.max_speed - self.min_speed
        angle_range = self.end_angle - self.start_angle
        ratio = (speed - self.min_speed) / speed_range
        return self.start_angle + ratio * angle_range
        
    def paintEvent(self, event):
        """繪製儀表板"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 計算繪製區域
        width = self.width()
        height = self.height()
        size = min(width, height)
        center = QPointF(width/2, height/2)
        radius = size/2 * 0.8  # 留出邊距
        
        # 繪製外框
        self._draw_frame(painter, center, radius)
        
        # 繪製刻度
        self._draw_ticks(painter, center, radius)
        
        # 繪製警告區域
        self._draw_warning_zone(painter, center, radius)
        
        # 繪製當前速度指針
        self._draw_needle(painter, center, radius)
        
        # 繪製中心點
        self._draw_center(painter, center, radius)
        
        # 繪製數字顯示
        self._draw_speed_text(painter, center, radius)
        
    def _draw_frame(self, painter: QPainter, center: QPointF, radius: float):
        """繪製外框"""
        # 漸層背景
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(self.theme.colors['background']))
        gradient.setColorAt(1, QColor(self.theme.colors['grid']))
        painter.setBrush(gradient)
        
        # 外圈
        pen = QPen(QColor(self.theme.colors['foreground']), 2)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)
        
    def _draw_ticks(self, painter: QPainter, center: QPointF, radius: float):
        """繪製刻度"""
        # 主刻度
        major_pen = QPen(QColor(self.theme.colors['foreground']), 2)
        minor_pen = QPen(QColor(self.theme.colors['grid']), 1)
        text_pen = QPen(QColor(self.theme.colors['text']), 1)
        
        for speed in range(self.min_speed, self.max_speed + 1):
            angle = self._speed_to_angle(speed)
            
            # 主刻度
            if speed % self.major_ticks == 0:
                painter.setPen(major_pen)
                outer_point = self._calculate_point(center, radius, angle)
                inner_point = self._calculate_point(center, radius * 0.9, angle)
                painter.drawLine(outer_point, inner_point)
                
                # 刻度文字
                painter.setPen(text_pen)
                text_point = self._calculate_point(center, radius * 0.7, angle)
                painter.drawText(
                    QRectF(text_point.x() - 15, text_point.y() - 10, 30, 20),
                    Qt.AlignmentFlag.AlignCenter,
                    str(speed)
                )
            
            # 副刻度
            elif speed % self.minor_ticks == 0:
                painter.setPen(minor_pen)
                outer_point = self._calculate_point(center, radius, angle)
                inner_point = self._calculate_point(center, radius * 0.95, angle)
                painter.drawLine(outer_point, inner_point)
                
    def _draw_warning_zone(self, painter: QPainter, center: QPointF, radius: float):
        """繪製警告區域"""
        # 警告區域路徑
        warning_path = QPainterPath()
        warning_start = self._speed_to_angle(self.warning_threshold)
        warning_end = self._speed_to_angle(self.speed_limit)
        
        # 添加警告區域弧
        warning_rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2
        )
        warning_path.arcMoveTo(warning_rect, warning_start)
        warning_path.arcTo(warning_rect, warning_start, warning_end - warning_start)
        
        # 繪製警告區域
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.theme.colors['warning']))
        painter.setOpacity(0.3)
        painter.drawPath(warning_path)
        painter.setOpacity(1.0)
        
        # 繪製超速區域
        danger_path = QPainterPath()
        danger_start = self._speed_to_angle(self.speed_limit)
        danger_end = self._speed_to_angle(self.max_speed)
        
        danger_path.arcMoveTo(warning_rect, danger_start)
        danger_path.arcTo(warning_rect, danger_start, danger_end - danger_start)
        
        painter.setBrush(QColor(self.theme.colors['danger']))
        painter.setOpacity(0.3)
        painter.drawPath(danger_path)
        painter.setOpacity(1.0)
        
    def _draw_needle(self, painter: QPainter, center: QPointF, radius: float):
        """繪製指針"""
        angle = self._speed_to_angle(self.current_speed)
        
        # 建立指針路徑
        needle = QPainterPath()
        needle.moveTo(center)
        
        # 指針寬度
        width = radius * 0.05
        length = radius * 0.8
        
        # 計算指針頂點和兩側點
        tip = self._calculate_point(center, length, angle)
        left = self._calculate_point(center, width, angle + 90)
        right = self._calculate_point(center, width, angle - 90)
        
        # 繪製指針
        needle.lineTo(left)
        needle.lineTo(tip)
        needle.lineTo(right)
        needle.lineTo(center)
        
        # 設置指針顏色
        if self.current_speed > self.speed_limit:
            color = self.theme.colors['danger']
        elif self.current_speed > self.warning_threshold:
            color = self.theme.colors['warning']
        else:
            color = self.theme.colors['primary']
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        painter.drawPath(needle)
        
    def _draw_center(self, painter: QPainter, center: QPointF, radius: float):
        """繪製中心點"""
        # 中心圓
        center_radius = radius * 0.1
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self.theme.colors['foreground']))
        painter.drawEllipse(center, center_radius, center_radius)
        
        # 內圈
        inner_radius = center_radius * 0.7
        painter.setBrush(QColor(self.theme.colors['background']))
        painter.drawEllipse(center, inner_radius, inner_radius)
        
    def _draw_speed_text(self, painter: QPainter, center: QPointF, radius: float):
        """繪製速度文字"""
        # 設置字型
        font = QFont(self.theme.fonts['family'])
        font.setPixelSize(int(radius * 0.2))
        painter.setFont(font)
        
        # 繪製速度值
        speed_text = f"{self.current_speed:.1f}"
        text_rect = QRectF(
            center.x() - radius * 0.3,
            center.y() + radius * 0.2,
            radius * 0.6,
            radius * 0.3
        )
        painter.setPen(QColor(self.theme.colors['text']))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, speed_text)
        
        # 繪製單位
        font.setPixelSize(int(radius * 0.1))
        painter.setFont(font)
        unit_rect = QRectF(
            text_rect.x(),
            text_rect.bottom(),
            text_rect.width(),
            radius * 0.15
        )
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, "km/h")
        
    def set_speed(self, speed: float):
        """設置當前速度"""
        self.target_speed = max(self.min_speed, min(speed, self.max_speed))
        self._start_animation()
        
    def set_limits(self, warning: float, limit: float):
        """設置速度限制"""
        self.warning_threshold = warning
        self.speed_limit = limit
        self.update()
        
    def _start_animation(self):
        """開始速度動畫"""
        if hasattr(self, '_animation_timer'):
            self._animation_timer.stop()
            
        speed_diff = self.target_speed - self.current_speed
        if abs(speed_diff) < 0.1:
            self.current_speed = self.target_speed
            self.update()
            return
            
        self.animation_step = speed_diff / (self.animation_duration / 16)  # 60fps
        
        from PyQt6.QtCore import QTimer
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_timer.start(16)
        
    def _update_animation(self):
        """更新動畫"""
        if abs(self.current_speed - self.target_speed) < abs(self.animation_step):
            self.current_speed = self.target_speed
            self._animation_timer.stop()
        else:
            self.current_speed += self.animation_step
            
        self.update()
        
    def sizeHint(self) -> Tuple[int, int]:
        """建議尺寸"""
        return (300, 300)
        
    def minimumSizeHint(self) -> Tuple[int, int]:
        """最小尺寸"""
        return (200, 200)
