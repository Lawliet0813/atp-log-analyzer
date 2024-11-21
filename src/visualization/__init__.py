# visualization/__init__.py

from .core.base import BaseVisualization, Theme
from .core.themes import ThemeManager
from .core.processors import (
    DataPreprocessor,
    SignalProcessor,
    EventProcessor,
    ProcessingConfig
)

from .plots.speed_plot import SpeedPlot
from .plots.event_plot import EventPlot
from .plots.gauge_plot import GaugePlot

from .widgets.dashboard import ATPDashboard
from .widgets.indicators import (
    StatusLight,
    StatusIndicator,
    IndicatorGroup,
    SystemStatusPanel
)

__version__ = "1.0.0"
__author__ = "ATP Team"

# 導出所有公開類和函數
__all__ = [
    # 基礎類別
    'BaseVisualization',
    'Theme',
    'ThemeManager',
    
    # 數據處理
    'DataPreprocessor',
    'SignalProcessor',
    'EventProcessor',
    'ProcessingConfig',
    
    # 圖表元件
    'SpeedPlot',
    'EventPlot',
    'GaugePlot',
    
    # 介面元件
    'ATPDashboard',
    'StatusLight',
    'StatusIndicator',
    'IndicatorGroup',
    'SystemStatusPanel'
]

# 初始化主題管理器
theme_manager = ThemeManager()

def get_theme_manager() -> ThemeManager:
    """獲取主題管理器實例"""
    return theme_manager

def set_global_theme(theme_name: str):
    """設置全局主題"""
    theme_manager.load_theme(theme_name)
