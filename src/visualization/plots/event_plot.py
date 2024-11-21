# visualization/plots/event_plot.py

from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from ..core.base import BasePlotWidget
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor

class EventPlot(BasePlotWidget):
    """優化的事件分布圖元件"""
    
    # 自定義信號
    event_selected = pyqtSignal(dict)  # 事件選中信號
    
    # 事件嚴重程度對應顏色
    SEVERITY_COLORS = {
        'CRITICAL': '#e74c3c',  # 紅色
        'HIGH': '#f39c12',      # 橙色
        'MEDIUM': '#f1c40f',    # 黃色
        'LOW': '#3498db',       # 藍色
        'INFO': '#2ecc71'       # 綠色
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_types = set()  # 事件類型集合
        self.selected_event = None
        self._setup_event_plot()
        self._setup_interactions()
        
    def _setup_event_plot(self):
        """設置事件圖"""
        # 建立事件散點圖層
        self.events_scatter = self.add_layer(
            'events', 'scatter',
            symbol='o'
        )
        
        # 建立事件連線圖層
        self.events_lines = self.add_layer(
            'lines', 'line',
            color='grid'
        )
        
        # 建立選中事件標記圖層
        self.selection_marker = self.add_layer(
            'selection', 'scatter',
            symbol='s',
            size=15
        )
        
        # 設置座標軸
        self.set_labels(
            xlabel='時間',
            ylabel='事件類型',
            title='ATP事件分布圖'
        )
        
    def _setup_interactions(self):
        """設置互動功能"""
        # 事件點擊處理
        def on_event_clicked(plot, points):
            if len(points) > 0:
                point = points[0]
                event_data = point.data()
                self.select_event(event_data)
                self.event_selected.emit(event_data)
                
        self.events_scatter.sigClicked.connect(on_event_clicked)
        
    def update_events(self, events: List[Dict]):
        """更新事件數據"""
        if not events:
            return
            
        # 更新事件類型集合
        self.event_types = sorted(set(e['type'] for e in events))
        type_to_y = {t: i for i, t in enumerate(self.event_types)}
        
        # 準備散點數據
        times = []
        y_pos = []
        colors = []
        symbols = []
        event_data = []
        
        t0 = events[0]['time']  # 參考時間點
        
        for event in events:
            rel_time = (event['time'] - t0).total_seconds()
            times.append(rel_time)
            y_pos.append(type_to_y[event['type']])
            
            # 設置顏色
            color = QColor(self.SEVERITY_COLORS.get(
                event.get('severity', 'INFO')
            ))
            colors.append(color)
            
            # 設置符號
            symbol = 'o'  # 預設圓形
            if event.get('type') == 'emergency_brake':
                symbol = 'x'
            elif event.get('type') == 'atp_failure':
                symbol = 's'
            symbols.append(symbol)
            
            # 儲存事件資料
            event_data.append({
                'time': event['time'],
                'type': event['type'],
                'severity': event.get('severity', 'INFO'),
                'description': event.get('description', ''),
                'rel_time': rel_time,
                'y_pos': type_to_y[event['type']]
            })
            
        # 更新散點圖層
        self.update_layer('events', {
            'x': times,
            'y': y_pos,
            'symbol': symbols,
            'brush': colors,
            'data': event_data
        })
        
        # 更新連線(用於顯示事件順序)
        self.update_layer('lines', {
            'x': times,
            'y': y_pos,
            'pen': pg.mkPen(
                self.theme.colors['grid'],
                width=1,
                style=pg.QtCore.Qt.PenStyle.DotLine
            )
        })
        
        # 設置Y軸刻度
        axis = self.plot_widget.getAxis('left')
        axis.setTicks([[(i, t) for t, i in type_to_y.items()]])
        
        # 設置合適的視圖範圍
        self.plot_widget.setXRange(
            min(times),
            max(times),
            padding=self.theme.plot['padding']
        )
        self.plot_widget.setYRange(
            -0.5,
            len(self.event_types) - 0.5,
            padding=self.theme.plot['padding']
        )
        
    def select_event(self, event_data: Dict):
        """選中事件"""
        self.selected_event = event_data
        
        # 更新選中標記
        self.update_layer('selection', {
            'x': [event_data['rel_time']],
            'y': [event_data['y_pos']],
            'brush': pg.mkBrush(self.theme.colors['primary'])
        })
        
    def clear_selection(self):
        """清除選中"""
        self.selected_event = None
        self.update_layer('selection', {'x': [], 'y': []})
        
    def filter_events(self, severity: Optional[str] = None,
                     event_type: Optional[str] = None):
        """過濾事件"""
        if not self.events_scatter.data:
            return
            
        visible_mask = np.ones(len(self.events_scatter.data), dtype=bool)
        
        if severity:
            severity_mask = [
                d['severity'] == severity
                for d in self.events_scatter.data
            ]
            visible_mask &= np.array(severity_mask)
            
        if event_type:
            type_mask = [
                d['type'] == event_type
                for d in self.events_scatter.data
            ]
            visible_mask &= np.array(type_mask)
            
        # 更新點的可見性
        self.events_scatter.setPointsVisible(visible_mask)
        
    def get_event_statistics(self) -> Dict:
        """獲取事件統計資訊"""
        if not self.events_scatter.data:
            return {}
            
        stats = {
            'total_events': len(self.events_scatter.data),
            'by_type': {},
            'by_severity': {},
            'time_distribution': {}
        }
        
        for event in self.events_scatter.data:
            # 按類型統計
            event_type = event['type']
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1
            
            # 按嚴重程度統計
            severity = event['severity']
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # 按時間分布統計(每小時)
            hour = event['time'].hour
            stats['time_distribution'][hour] = stats['time_distribution'].get(hour, 0) + 1
            
        return stats
