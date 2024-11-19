# src/analyzer/atp_analyzer.py

from dataclasses import dataclass
from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime, timedelta

@dataclass
class AnalysisResult:
    """分析結果資料結構"""
    max_speed: float           # 最高速度(km/h)
    avg_speed: float          # 平均速度(km/h) 
    total_distance: float     # 總行駛距離(km)
    total_time: timedelta     # 總行駛時間
    over_speed_count: int     # 超速次數
    emergency_brake_count: int # 緊急煞車次數
    atp_down_count: int       # ATP關機次數
    speed_stats: Dict         # 速度統計資料
    location_stats: Dict      # 位置統計資料
    event_stats: Dict         # 事件統計資料

class ATPAnalyzer:
    """ATP記錄分析器"""
    
    def __init__(self):
        self.speed_threshold = 90.0  # 超速門檻(km/h)
        
    def analyze(self, records: List) -> AnalysisResult:
        """分析ATP記錄資料"""
        if not records:
            raise ValueError("No records to analyze")
            
        # 1. 基本資料統計
        speeds = []        # 速度列表
        locations = []     # 位置列表
        timestamps = []    # 時間列表
        events = []        # 事件列表
        
        for record in records:
            if record.log_type == 211:  # 速度記錄
                speeds.append(record.speed / 100.0)  # 轉換為km/h
                locations.append(record.location / 100000.0)  # 轉換為km
                timestamps.append(record.timestamp)
            elif record.log_type in [2, 3, 91, 201]:  # 事件記錄
                events.append(record)
                
        # 2. 計算基本統計值
        max_speed = max(speeds) if speeds else 0
        avg_speed = np.mean(speeds) if speeds else 0
        total_distance = locations[-1] - locations[0] if locations else 0
        total_time = timestamps[-1] - timestamps[0] if timestamps else timedelta()
        
        # 3. 計算超速統計
        over_speed_count = sum(1 for s in speeds if s > self.speed_threshold)
        
        # 4. 計算煞車統計
        emergency_brake_count = sum(
            1 for e in events 
            if e.log_type == 2 and self._is_emergency_brake(e.data)
        )
        
        # 5. 計算ATP關機統計
        atp_down_count = sum(
            1 for e in events
            if e.log_type == 201 
        )
        
        # 6. 速度分布統計
        speed_stats = {
            '速度分布': self._calculate_speed_distribution(speeds),
            '加減速分析': self._analyze_acceleration(speeds, timestamps)
        }
        
        # 7. 位置相關統計
        location_stats = {
            '站間運行時間': self._calculate_station_times(records),
            '位置分布': self._calculate_location_distribution(locations)
        }
        
        # 8. 事件統計分析
        event_stats = self._analyze_events(events)
        
        return AnalysisResult(
            max_speed=max_speed,
            avg_speed=avg_speed,
            total_distance=total_distance,
            total_time=total_time,
            over_speed_count=over_speed_count,
            emergency_brake_count=emergency_brake_count,
            atp_down_count=atp_down_count,
            speed_stats=speed_stats,
            location_stats=location_stats,
            event_stats=event_stats
        )
    
    def _is_emergency_brake(self, data: bytes) -> bool:
        """判斷是否為緊急煞車事件"""
        return len(data) > 0 and data[0] == 2  # 狀態碼2表示緊急煞車
        
    def _calculate_speed_distribution(self, speeds: List[float]) -> Dict:
        """計算速度分布"""
        if not speeds:
            return {}
            
        bins = [0, 20, 40, 60, 80, 100, 120]
        hist, _ = np.histogram(speeds, bins=bins)
        
        return {
            f"{bins[i]}-{bins[i+1]}km/h": int(count)
            for i, count in enumerate(hist)
        }
        
    def _analyze_acceleration(self, speeds: List[float], 
                            timestamps: List[datetime]) -> Dict:
        """分析加減速特性"""
        if len(speeds) < 2:
            return {}
            
        # 計算加速度 (km/h/s)
        time_diffs = [(t2-t1).total_seconds() 
                     for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
        speed_diffs = [s2-s1 for s1, s2 in zip(speeds[:-1], speeds[1:])]
        
        accelerations = [
            sd/td if td > 0 else 0 
            for sd, td in zip(speed_diffs, time_diffs)
        ]
        
        return {
            '最大加速度': f"{max(accelerations):.2f} km/h/s",
            '最大減速度': f"{abs(min(accelerations)):.2f} km/h/s",
            '平均加速度': f"{np.mean([a for a in accelerations if a > 0]):.2f} km/h/s",
            '平均減速度': f"{abs(np.mean([a for a in accelerations if a < 0])):.2f} km/h/s"
        }
        
    def _calculate_station_times(self, records: List) -> Dict:
        """計算站間運行時間"""
        station_times = {}
        current_station = None
        station_entry_time = None
        
        for record in records:
            if record.log_type == 91:  # PRS事件(到站)
                if current_station and station_entry_time:
                    duration = record.timestamp - station_entry_time
                    key = f"{current_station}->{record.data.decode('ascii')}"
                    station_times[key] = f"{duration.total_seconds()/60:.1f}分鐘"
                current_station = record.data.decode('ascii')
                station_entry_time = record.timestamp
                
        return station_times
        
    def _calculate_location_distribution(self, locations: List[float]) -> Dict:
        """計算位置分布"""
        if not locations:
            return {}
            
        # 每10km一個區間
        bins = np.arange(0, max(locations) + 10, 10)
        hist, _ = np.histogram(locations, bins=bins)
        
        return {
            f"{bins[i]:.0f}-{bins[i+1]:.0f}km": int(count)
            for i, count in enumerate(hist)
        }
        
    def _analyze_events(self, events: List) -> Dict:
        """分析事件統計"""
        event_counts = {
            'ATP狀態變更': 0,
            'MMI狀態變更': 0,
            'PRS事件': 0,
            'ATP關閉': 0
        }
        
        event_details = {
            'ATP重要事件': [],
            'MMI操作記錄': [],
            'PRS通訊記錄': []
        }
        
        for event in events:
            if event.log_type == 2:
                event_counts['ATP狀態變更'] += 1
                if self._is_emergency_brake(event.data):
                    event_details['ATP重要事件'].append(
                        f"{event.timestamp}: 緊急煞車"
                    )
            elif event.log_type == 3:
                event_counts['MMI狀態變更'] += 1
                event_details['MMI操作記錄'].append(
                    f"{event.timestamp}: 狀態碼{event.data[0]}"
                )
            elif event.log_type == 91:
                event_counts['PRS事件'] += 1
                event_details['PRS通訊記錄'].append(
                    f"{event.timestamp}: {event.data.decode('ascii')}"
                )
            elif event.log_type == 201:
                event_counts['ATP關閉'] += 1
                
        return {
            '事件計數': event_counts,
            '事件詳情': event_details
        }
