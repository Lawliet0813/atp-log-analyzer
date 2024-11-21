# visualization/plots/speed_plot.py

from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from ..core.base import BasePlotWidget, Theme
from PyQt6.QtCore import pyqtSignal

class SpeedPlot(BasePlotWidget):
    """優化的速度曲線圖元件"""
    
    # 自定義信號
    speed_threshold_crossed = pyqtSignal(float, float)  # 超速信號(速度, 時間點)
    emergency_brake_detected = pyqtSignal(float, float) # 緊急煞車信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.speed_limit = 90.0  # 速限預設值
        self.warning_threshold = 80.0  # 警告預設值
        self._setup_speed_plot()
        self._setup_interactions()
        
    def _setup_speed_plot(self):
        """設置速度圖"""
        # 基本圖層
        self.speed_curve = self.add_layer(
            'speed', 'line',
            color='primary'
        )
        self.limit_line = self.add_layer(
            'limit', 'line',
            color='danger'
        )
        self.warning_line = self.add_layer(
            'warning', 'line',
            color='warning'
        )
        
        # 事件標記圖層
        self.event_markers = self.add_layer(
            'events', 'scatter',
            color='secondary'
        )
        
        # 設置座標軸
        self.set_labels(
            xlabel='時間',
            ylabel='速度 (km/h)',
            title='列車速度曲線'
        )
        
        # 啟用圖例
        self.enable_legend()
        
        # 啟用十字準線
        self.enable_crosshair()
        
    def _setup_interactions(self):
        """設置互動功能"""
        # 滑鼠移動事件
        def on_mouse_moved(evt):
            x, y = self.get_data_coords(evt)
            if x is not None and y is not None:
                # 檢查是否超速
                if y > self.speed_limit:
                    self.speed_threshold_crossed.emit(y, x)
                    
        self.plot_widget.scene().sigMouseMoved.connect(on_mouse_moved)
        
    def update_speed_data(self, 
                         times: List[datetime],
                         speeds: List[float],
                         events: Optional[List[Dict]] = None):
        """更新速度數據"""
        if not times or not speeds:
            return
            
        # 數據預處理
        t0 = times[0]
        rel_times = [(t - t0).total_seconds() for t in times]
        
        # 降採樣(如果數據點過多)
        if len(speeds) > 1000:
            rel_times = self.processor.downsample(np.array(rel_times))
            speeds = self.processor.downsample(np.array(speeds))
            
        # 平滑化處理
        smoothed_speeds = self.processor.smooth_data(np.array(speeds))
        
        # 更新速度曲線
        self.update_layer('speed', {
            'x': rel_times[:len(smoothed_speeds)],
            'y': smoothed_speeds,
            'name': '實際速度'
        })
        
        # 更新速限線
        self.update_layer('limit', {
            'x': [rel_times[0], rel_times[-1]],
            'y': [self.speed_limit, self.speed_limit],
            'name': '速度限制'
        })
        
        # 更新警告線
        self.update_layer('warning', {
            'x': [rel_times[0], rel_times[-1]],
            'y': [self.warning_threshold, self.warning_threshold],
            'name': '警告線'
        })
        
        # 更新事件標記
        if events:
            event_times = []
            event_speeds = []
            for event in events:
                if event['type'] in ['emergency_brake', 'over_speed']:
                    t = (event['time'] - t0).total_seconds()
                    event_times.append(t)
                    event_speeds.append(event['speed'])
                    
            self.update_layer('events', {
                'x': event_times,
                'y': event_speeds,
                'symbol': 'x' if event['type'] == 'emergency_brake' else 'o'
            })
            
        # 設置適當的視圖範圍
        self.plot_widget.setXRange(
            rel_times[0],
            rel_times[-1],
            padding=self.theme.plot['padding']
        )
        
        max_speed = max(speeds) * (1 + self.theme.plot['padding'])
        self.plot_widget.setYRange(0, max_speed)
        
    def set_speed_limit(self, limit: float):
        """設置速度限制"""
        self.speed_limit = limit
        # 更新速限線(如果已有數據)
        if 'limit' in self.layers:
            xrange = self.plot_widget.getViewBox().viewRange()[0]
            self.update_layer('limit', {
                'x': xrange,
                'y': [limit, limit]
            })
            
    def set_warning_threshold(self, threshold: float):
        """設置警告閾值"""
        self.warning_threshold = threshold
        # 更新警告線(如果已有數據)
        if 'warning' in self.layers:
            xrange = self.plot_widget.getViewBox().viewRange()[0]
            self.update_layer('warning', {
                'x': xrange,
                'y': [threshold, threshold]
            })
            
    def enable_speed_analysis(self):
        """啟用速度分析功能"""
        # 添加統計信息圖層
        self.add_layer(
            'stats', 'scatter',
            symbol='s',
            color='secondary'
        )
        
        # 計算並顯示關鍵統計點
        def update_stats():
            if 'speed' not in self.layers:
                return
                
            speed_data = self.layers['speed'].yData
            if speed_data is None:
                return
                
            # 計算統計值
            mean_speed = np.mean(speed_data)
            std_speed = np.std(speed_data)
            max_speed = np.max(speed_data)
            min_speed = np.min(speed_data)
            
            # 更新統計點
            x_pos = self.plot_widget.getViewBox().viewRange()[0][0]
            self.update_layer('stats', {
                'x': [x_pos] * 4,
                'y': [mean_speed, mean_speed + std_speed, 
                      max_speed, min_speed],
                'symbol': ['t', 's', 'p', 'n'],
                'brush': pg.mkBrush(self.theme.colors['secondary'])
            })
            
        # 連接到視圖更新信號
        self.plot_widget.sigRangeChanged.connect(update_stats)
        
    def export_analysis(self) -> Dict:
        """匯出分析結果"""
        if 'speed' not in self.layers:
            return {}
            
        speed_data = self.layers['speed'].yData
        if speed_data is None:
            return {}
            
        return {
            'max_speed': float(np.max(speed_data)),
            'min_speed': float(np.min(speed_data)),
            'avg_speed': float(np.mean(speed_data)),
            'std_speed': float(np.std(speed_data)),
            'over_speed_count': int(np.sum(speed_data > self.speed_limit)),
            'warning_count': int(np.sum(speed_data > self.warning_threshold)),
            'total_points': len(speed_data)
        }
