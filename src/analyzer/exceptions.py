# src/analyzer/exceptions.py

class ATPAnalyzerError(Exception):
    """ATP分析器異常基礎類別"""
    
    def __init__(self, message: str = None, details: dict = None):
        self.message = message or "ATP分析器錯誤"
        self.details = details or {}
        super().__init__(self.message)
        
    def __str__(self):
        if self.details:
            return f"{self.message} - 詳細資訊: {self.details}"
        return self.message

class DataValidationError(ATPAnalyzerError):
    """資料驗證錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "資料驗證失敗",
            details
        )

class ProcessingError(ATPAnalyzerError):
    """資料處理錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "資料處理失敗",
            details
        )

class AnalysisError(ATPAnalyzerError):
    """分析過程錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "分析過程失敗",
            details
        )

class ConfigError(ATPAnalyzerError):
    """配置錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "配置錯誤",
            details
        )

class FileError(ATPAnalyzerError):
    """檔案操作錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "檔案操作失敗",
            details
        )

class ExportError(ATPAnalyzerError):
    """匯出錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "匯出失敗",
            details
        )

class TimeoutError(ATPAnalyzerError):
    """操作超時錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "操作超時",
            details
        )

class MemoryError(ATPAnalyzerError):
    """記憶體錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "記憶體不足",
            details
        )

class ParallelProcessError(ATPAnalyzerError):
    """平行處理錯誤"""
    
    def __init__(self, message: str = None, details: dict = None):
        super().__init__(
            message or "平行處理失敗",
            details
        )

# 異常代碼定義
ERROR_CODES = {
    # 資料驗證錯誤 (1000-1999)
    1001: "記錄數量不足",
    1002: "缺少必要欄位",
    1003: "時間序列錯誤",
    1004: "速度資料異常",
    1005: "位置資料異常",
    1006: "事件資料異常",
    1007: "配置驗證失敗",
    
    # 處理錯誤 (2000-2999)
    2001: "資料轉換失敗",
    2002: "資料計算錯誤",
    2003: "事件解析失敗",
    2004: "資料合併錯誤",
    2005: "資料過濾錯誤",
    
    # 分析錯誤 (3000-3999)
    3001: "速度分析失敗",
    3002: "事件分析失敗",
    3003: "位置分析失敗",
    3004: "統計分析失敗",
    3005: "報告產生失敗",
    
    # 檔案錯誤 (4000-4999)
    4001: "檔案不存在",
    4002: "檔案讀取失敗",
    4003: "檔案寫入失敗",
    4004: "檔案格式錯誤",
    4005: "檔案權限不足",
    
    # 系統錯誤 (5000-5999)
    5001: "記憶體不足",
    5002: "處理超時",
    5003: "平行處理失敗",
    5004: "系統資源不足",
    5005: "執行環境錯誤"
}

def get_error_message(code: int) -> str:
    """取得錯誤代碼對應的訊息"""
    return ERROR_CODES.get(code, "未知錯誤")

def create_error(code: int, **kwargs) -> ATPAnalyzerError:
    """建立對應的異常物件
    
    Args:
        code: 錯誤代碼
        **kwargs: 額外的錯誤資訊
        
    Returns:
        ATPAnalyzerError: 異常物件
    """
    message = get_error_message(code)
    
    if 1000 <= code < 2000:
        return DataValidationError(message, kwargs)
    elif 2000 <= code < 3000:
        return ProcessingError(message, kwargs)
    elif 3000 <= code < 4000:
        return AnalysisError(message, kwargs)
    elif 4000 <= code < 5000:
        return FileError(message, kwargs)
    elif code == 5001:
        return MemoryError(message, kwargs)
    elif code == 5002:
        return TimeoutError(message, kwargs)
    elif code == 5003:
        return ParallelProcessError(message, kwargs)
    else:
        return ATPAnalyzerError(message, kwargs)
