# src/analyzer/__init__.py

"""ATP行車記錄分析器套件

此套件提供ATP(Automatic Train Protection)行車記錄的分析功能，
包括速度分析、事件分析、位置分析等功能。

主要模組：
- atp_analyzer: 主要分析器類別
- processors: 資料處理器
- validators: 資料驗證器
- models: 資料模型
- exceptions: 異常處理
- exporters: 報表匯出器
- config: 配置管理
- utils: 工具函數
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from .atp_analyzer import ATPAnalyzer
from .models import (
    RURecord,
    SpeedProfile,
    EventRecord, 
    StationRecord,
    AnalysisResult,
    AnalysisConfig
)
from .exceptions import (
    ATPAnalyzerError,
    DataValidationError,
    ProcessingError,
    AnalysisError,
    ConfigError,
    ExportError
)
from .config import Config

# 版本資訊
__version__ = "1.0.0"
__author__ = "陳彥儒"
__license__ = "MIT"
__description__ = "ATP行車記錄分析器"

# 配置系統日誌
logger = logging.getLogger(__name__)

def setup_logging(log_file: Optional[str] = None,
                 log_level: str = 'INFO'):
    """設定日誌系統
    
    Args:
        log_file: 日誌檔案路徑(可選)
        log_level: 日誌等級(DEBUG/INFO/WARNING/ERROR/CRITICAL)
    """
    # 設定日誌格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 設定控制台輸出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 設定根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # 如果指定了日誌檔案，則添加檔案處理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
    logger.info(f"日誌系統已初始化: level={log_level}, file={log_file}")

def create_analyzer(config: Optional[Dict[str, Any]] = None) -> ATPAnalyzer:
    """建立分析器實例
    
    Args:
        config: 分析器配置(可選)
        
    Returns:
        ATPAnalyzer: 分析器實例
    """
    return ATPAnalyzer(config)

# ATP事件類型定義
ATP_EVENT_TYPES = {
    2: "ATP狀態變更",
    3: "MMI狀態變更",
    91: "PRS事件",
    201: "ATP關閉時的速度和距離",
    211: "定期速度與距離記錄",
    216: "按鈕事件",
    221: "計數器電路板狀態",
    222: "USB狀態",
    223: "PRS狀態",
    224: "速度計狀態",
    225: "資料下載狀態",
    227: "MVB狀態",
    228: "GPP狀態"
}

# ATP狀態碼定義
ATP_STATUS_CODES = {
    11: "ATP1關機",
    12: "ATP2關機", 
    13: "ATP1運行",
    14: "ATP2運行",
    15: "ATP由關機轉為運行",
    16: "ATP由運行轉為關機"
}

# MMI狀態碼定義
MMI_STATUS_CODES = {
    1: "MMI1關機",
    2: "MMI2關機",
    3: "MMI1運行",
    4: "MMI2運行", 
    5: "MMI由關機轉為運行",
    6: "MMI由運行轉為關機"
}

# PRS事件碼定義
PRS_EVENT_CODES = {
    1: "PRS1列車編號設定成功",
    2: "PRS2列車編號設定成功",
    3: "PRS1 CRC錯誤",
    4: "PRS2 CRC錯誤",
    5: "PRS1設定列車編號超時",
    6: "PRS2設定列車編號超時",
    7: "ID與PRSCV1不匹配",
    8: "ID與PRSCV2不匹配",
    9: "列車編號與PRS1回傳不符",
    10: "列車編號與PRS2回傳不符",
    11: "PRS1與PRSCV1通訊中斷",
    12: "PRS2與PRSCV2通訊中斷", 
    13: "PRS1與PRSCV1通訊恢復",
    14: "PRS2與PRSCV2通訊恢復"
}

# 匯出可用的類別與函數
__all__ = [
    'ATPAnalyzer',
    'RURecord',
    'SpeedProfile',
    'EventRecord',
    'StationRecord',
    'AnalysisResult',
    'AnalysisConfig',
    'ATPAnalyzerError',
    'DataValidationError',
    'ProcessingError',
    'AnalysisError',
    'ConfigError',
    'ExportError',
    'Config',
    'setup_logging',
    'create_analyzer',
    'ATP_EVENT_TYPES',
    'ATP_STATUS_CODES',
    'MMI_STATUS_CODES',
    'PRS_EVENT_CODES'
]
