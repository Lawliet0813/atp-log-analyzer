from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
import pandas as pd

class ATPDataVisualizer:
    """ATP數據視覺化工具"""
    
    def __init__(self):
        # 設定視覺化主題顏色
        self.colors = {
            'speed': '#2ecc71',      # 速度曲線
            'limit': '#e74c3c',      # 速限線
            'warning': '#f39c12',    # 警告
            'critical': '#c0392b',   # 危急
            'normal': '#3498db',     # 正常
            'background': '#2c3e50', # 背景
            'grid': '#34495e'        # 網格
        }
        
        # 設定圖表樣式
        self.plot_config = {
            'background': 'k',
            'foreground': 'w',
            'grid_alpha': 0.5
        }
        
    def create_speed_plot(self) -> pg.PlotWidget:
        """創建速度曲線圖表"""
        plot = pg.PlotWidget()
        plot.setBackground(self.plot_config['background'])
        plot.showGrid(x=True, y=True, alpha=self.plot_config['grid_alpha'])
        
        # 設定座標軸
        plot.setLabel('left', '速度', units='km/h', color=self.plot_config['foreground'])
        plot.setLabel('bottom', '時間', color=self.plot_config['foreground'])
        
        return plot
        
    def plot_speed_profile(self, plot_widget: pg.PlotWidget,
                          times: List[datetime],
                          speeds: List[float],
                          speed_limits: List[float] = None):
        """繪製速度剖面圖"""
        # 清除現有圖形
        plot_widget.clear()
        
        # 轉換時間為相對秒數
        t0 = times[0].timestamp()
        x = [(t.timestamp() - t0) for t in times]
        
        # 繪製速度曲線
        plot_widget.plot(x, speeds, pen=pg.mkPen(self.colors['speed'], width=2),
                        name='列車速度')
                        
        # 繪製速限線
        if speed_limits:
            plot_widget.plot(x, speed_limits, pen=pg.mkPen(self.colors['limit'], 
                           width=2, style=Qt.PenStyle.DashLine),
                           name='速度限制')
                           
        # 更新X軸標籤格式
        def format_time(seconds):
            m, s = divmod(int(seconds), 60)
            h, m = divmod(m, 60)
            return f"{h:02d}:{m:02d}:{s:02d}"
            
        axis = plot_widget.getAxis('bottom')
        axis.setTicks([[(i, format_time(i)) for i in range(0, int(x[-1]), 300)]])

    def create_event_scatter_plot(self) -> pg.PlotWidget:
        """創建事件散點圖"""
        plot = pg.PlotWidget()
        plot.setBackground(self.plot_config['background'])
        plot.showGrid(x=True, y=True, alpha=self.plot_config['grid_alpha'])
        
        # 設定座標軸
        plot.setLabel('left', '事件類型')
        plot.setLabel('bottom', '時間')
        
        return plot
        
    def plot_events(self, plot_widget: pg.PlotWidget, events: List[Dict]):
        """繪製事件分布圖"""
        plot_widget.clear()
        
        # 準備數據
        event_types = sorted(set(e['type'] for e in events))
        type_to_y = {t: i for i, t in enumerate(event_types)}
        
        # 設定Y軸刻度
        axis = plot_widget.getAxis('left')
        axis.setTicks([[(i, t) for t, i in type_to_y.items()]])
        
        # 依事件等級設定顏色
        colors = {
            'CRITICAL': self.colors['critical'],
            'HIGH': self.colors['warning'],
            'MEDIUM': self.colors['warning'],
            'LOW': self.colors['normal'],
            'INFO': self.colors['normal']
        }
        
        # 繪製散點
        for event in events:
            x = event['timestamp'].timestamp()
            y = type_to_y[event['type']]
            color = colors.get(event['severity'], self.colors['normal'])
            
            # 添加點
            plot_widget.plot([x], [y], pen=None, 
                           symbol='o', symbolPen=None,
                           symbolBrush=color, symbolSize=10)

    def create_distribution_plot(self) -> pg.PlotWidget:
        """創建分布圖"""
        plot = pg.PlotWidget()
        plot.setBackground(self.plot_config['background'])
        plot.showGrid(x=True, y=True, alpha=self.plot_config['grid_alpha'])
        
        return plot
        
    def plot_speed_distribution(self, plot_widget: pg.PlotWidget, speeds: List[float]):
        """繪製速度分布直方圖"""
        plot_widget.clear()
        
        # 計算直方圖數據
        y, x = np.histogram(speeds, bins=50)
        
        # 繪製直方圖
        bar_graph = pg.BarGraphItem(x=x[:-1], height=y, width=1.0,
                                  brush=self.colors['normal'])
        plot_widget.addItem(bar_graph)
        
        # 設定標籤
        plot_widget.setLabel('left', '次數')
        plot_widget.setLabel('bottom', '速度 (km/h)')

    def create_multi_axis_plot(self) -> pg.PlotWidget:
        """創建多軸圖表"""
        plot = pg.PlotWidget()
        plot.setBackground(self.plot_config['background'])
        
        # 添加右側Y軸
        right_axis = pg.ViewBox()
        plot.scene().addItem(right_axis)
        plot.getAxis('right').linkToView(right_axis)
        right_axis.setXLink(plot)
        
        return plot, right_axis
        
    def create_heatmap(self, data: np.ndarray, x_labels: List[str], 
                      y_labels: List[str]) -> pg.ImageView:
        """創建熱力圖"""
        view = pg.ImageView()
        view.setImage(data)
        
        # 設定座標軸標籤
        x_axis = view.getView().getAxis('bottom')
        y_axis = view.getView().getAxis('left')
        
        x_axis.setTicks([[(i, label) for i, label in enumerate(x_labels)]])
        y_axis.setTicks([[(i, label) for i, label in enumerate(y_labels)]])
        
        return view

    def create_dashboard(self, parent=None) -> QWidget:
        """創建綜合儀表板"""
        dashboard = QWidget(parent)
        layout = QVBoxLayout()
        
        # 速度曲線
        self.speed_plot = self.create_speed_plot()
        layout.addWidget(self.speed_plot)
        
        # 事件分布
        self.event_plot = self.create_event_scatter_plot()
        layout.addWidget(self.event_plot)
        
        # 速度分布
        self.dist_plot = self.create_distribution_plot()
        layout.addWidget(self.dist_plot)
        
        dashboard.setLayout(layout)
        return dashboard
        
    def update_dashboard(self, data: Dict):
        """更新儀表板數據"""
        if 'speeds' in data and 'times' in data:
            self.plot_speed_profile(self.speed_plot, 
                                  data['times'],
                                  data['speeds'],
                                  data.get('limits'))
                                  
        if 'events' in data:
            self.plot_events(self.event_plot, data['events'])
            
        if 'speeds' in data:
            self.plot_speed_distribution(self.dist_plot, data['speeds'])
