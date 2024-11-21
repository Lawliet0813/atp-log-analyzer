# visualization/widgets/dashboard.py

from typing import Dict, List, Optional
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                           QGroupBox, QLabel, QGridLayout)
from PyQt6.QtCore import pyqtSignal
from ..plots.speed_plot import SpeedPlot
from ..plots.event_plot import EventPlot
from ..plots.gauge_plot import GaugePlot
from ..core.base import Theme

class ATPDashboard(QWidget):
    """ATP儀表板整合組件"""
    
    # 自定義信號
    status_changed = pyqtSignal(str, str)  # 狀態變更信號(類型, 狀態)
    alert_triggered = pyqtSignal(str, str)  # 警報觸發信號(類型, 訊息)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = Theme()
        self._setup_ui()
        self._setup_connections()
        
    def _setup_ui(self):
        """設置UI"""
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        
        # 速度儀表組
        speed_group = QGroupBox("速度監控")
        speed_layout = QHBoxLayout()
        
        # 速度儀表
        self.speed_gauge = GaugePlot()
        speed_layout.addWidget(self.speed_gauge)
        
        # 速度狀態
        speed_status = QWidget()
        status_layout = QVBoxLayout()
        self.speed_label = QLabel("當前速度: 0 km/h")
        self.limit_label = QLabel("速限: 90 km/h")
        status_layout.addWidget(self.speed_label)
        status_layout.addWidget(self.limit_label)
        speed_status.setLayout(status_layout)
        speed_layout.addWidget(speed_status)
        
        speed_group.setLayout(speed_layout)
        main_layout.addWidget(speed_group, 0, 0)
        
        # 速度曲線圖
        speed_plot_group = QGroupBox("速度曲線")
        speed_plot_layout = QVBoxLayout()
        self.speed_plot = SpeedPlot()
        speed_plot_layout.addWidget(self.speed_plot)
        speed_plot_group.setLayout(speed_plot_layout)
        main_layout.addWidget(speed_plot_group, 1, 0, 1, 2)
        
        # 事件監控
        event_group = QGroupBox("事件監控")
        event_layout = QVBoxLayout()
        self.event_plot = EventPlot()
        event_layout.addWidget(self.event_plot)
        event_group.setLayout(event_layout)
        main_layout.addWidget(event_group, 0, 1)
        
        # 設置欄位比例
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        main_layout.setRowStretch(0, 1)
        main_layout.setRowStretch(1, 2)
        
    def _setup_connections(self):
        """設置信號連接"""
        # 速度超限警報
        self.speed_plot.speed_threshold_crossed.connect(
            lambda speed, time: self.alert_triggered.emit(
                'speed_limit',
                f'速度超限: {speed:.1f} km/h at {time}'
            )
        )
        
        # 緊急煞車警報
        self.speed_plot.emergency_brake_detected.connect(
            lambda speed, time: self.alert_triggered.emit(
                'emergency_brake',
                f'緊急煞車: {speed:.1f} km/h at {time}'
            )
        )
        
        # 事件選中
        self.event_plot.event_selected.connect(self._on_event_selected)
        
    def update_speed_data(self, times: List[datetime], speeds: List[float],
                         events: Optional[List[Dict]] = None):
        """更新速度數據"""
        # 更新即時速度
        current_speed = speeds[-1] if speeds else 0
        self.speed_gauge.set_speed(current_speed)
        self.speed_label.setText(f"當前速度: {current_speed:.1f} km/h")
        
        # 更新速度曲線
        self.speed_plot.update_speed_data(times, speeds, events)
        
        # 觸發狀態信號
        if current_speed > self.speed_gauge.speed_limit:
            self.status_changed.emit('speed', 'over_limit')
        elif current_speed > self.speed_gauge.warning_threshold:
            self.status_changed.emit('speed', 'warning')
        else:
            self.status_changed.emit('speed', 'normal')
            
    def update_events(self, events: List[Dict]):
        """更新事件數據"""
        self.event_plot.update_events(events)
        
        # 檢查嚴重事件
        critical_events = [
            e for e in events
            if e.get('severity') == 'CRITICAL'
        ]
        if critical_events:
            self.status_changed.emit('event', 'critical')
            self.alert_triggered.emit(
                'critical_event',
                f'發生{len(critical_events)}件嚴重事件'
            )
            
    def set_speed_limits(self, warning: float, limit: float):
        """設置速度限制"""
        self.speed_gauge.set_limits(warning, limit)
        self.speed_plot.set_speed_limit(limit)
        self.limit_label.setText(f"速限: {limit} km/h")
        
    def filter_events(self, severity: Optional[str] = None,
                     event_type: Optional[str] = None):
        """過濾事件"""
        self.event_plot.filter_events(severity, event_type)
        
    def _on_event_selected(self, event: Dict):
        """事件選中處理"""
        # 在速度曲線上標記對應時間點
        if 'time' in event and 'speed' in event:
            self.speed_plot.mark_point(event['time'], event['speed'])
            
        # 觸發狀態信號
        self.status_changed.emit(
            'selection',
            f"選中事件: {event.get('description', event['type'])}"
        )
        
    def clear_data(self):
        """清除數據"""
        self.speed_gauge.set_speed(0)
        self.speed_plot.clear_data()
        self.event_plot.clear_data()
        self.speed_label.setText("當前速度: 0 km/h")
        
    def export_analysis(self) -> Dict:
        """匯出分析結果"""
        return {
            'speed_analysis': self.speed_plot.export_analysis(),
            'event_statistics': self.event_plot.get_event_statistics()
        }
        
    def update_theme(self, theme: Theme):
        """更新主題"""
        self.theme = theme
        self.speed_gauge.update_theme(theme)
        self.speed_plot.update_theme(theme)
        self.event_plot.update_theme(theme)
        
        # 更新群組框樣式
        style = f"""
            QGroupBox {{
                border: 2px solid {theme.colors['border']};
                border-radius: 5px;
                margin-top: 1ex;
                font-size: {theme.fonts['sizes']['large']}px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                color: {theme.colors['text']};
            }}
        """
        for group in self.findChildren(QGroupBox):
            group.setStyleSheet(style)
