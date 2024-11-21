# src/analyzer/models.py

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

@dataclass
class RURecord:
    """ATP RU記錄資料結構"""
    log_type: int       # 記錄類型
    timestamp: datetime # 時間戳記
    location: float     # 位置(cm)
    speed: float       # 速度(cm/s)
    data: bytes        # 原始資料
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'log_type': self.log_type,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location,
            'speed': self.speed,
            'data': self.data.hex()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RURecord':
        """從字典建立實例"""
        return cls(
            log_type=data['log_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            location=data['location'],
            speed=data['speed'],
            data=bytes.fromhex(data['data'])
        )
        
    def __str__(self) -> str:
        return (
            f"RURecord(type={self.log_type}, "
            f"time={self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}, "
            f"loc={self.location/100000:.3f}km, "
            f"speed={self.speed/100:.1f}km/h)"
        )

@dataclass
class SpeedProfile:
    """速度剖面資料"""
    timestamps: List[datetime]           # 時間序列
    speeds: List[float]                 # 速度序列(km/h)
    locations: List[float]              # 位置序列(km)
    max_speed: float = field(default=0.0) # 最高速度
    avg_speed: float = field(default=0.0) # 平均速度
    over_speed_count: int = field(default=0) # 超速次數
    
    def calculate_stats(self, speed_threshold: float = 90.0):
        """計算統計資料"""
        if not self.speeds:
            return
            
        self.max_speed = max(self.speeds)
        self.avg_speed = sum(self.speeds) / len(self.speeds)
        self.over_speed_count = sum(1 for s in self.speeds if s > speed_threshold)
        
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'timestamps': [t.isoformat() for t in self.timestamps],
            'speeds': self.speeds,
            'locations': self.locations,
            'max_speed': self.max_speed,
            'avg_speed': self.avg_speed,
            'over_speed_count': self.over_speed_count
        }

@dataclass
class EventRecord:
    """事件記錄資料"""
    event_type: str           # 事件類型
    timestamp: datetime       # 發生時間
    location: float          # 發生位置(km)
    severity: str            # 嚴重程度
    description: str         # 事件描述
    data: Dict[str, Any]     # 詳細資料
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location,
            'severity': self.severity,
            'description': self.description,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventRecord':
        """從字典建立實例"""
        return cls(
            event_type=data['event_type'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            location=data['location'],
            severity=data['severity'],
            description=data['description'],
            data=data['data']
        )

@dataclass
class StationRecord:
    """車站記錄資料"""
    station_id: str          # 車站代碼
    station_name: str        # 車站名稱
    arrival_time: datetime   # 到達時間
    departure_time: Optional[datetime] = None  # 出發時間
    dwell_time: Optional[timedelta] = None     # 停留時間
    platform: Optional[str] = None             # 使用月台
    
    def calculate_dwell_time(self):
        """計算停留時間"""
        if self.arrival_time and self.departure_time:
            self.dwell_time = self.departure_time - self.arrival_time
            
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'station_id': self.station_id,
            'station_name': self.station_name,
            'arrival_time': self.arrival_time.isoformat(),
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'dwell_time': str(self.dwell_time) if self.dwell_time else None,
            'platform': self.platform
        }

@dataclass
class AnalysisResult:
    """分析結果資料"""
    max_speed: float                # 最高速度(km/h)
    avg_speed: float               # 平均速度(km/h)
    total_distance: float          # 總行駛距離(km)
    total_time: timedelta          # 總行駛時間
    over_speed_count: int          # 超速次數
    emergency_brake_count: int     # 緊急煞車次數
    atp_down_count: int           # ATP關機次數
    speed_stats: Dict[str, Any]    # 速度統計資料
    location_stats: Dict[str, Any] # 位置統計資料
    event_stats: Dict[str, Any]    # 事件統計資料
    
    def get_basic_stats(self) -> Dict[str, Any]:
        """取得基本統計資料"""
        return {
            '最高速度': f"{self.max_speed:.1f} km/h",
            '平均速度': f"{self.avg_speed:.1f} km/h",
            '總距離': f"{self.total_distance:.1f} km",
            '總時間': str(self.total_time),
            '超速次數': self.over_speed_count,
            '緊急煞車次數': self.emergency_brake_count,
            'ATP關機次數': self.atp_down_count
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'basic_stats': self.get_basic_stats(),
            'speed_stats': self.speed_stats,
            'location_stats': self.location_stats,
            'event_stats': self.event_stats
        }
        
    def to_json(self) -> str:
        """轉換為JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """從字典建立實例"""
        return cls(
            max_speed=data['basic_stats']['最高速度'],
            avg_speed=data['basic_stats']['平均速度'],
            total_distance=data['basic_stats']['總距離'],
            total_time=data['basic_stats']['總時間'],
            over_speed_count=data['basic_stats']['超速次數'],
            emergency_brake_count=data['basic_stats']['緊急煞車次數'],
            atp_down_count=data['basic_stats']['ATP關機次數'],
            speed_stats=data['speed_stats'],
            location_stats=data['location_stats'],
            event_stats=data['event_stats']
        )

@dataclass
class AnalysisConfig:
    """分析器配置資料"""
    chunk_size: int = 1000           # 分批大小
    speed_threshold: float = 90.0    # 速度閾值(km/h)
    cache_enabled: bool = True       # 啟用快取
    parallel_enabled: bool = True    # 啟用平行處理
    log_level: str = 'INFO'         # 日誌等級
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'chunk_size': self.chunk_size,
            'speed_threshold': self.speed_threshold,
            'cache_enabled': self.cache_enabled,
            'parallel_enabled': self.parallel_enabled,
            'log_level': self.log_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisConfig':
        """從字典建立實例"""
        return cls(**data)
        
    def validate(self):
        """驗證配置有效性"""
        if self.chunk_size < 100 or self.chunk_size > 10000:
            raise ValueError(f"無效的chunk_size: {self.chunk_size}")
            
        if self.speed_threshold < 0 or self.speed_threshold > 200:
            raise ValueError(f"無效的speed_threshold: {self.speed_threshold}")
            
        if self.log_level not in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
            raise ValueError(f"無效的log_level: {self.log_level}")

# 常用的資料轉換函數
def convert_speed(speed_cms: float) -> float:
    """將速度從cm/s轉換為km/h"""
    return speed_cms * 0.036  # (cm/s) * (3600s/h) / (100000cm/km)

def convert_location(location_cm: float) -> float:
    """將位置從cm轉換為km"""
    return location_cm / 100000.0

def parse_timestamp(timestamp_str: str) -> datetime:
    """解析時間戳記字串"""
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError(f"無效的時間格式: {timestamp_str}")
