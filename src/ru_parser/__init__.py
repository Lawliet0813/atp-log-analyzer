"""ATP RU檔案解析器套件"""

from .ru_file import RUParser, RUHeader, RURecord

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
    14: "PRS2與PRSCV2通訊恢復",
    15: "取得PRS1列車編號超時",
    16: "取得PRS2列車編號超時",
    17: "恢復取得PRS1列車編號",
    18: "恢復取得PRS2列車編號",
    19: "PRSCV1啟動",
    20: "PRSCV2啟動"
}

# 按鈕事件碼定義
BUTTON_EVENT_CODES = {
    1: "測試按鈕按下",
    2: "距離重置按鈕按下", 
    3: "資料下載按鈕按下"
}

class RUParserError(Exception):
    """RU解析器異常基礎類別"""
    pass

class HeaderParseError(RUParserError):
    """標頭解析錯誤"""
    pass
    
class RecordParseError(RUParserError):
    """記錄解析錯誤"""
    pass

class DataIntegrityError(RUParserError):
    """資料完整性錯誤"""
    pass

__version__ = "1.0.0"
__author__ = "陳彥儒"
__all__ = [
    'RUParser',
    'RUHeader', 
    'RURecord',
    'RUParserError',
    'HeaderParseError',
    'RecordParseError',
    'DataIntegrityError',
    'ATP_EVENT_TYPES',
    'ATP_STATUS_CODES',
    'MMI_STATUS_CODES', 
    'PRS_EVENT_CODES',
    'BUTTON_EVENT_CODES'
]
