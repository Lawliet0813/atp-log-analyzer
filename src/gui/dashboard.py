#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QGroupBox, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from .widgets import SpeedGauge, EventIndicator, LocationDisplay, TimeDisplay
from visualization.atp_visualizer import ATPDataVisualizer
from analyzer.atp_analyzer import ATPAnalyzer

class DashboardWidget(QWidget):
    """ATP分析儀表板元件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = ATPAnalyzer()
        self.visualizer = ATPDataVisualizer()
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """設置使用者界面"""
        # 主佈局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 上方狀態列
        status_bar = self.create_status_bar()
        main_layout.addLayout(status_bar)
        
        # 中間主要內容
        content = QHBoxLayout()
        
        # 左側速度儀表與位置資訊
        left_panel = self.create_left_panel()
        content.addLayout(left_panel, stretch=1)
        
        # 中間速度曲線
        center_panel = self.create_center_panel()
        content.addLayout(center_panel, stretch=3)
        
        # 右側事件監控
        right_panel = self.create_right_panel()
        content.addLayout(right_panel, stretch=1)
        
        main_layout.addLayout(content)
        
        # 下方事件指示器
        event_bar = self.create_event_bar()
        main_layout.addLayout(event_bar)
        
    def create_status_bar(self) -> QHBoxLayout:
        """創建狀態列"""
        layout = QHBoxLayout()
        
        # 列車號
        self.train_label = QLabel("列車號: ---")
        self.train_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        layout.addWidget(self.train_label)
        
        # 時間顯示
        self.time_display = TimeDisplay()
        layout.addWidget(self.time_display)
        
        # 運行模式
        self.mode_label = QLabel("模式: 全監控")
        self.mode_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #27ae60;
            }
        """)
        layout.addWidget(self.mode_label)
        
        return layout
        
    def create_left_panel(self) -> QVBoxLayout:
        """創建左側面板"""
        layout = QVBoxLayout()
        
        # 速度儀表
        speed_group = QGroupBox("即時速度")
        speed_layout = QVBoxLayout()
        self.speed_gauge = SpeedGauge()
        speed_layout.addWidget(self.speed_gauge)
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # 位置資訊
        location_group = QGroupBox("位置資訊")
        location_layout = QVBoxLayout()
        self.location_display = LocationDisplay()
        location_layout.addWidget(self.location_display)
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        return layout
        
    def create_center_panel(self) -> QVBoxLayout:
        """創建中間面板"""
        layout = QVBoxLayout()
        
        # 速度曲線圖
        speed_group = QGroupBox("速度曲線")
        speed_layout = QVBoxLayout()
        self.speed_plot = self.visualizer.create_speed_plot()
        speed_layout.addWidget(self.speed_plot)
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # 事件分布圖
        event_group = QGroupBox("事件分布")
        event_layout = QVBoxLayout()
        self.event_plot = self.visualizer.create_event_scatter_plot()
        event_layout.addWidget(self.event_plot)
        event_group.setLayout(event_layout)
        layout.addWidget(event_group)
        
        return layout
        
    def create_right_panel(self) -> QVBoxLayout:
        """創建右側面板"""
        layout = QVBoxLayout()
        
        # ATP狀態監控
        status_group = QGroupBox("系統狀態")
        status_layout = QVBoxLayout()
        self.event_indicator = EventIndicator()
        status_layout.addWidget(self.event_indicator)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 關鍵統計資訊
        stats_group = QGroupBox("統計資訊")
        stats_layout = QGridLayout()
        
        # 添加統計標籤
        self.stats_labels = {
            'max_speed': QLabel("最高速度: ---"),
            'avg_speed': QLabel("平均速度: ---"),
            'distance': QLabel("行駛距離: ---"),
            'run_time': QLabel("運行時間: ---"),
            'over_speed': QLabel("超速次數: ---"),
            'emergency': QLabel("緊急煞車: ---")
        }
        
        row = 0
        for label in self.stats_labels.values():
            label.setStyleSheet("font-size: 12px;")
            stats_layout.addWidget(label, row, 0)
            row += 1
            
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        return layout
        
    def create_event_bar(self) -> QHBoxLayout:
        """創建事件指示列"""
        layout = QHBoxLayout()
        
        # ATP狀態
        self.atp_status = QLabel("ATP狀態: 正常")
        self.atp_status.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
        """)
        layout.addWidget(self.atp_status)
        
        # 煞車狀態
        self.brake_status = QLabel("煞車狀態: 正常")
        self.brake_status.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
        """)
        layout.addWidget(self.brake_status)
        
        # PRS狀態
        self.prs_status = QLabel("PRS狀態: 正常")
        self.prs_status.setStyleSheet("""
            QLabel {
                padding: 5px;
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
        """)
        layout.addWidget(self.prs_status)
        
        return layout
        
    def setup_timer(self):
        """設置更新計時器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(1000)  # 每秒更新一次
        
    def update_dashboard(self):
        """更新儀表板資料"""
        # 更新時間顯示
        current_time = datetime.now()
        self.time_display.set_time(current_time.strftime("%H:%M:%S"))
        
    def update_speed(self, speed: float):
        """更新速度顯示"""
        self.speed_gauge.set_speed(speed)
        
    def update_location(self, location: float, prev_station: str, next_station: str):
        """更新位置資訊"""
        self.location_display.set_location(location)
        self.location_display.set_stations(prev_station, next_station)
        
    def update_events(self, events: List[Dict]):
        """更新事件顯示"""
        # 更新事件指示器
        latest_events = events[-10:]  # 只顯示最新的10筆
        
        # 更新事件散點圖
        self.visualizer.plot_events(self.event_plot, latest_events)
        
        # 更新系統狀態
        for event in reversed(latest_events):
            if event['type'] == 'ATP':
                self.event_indicator.set_atp_status(event['description'], 
                                                  event['severity'] == 'CRITICAL')
            elif event['type'] == 'BRAKE':
                self.event_indicator.set_brake_status(event['description'],
                                                    event['severity'] == 'CRITICAL')
            elif event['type'] == 'PRS':
                self.event_indicator.set_prs_status(event['description'],
                                                  event['severity'] == 'CRITICAL')
                
    def update_statistics(self, stats: Dict):
        """更新統計資訊"""
        if not stats:
            return
            
        # 更新統計標籤
        if 'max_speed' in stats:
            self.stats_labels['max_speed'].setText(
                f"最高速度: {stats['max_speed']:.1f} km/h"
            )
        if 'avg_speed' in stats:
            self.stats_labels['avg_speed'].setText(
                f"平均速度: {stats['avg_speed']:.1f} km/h"
            )
        if 'distance' in stats:
            self.stats_labels['distance'].setText(
                f"行駛距離: {stats['distance']:.2f} km"
            )
        if 'run_time' in stats:
            self.stats_labels['run_time'].setText(
                f"運行時間: {stats['run_time']}"
            )
        if 'over_speed' in stats:
            self.stats_labels['over_speed'].setText(
                f"超速次數: {stats['over_speed']}"
            )
        if 'emergency' in stats:
            self.stats_labels['emergency'].setText(
                f"緊急煞車: {stats['emergency']}"
            )
            
    def set_train_info(self, train_no: str):
        """設置列車資訊"""
        self.train_label.setText(f"列車號: {train_no}")
        
    def set_mode(self, mode: str):
        """設置運行模式"""
        self.mode_label.setText(f"模式: {mode}")
        
        # 根據模式設置顏色
        if mode == "全監控":
            color = "#27ae60"
        elif mode == "目視行車":
            color = "#f39c12"
        elif mode == "系統隔離":
            color = "#c0392b"
        else:
            color = "#7f8c8d"
            
        self.mode_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {color};
            }}
        """)
