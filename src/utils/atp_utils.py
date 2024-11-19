# src/utils/atp_utils.py

import struct
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np

class ATPEventParser:
    """ATP事件解析器"""
    
    # ATP事件代碼對應
    ATP_STATUS_MAP = {
        0: "正常",
        1: "常用緊軔",
        2: "緊急緊軔",
        3: "系統故障",
        4: "通訊異常",
        5: "感應子異常", 
        6: "軔機測試中",
        7: "超速警告",
        8: "自動防護"
    }
    
    # MMI事件代碼對應
    MMI_STATUS_MAP = {
        0: "正常",
        1: "顯示異常",
        2: "按鍵故障",
        3: "記憶體不足",
        4: "通訊中斷",
        5: "系統重啟"
    }
    
    # PRS事件代碼對應
    PRS_EVENT_MAP = {
        0: "通訊正常",
        1: "列車編號設定",
        2: "CRC錯誤",
        3: "通訊逾時",
        4: "編號不符",
        5: "連線中斷",
        6: "連線恢復"
    }
    
    @classmethod
    def parse_atp_status(cls, data: bytes) -> str:
        """解析ATP狀態事件"""
        if len(data) < 1:
            return "資料不完整"
        status_code = data[0]
        return cls.ATP_STATUS_MAP.get(status_code, f"未知狀態({status_code})")
        
    @classmethod
    def parse_mmi_status(cls, data: bytes) -> str:
        """解析MMI狀態事件"""
        if len(data) < 1:
            return "資料不完整"
        status_code = data[0]
        return cls.MMI_STATUS_MAP.get(status_code, f"未知狀態({status_code})")
        
    @classmethod
    def parse_prs_event(cls, data: bytes) -> str:
        """解析PRS事件"""
        if len(data) < 1:
            return "資料不完整"
        event_code = data[0]
        return cls.PRS_EVENT_MAP.get(event_code, f"未知事件({event_code})")
        
    @classmethod
    def get_event_description(cls, event_type: int, data: bytes) -> str:
        """取得事件描述"""
        if event_type == 2:
            return cls.parse_atp_status(data)
        elif event_type == 3:
            return cls.parse_mmi_status(data)
        elif event_type == 91:
            return cls.parse_prs_event(data)
        elif event_type == 201:
            if len(data) >= 8:
                location = struct.unpack('i', data[0:4])[0]
                speed = struct.unpack('i', data[4:8])[0] / 100.0
                return f"位置:{location/100000:.2f}km, 速度:{speed:.1f}km/h"
        return "未知事件類型"

class SpeedAnalyzer:
    """速度分析工具"""
    
    def __init__(self, speed_threshold: float = 90.0):
        self.speed_threshold = speed_threshold
        
    def analyze_speed_profile(self, speeds: List[float], 
                            timestamps: List[datetime]) -> Dict:
        """分析速度特性"""
        if not speeds or not timestamps:
            return {}
            
        # 基本統計
        max_speed = max(speeds)
        avg_speed = np.mean(speeds)
        std_speed = np.std(speeds)
        
        # 超速統計
        over_speed_count = sum(1 for s in speeds if s > self.speed_threshold)
        over_speed_ratio = over_speed_count / len(speeds) * 100
        
        # 速度分布
        bins = [0, 20, 40, 60, 80, 100, 120]
        hist, _ = np.histogram(speeds, bins=bins)
        speed_dist = {
            f"{bins[i]}-{bins[i+1]}km/h": int(count)
            for i, count in enumerate(hist)
        }
        
        # 加減速分析
        dt = np.diff([t.timestamp() for t in timestamps])
        dv = np.diff(speeds)
        accelerations = dv/dt  # km/h/s
        
        acc_stats = {
            'max_acceleration': max(accelerations),
            'max_deceleration': abs(min(accelerations)),
            'avg_acceleration': np.mean([a for a in accelerations if a > 0]),
            'avg_deceleration': abs(np.mean([a for a in accelerations if a < 0]))
        }
        
        return {
            'basic_stats': {
                'max_speed': max_speed,
                'avg_speed': avg_speed,
                'std_speed': std_speed,
                'over_speed_count': over_speed_count,
                'over_speed_ratio': over_speed_ratio
            },
            'speed_distribution': speed_dist,
            'acceleration_stats': acc_stats
        }
        
    def detect_speed_events(self, speeds: List[float], 
                          timestamps: List[datetime],
                          window_size: int = 5) -> List[Dict]:
        """檢測速度事件"""
        events = []
        
        # 使用移動窗口檢測突然的速度變化
        for i in range(len(speeds) - window_size):
            window = speeds[i:i+window_size]
            avg_speed = np.mean(window)
            std_speed = np.std(window)
            
            # 檢測急加速
            if i > 0:
                acceleration = (speeds[i] - speeds[i-1]) / \
                             (timestamps[i].timestamp() - timestamps[i-1].timestamp())
                if acceleration > 2.0:  # km/h/s
                    events.append({
                        'time': timestamps[i],
                        'type': 'rapid_acceleration',
                        'value': acceleration,
                        'speed': speeds[i]
                    })
                    
            # 檢測急減速
            if i > 0:
                deceleration = (speeds[i-1] - speeds[i]) / \
                              (timestamps[i].timestamp() - timestamps[i-1].timestamp())
                if deceleration > 2.0:  # km/h/s
                    events.append({
                        'time': timestamps[i],
                        'type': 'rapid_deceleration',
                        'value': deceleration,
                        'speed': speeds[i]
                    })
                    
            # 檢測超速
            if speeds[i] > self.speed_threshold:
                events.append({
                    'time': timestamps[i],
                    'type': 'over_speed',
                    'value': speeds[i],
                    'threshold': self.speed_threshold
                })
                
            # 檢測速度異常波動
            if std_speed > 5.0:  # km/h
                events.append({
                    'time': timestamps[i],
                    'type': 'speed_fluctuation',
                    'value': std_speed,
                    'avg_speed': avg_speed
                })
                
        return events

class LocationAnalyzer:
    """位置分析工具"""
    
    def __init__(self, station_map: Dict[str, float]):
        """
        初始化位置分析器
        station_map: 站點位置對照表 {站名: 公里標}
        """
        self.station_map = station_map
        
    def analyze_station_times(self, locations: List[float],
                            timestamps: List[datetime]) -> Dict:
        """分析站間運行時間"""
        station_times = {}
        current_station = None
        station_entry_time = None
        
        for i, loc in enumerate(locations):
            # 尋找最近的車站
            nearest_station = min(
                self.station_map.items(),
                key=lambda x: abs(x[1] - loc)
            )
            
            # 如果接近車站(誤差在50公尺內)
            if abs(nearest_station[1] - loc) < 0.05:
                if current_station and station_entry_time:
                    duration = timestamps[i] - station_entry_time
                    key = f"{current_station}->{nearest_station[0]}"
                    station_times[key] = duration.total_seconds() / 60
                    
                current_station = nearest_station[0]
                station_entry_time = timestamps[i]
                
        return station_times
        
    def calculate_section_speeds(self, locations: List[float],
                               timestamps: List[datetime]) -> Dict:
        """計算區間平均速度"""
        section_speeds = {}
        
        for i in range(len(locations) - 1):
            distance = locations[i+1] - locations[i]  # km
            time_diff = (timestamps[i+1] - timestamps[i]).total_seconds() / 3600  # h
            if time_diff > 0:
                speed = distance / time_diff  # km/h
                
                # 找出所在區間
                for station1, loc1 in self.station_map.items():
                    for station2, loc2 in self.station_map.items():
                        if loc1 < locations[i] < loc2:
                            section = f"{station1}-{station2}"
                            if section not in section_speeds:
                                section_speeds[section] = []
                            section_speeds[section].append(speed)
                            
        # 計算每個區間的平均速度
        return {
            section: np.mean(speeds)
            for section, speeds in section_speeds.items()
        }

class StationDataAnalyzer:
    """車站資料分析器"""
    
    def __init__(self):
        self.station_codes = {}  # 車站代碼對照表
        
    def load_station_codes(self, codes: Dict[str, str]):
        """載入車站代碼"""
        self.station_codes = codes
        
    def analyze_station_events(self, events: List[Dict]) -> Dict:
        """分析車站相關事件"""
        station_stats = {}
        
        for event in events:
            if event.get('type') == 'station':
                station = event.get('station')
                if station not in station_stats:
                    station_stats[station] = {
                        'arrival_count': 0,
                        'departure_count': 0,
                        'dwell_times': []
                    }
                    
                if event.get('action') == 'arrival':
                    station_stats[station]['arrival_count'] += 1
                    # 記錄到站時間
                    station_stats[station]['last_arrival'] = event.get('time')
                elif event.get('action') == 'departure':
                    station_stats[station]['departure_count'] += 1
                    # 計算停站時間
                    if 'last_arrival' in station_stats[station]:
                        dwell_time = (event.get('time') - 
                                    station_stats[station]['last_arrival']).total_seconds()
                        station_stats[station]['dwell_times'].append(dwell_time)
                        
        # 計算平均停站時間
        for station in station_stats:
            times = station_stats[station]['dwell_times']
            if times:
                station_stats[station]['avg_dwell_time'] = np.mean(times)
                station_stats[station]['max_dwell_time'] = max(times)
                station_stats[station]['min_dwell_time'] = min(times)
            del station_stats[station]['dwell_times']  # 移除原始資料
            del station_stats[station]['last_arrival']  # 移除暫存資料
            
        return station_stats
