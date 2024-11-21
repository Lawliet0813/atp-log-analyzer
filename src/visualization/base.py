# visualization/core/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
import pyqtgraph as pg

class Theme:
    """視覺化主題配置"""
    
    def __init__(self):
        # 顏色配置
        self.colors = {
            'background': '#2c3e50',
            'foreground': '#ecf0f1',
            'primary': '#3498db',
            'secondary': '#2ecc71',
            'warning': '#f1c40f',
            'danger': '#e74c3c',
            'grid': '#34495e',
            'text': '#2c3e50'
        }
        
        # 字型配置
        self.fonts = {
            'family': 'Arial',
            'sizes': {
                'small': 10,
                'normal': 12,
                'large': 14,
                'title': 16
            }
        }
        
        # 繪圖配置
        self.plot = {
            'line_width': 2,
            'grid_alpha': 0.3,
            'marker_size': 8,
            'padding': 0.1  # 軸範圍擴展比例
        }

class DataProcessor:
    """數據預處理工具"""
    
    @staticmethod
    def downsample(data: np.ndarray, target_points: int = 1000) -> np.ndarray:
        """降採樣數據點"""
        if len(data) <= target_points:
            return data
            
        # 使用平均值降採樣
        window_size = len(data) // target_points
        return np.array([
            data[i:i + window_size].mean() 
            for i in range(0, len(data), window_size)
        ])
    
    @staticmethod
    def smooth_data(data: np.ndarray, window: int = 5) -> np.ndarray:
        """平滑化數據"""
        kernel = np.ones(window) / window
        return np.convolve(data, kernel, mode='valid')
    
    @staticmethod
    def remove_outliers(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """移除異常值"""
        mean = np.mean(data)
        std = np.std(data)
        mask = np.abs(data - mean) <= threshold * std
        return data[mask]
    
    @staticmethod
    def interpolate_missing(data: np.ndarray) -> np.ndarray:
        """插值缺失值"""
        mask = np.isnan(data)
        if not mask.any():
            return data
            
        xp = np.arange(len(data))[~mask]
        fp = data[~mask]
        x = np.arange(len(data))
        return np.interp(x, xp, fp)

class BaseVisualization(QWidget):
    """視覺化基礎類別"""
    
    # 自定義信號
    data_updated = pyqtSignal()  # 數據更新信號
    selection_changed = pyqtSignal(object)  # 選擇變更信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = Theme()
        self.processor = DataProcessor()
        self.cache = {}  # 數據緩存
        self.view_range = None  # 視圖範圍
        self._setup_widget()
    
    def _setup_widget(self):
        """初始化Widget"""
        self.setMinimumSize(200, 150)
        self.preferred_size = (400, 300)
    
    def update_theme(self, theme: Theme):
        """更新主題"""
        self.theme = theme
        self._apply_theme()
    
    @abstractmethod
    def _apply_theme(self):
        """套用主題(由子類實作)"""
        pass
    
    def set_view_range(self, xmin: float, xmax: float):
        """設置視圖範圍"""
        self.view_range = (xmin, xmax)
        self._update_visible_data()
    
    def _update_visible_data(self):
        """更新可視數據(由子類實作)"""
        pass
    
    def clear_cache(self):
        """清除緩存"""
        self.cache.clear()
    
    def export_image(self, filename: str, format: str = 'png'):
        """匯出圖片"""
        pass

class BasePlotWidget(BaseVisualization):
    """基礎繪圖元件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot_widget = None
        self.layers = {}  # 圖層集合
        self._setup_plot()
    
    def _setup_plot(self):
        """設置繪圖元件"""
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(self.theme.colors['background'])
        self.plot_widget.showGrid(x=True, y=True, alpha=self.theme.plot['grid_alpha'])
    
    def add_layer(self, name: str, layer_type: str = 'line', **kwargs) -> Any:
        """添加圖層"""
        if layer_type == 'line':
            layer = self.plot_widget.plot(
                name=name,
                pen=pg.mkPen(
                    self.theme.colors.get(kwargs.get('color', 'primary')),
                    width=self.theme.plot['line_width']
                )
            )
        elif layer_type == 'scatter':
            layer = pg.ScatterPlotItem(
                symbol=kwargs.get('symbol', 'o'),
                size=kwargs.get('size', self.theme.plot['marker_size'])
            )
            self.plot_widget.addItem(layer)
            
        self.layers[name] = layer
        return layer
    
    def update_layer(self, name: str, data: Dict):
        """更新圖層數據"""
        if name in self.layers:
            self.layers[name].setData(**data)
    
    def remove_layer(self, name: str):
        """移除圖層"""
        if name in self.layers:
            self.plot_widget.removeItem(self.layers[name])
            del self.layers[name]
    
    def _apply_theme(self):
        """套用主題"""
        if self.plot_widget:
            self.plot_widget.setBackground(self.theme.colors['background'])
            
            # 更新座標軸樣式
            for axis in ['left', 'bottom']:
                ax = self.plot_widget.getAxis(axis)
                ax.setPen(self.theme.colors['foreground'])
                ax.setTextPen(self.theme.colors['foreground'])
            
            # 更新網格樣式
            self.plot_widget.getPlotItem().getViewBox().setBackgroundColor(
                self.theme.colors['background']
            )
            
    def set_labels(self, xlabel: str = None, ylabel: str = None, title: str = None):
        """設置標籤"""
        if xlabel:
            self.plot_widget.setLabel('bottom', xlabel)
        if ylabel:
            self.plot_widget.setLabel('left', ylabel)
        if title:
            self.plot_widget.setTitle(title)
            
    def enable_legend(self, **kwargs):
        """啟用圖例"""
        self.plot_widget.addLegend(**kwargs)
    
    def enable_crosshair(self):
        """啟用十字準線"""
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plot_widget.addItem(self.vLine, ignoreBounds=True)
        self.plot_widget.addItem(self.hLine, ignoreBounds=True)
        
        def mouseMoved(evt):
            pos = evt[0]
            if self.plot_widget.sceneBoundingRect().contains(pos):
                mousePoint = self.plot_widget.plotItem.vb.mapSceneToView(pos)
                self.vLine.setPos(mousePoint.x())
                self.hLine.setPos(mousePoint.y())
                
        self.plot_widget.scene().sigMouseMoved.connect(mouseMoved)
        
    def get_data_coords(self, event) -> Tuple[float, float]:
        """獲取數據座標"""
        pos = event.scenePos()
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            return mousePoint.x(), mousePoint.y()
        return None, None
