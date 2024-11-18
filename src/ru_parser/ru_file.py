from dataclasses import dataclass
from datetime import datetime
import struct
from typing import List, Optional

@dataclass
class RUHeader:
    """RU檔案標頭資訊"""
    work_shift: str  # 工作班別
    train_no: str   # 列車號
    driver_id: str  # 司機員ID
    vehicle_id: str # 車輛ID
    date: datetime  # 記錄日期

@dataclass
class RURecord:
    """RU記錄資料結構"""
    log_type: int       # 記錄類型
    timestamp: datetime # 時間戳記
    location: float     # 位置(cm)
    speed: float       # 速度(cm/s)
    data: bytes        # 原始資料

class RUParser:
    """ATP RU記錄檔解析器"""
    def __init__(self):
        self.header = None
        self.records: List[RURecord] = []
        
    def parse_file(self, filename: str) -> None:
        """解析RU檔案"""
        with open(filename, 'rb') as f:
            # 解析標頭
            self.header = self._parse_header(f)
            
            # 解析記錄
            while True:
                record = self._parse_record(f)
                if not record:
                    break
                self.records.append(record)
