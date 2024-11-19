"""ATP行車記錄分析器套件"""

from .atp_analyzer import ATPAnalyzer, AnalysisResult

# 速度相關常數定義
SPEED_THRESHOLDS = {
    'EMERGENCY': 115,  # 緊急煞車門檻(km/h)
    'WARNING': 90,     # 警告門檻(km/h)
    'NORMAL': 80,      # 一般運行速度(km/h)
    'SHUNTING': 25,    # 調車速度(km/h)
    'APPROACH': 40,    # 接近速度(km/h)
    'RELEASE': 25,     # 解速限速度(km/h)
}

# 加速度閾值定義(m/s^2)
ACCELERATION_THRESHOLDS = {
    'MAX_ACC': 1.0,   # 最大加速度
    'MAX_DEC': -1.0,  # 最大減速度
    'NORMAL_ACC': 0.8,# 正常加速度
    'NORMAL_DEC': -0.8# 正常減速度
}

# 事件分析等級定義
EVENT_SEVERITY = {
    'CRITICAL': 1,    # 危急 
    'HIGH': 2,        # 高度警示
    'MEDIUM': 3,      # 中度警示
    'LOW': 4,         # 低度警示
    'INFO': 5         # 一般資訊
}

# ATP事件分析類型
ATP_EVENT_CATEGORIES = {
    'SPEED': {        # 速度相關事件
        'OVER_SPEED': 'CRITICAL',           # 超速 
        'APPROACH_LIMIT': 'HIGH',           # 接近速限
        'ACCELERATION_WARNING': 'MEDIUM',    # 加速警告
        'SPEED_VARIATION': 'LOW'            # 速度變化
    },
    'BRAKE': {        # 煞車相關事件 
        'EMERGENCY_BRAKE': 'CRITICAL',      # 緊急煞車
        'SERVICE_BRAKE': 'HIGH',            # 常用煞車
        'BRAKE_TEST': 'INFO',               # 煞車測試
        'BRAKE_RELEASE': 'INFO'             # 煞車解除
    },
    'SYSTEM': {       # 系統相關事件
        'ATP_FAILURE': 'CRITICAL',          # ATP故障
        'MMI_FAILURE': 'HIGH',              # MMI故障
        'COMMUNICATION_ERROR': 'HIGH',       # 通訊異常
        'SYSTEM_STARTUP': 'INFO'            # 系統啟動
    },
    'OPERATION': {    # 操作相關事件
        'ISOLATION': 'CRITICAL',            # ATP隔離
        'MODE_CHANGE': 'HIGH',              # 模式切換
        'PARAMETER_CHANGE': 'MEDIUM',        # 參數變更
        'DRIVER_INPUT': 'LOW'               # 駕駛輸入
    }
}

# 分析報告類型定義
REPORT_TYPES = {
    'SUMMARY': 1,     # 摘要報告
    'DETAILED': 2,    # 詳細報告
    'EVENT': 3,       # 事件報告
    'SPEED': 4,       # 速度報告
    'OPERATION': 5    # 操作報告
}

# 資料分析參數設定
ANALYSIS_PARAMS = {
    'SAMPLING_RATE': 10,          # 取樣率(Hz)
    'WINDOW_SIZE': 60,            # 分析視窗大小(秒)
    'MOVING_AVERAGE': 5,          # 移動平均點數
    'EVENT_THRESHOLD': 0.1,       # 事件觸發閾值
    'MIN_EVENT_DURATION': 2.0,    # 最小事件持續時間(秒)
    'MAX_DATA_GAP': 5.0          # 最大資料間隔(秒)
}

class AnalyzerError(Exception):
    """分析器異常基礎類別"""
    pass

class DataValidationError(AnalyzerError):
    """資料驗證錯誤"""
    pass

class AnalysisError(AnalyzerError):
    """分析處理錯誤"""
    pass

class ReportGenerationError(AnalyzerError):
    """報告產製錯誤"""
    pass

__version__ = "1.0.0"
__author__ = "陳彥儒"
__all__ = [
    'ATPAnalyzer',
    'AnalysisResult',
    'AnalyzerError',
    'DataValidationError', 
    'AnalysisError',
    'ReportGenerationError',
    'SPEED_THRESHOLDS',
    'ACCELERATION_THRESHOLDS',
    'EVENT_SEVERITY',
    'ATP_EVENT_CATEGORIES',
    'REPORT_TYPES',
    'ANALYSIS_PARAMS'
]
