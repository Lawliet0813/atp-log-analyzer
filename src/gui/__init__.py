"""ATP行車紀錄分析系統GUI套件"""

from .main_window import MainWindow
from .widgets import (
    SpeedGauge,
    EventIndicator, 
    LocationDisplay,
    TimeDisplay,
    ProgressBar
)
from .dialogs import (
    SpeedAnalysisDialog,
    EventAnalysisDialog,
    SettingsDialog,
    ATPSettingsDialog
)

# 版本資訊
__version__ = "1.0.0"

# 匯出類別
__all__ = [
    'MainWindow',
    'SpeedGauge',
    'EventIndicator',
    'LocationDisplay', 
    'TimeDisplay',
    'ProgressBar',
    'SpeedAnalysisDialog',
    'EventAnalysisDialog',
    'SettingsDialog',
    'ATPSettingsDialog'
]

# GUI全域設定
GUI_CONFIG = {
    # 主題顏色
    'THEME_COLORS': {
        'primary': '#2c3e50',    # 主色
        'secondary': '#34495e',  # 次要色
        'success': '#2ecc71',    # 成功色
        'warning': '#f39c12',    # 警告色
        'danger': '#e74c3c',     # 危險色
        'info': '#3498db',       # 資訊色
        'text': '#2c3e50',       # 文字色
        'background': '#ecf0f1', # 背景色
        'border': '#bdc3c7'      # 邊框色
    },
    
    # 字型設定
    'FONTS': {
        'title': ('Arial', 16, 'bold'),
        'text': ('Arial', 12),
        'small': ('Arial', 10),
        'monospace': ('Consolas', 12)
    },
    
    # 視窗大小
    'WINDOW_SIZE': {
        'main': (1200, 800),
        'dialog': (800, 600),
        'popup': (400, 300)
    },
    
    # 資料視覺化設定
    'PLOT_CONFIG': {
        'background': 'white',
        'foreground': 'black',
        'grid': True,
        'grid_color': '#95a5a6',
        'grid_alpha': 0.3,
        'line_width': 2
    },
    
    # 圖表顏色
    'CHART_COLORS': {
        'speed': '#2ecc71',
        'limit': '#e74c3c', 
        'signal': '#3498db',
        'warning': '#f39c12',
        'event': '#9b59b6'
    },
    
    # 圖示設定
    'ICONS': {
        'size': 24,
        'color': '#2c3e50'
    },
    
    # 動畫設定
    'ANIMATION': {
        'duration': 200,  # 毫秒
        'enabled': True
    }
}

# 警示訊息設定
ALERT_MESSAGES = {
    'ERROR': {
        'file_not_found': '找不到檔案',
        'invalid_file': '無效的檔案格式',
        'parse_error': '解析檔案失敗',
        'analysis_error': '分析資料失敗'
    },
    'WARNING': {
        'no_data': '無可用資料',
        'incomplete_data': '資料不完整',
        'outdated_data': '資料可能已過期'
    },
    'INFO': {
        'loading': '載入中...',
        'analyzing': '分析中...',
        'completed': '完成',
        'saved': '已儲存'
    }
}

# 快捷鍵設定
SHORTCUTS = {
    'GENERAL': {
        'open': 'Ctrl+O',
        'save': 'Ctrl+S',
        'exit': 'Ctrl+Q',
        'help': 'F1'
    },
    'ANALYSIS': {
        'start': 'F5',
        'stop': 'F6',
        'reset': 'F7'
    },
    'VIEW': {
        'zoom_in': 'Ctrl++',
        'zoom_out': 'Ctrl+-',
        'reset_zoom': 'Ctrl+0'
    }
}

# 視窗標題格式
WINDOW_TITLE_FORMAT = "ATP行車紀錄分析系統 - {filename} [{status}]"

# 匯出檔案格式
EXPORT_FORMATS = {
    'REPORT': ['XLSX', 'CSV', 'PDF'],
    'CHART': ['PNG', 'SVG', 'PDF'],
    'DATA': ['CSV', 'JSON']
}

def init_gui():
    """初始化GUI系統"""
    # TODO: 實作GUI初始化邏輯
    pass

def set_theme(theme_name: str):
    """設定GUI主題"""
    # TODO: 實作主題切換邏輯
    pass

def get_config(key: str):
    """取得GUI設定值"""
    return GUI_CONFIG.get(key)

def set_config(key: str, value):
    """設定GUI設定值"""
    GUI_CONFIG[key] = value
