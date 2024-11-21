# visualization/core/processors.py

from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from scipy import signal

@dataclass
class ProcessingConfig:
    """數據處理配置"""
    downsample_threshold: int = 1000    # 降採樣閾值
    smooth_window: int = 5              # 平滑窗口大小
    outlier_threshold: float = 3.0      # 異常值檢測閾值(標準差)
    min_peak_distance: int = 10         # 峰值檢測最小距離
    interpolation_method: str = 'linear' # 插值方法

class DataPreprocessor:
    """數據預處理器"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
    
    def process_time_series(self, times: List[datetime], 
                          values: List[float]) -> Tuple[np.ndarray, np.ndarray]:
        """處理時間序列數據"""
        # 轉換為numpy數組
        times_arr = np.array([t.timestamp() for t in times])
        values_arr = np.array(values)
        
        # 移除異常值
        valid_mask = self._remove_outliers(values_arr)
        times_arr = times_arr[valid_mask]
        values_arr = values_arr[valid_mask]
        
        # 插值缺失值
        times_arr, values_arr = self._interpolate_missing(times_arr, values_arr)
        
        # 降採樣
        if len(values_arr) > self.config.downsample_threshold:
            times_arr, values_arr = self._downsample(times_arr, values_arr)
        
        # 平滑處理
        values_arr = self._smooth_data(values_arr)
        
        return times_arr, values_arr
        
    def _remove_outliers(self, data: np.ndarray) -> np.ndarray:
        """移除異常值"""
        mean = np.mean(data)
        std = np.std(data)
        threshold = self.config.outlier_threshold * std
        return np.abs(data - mean) <= threshold
        
    def _interpolate_missing(self, times: np.ndarray, 
                           values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """插值缺失值"""
        # 檢測缺失值
        mask = ~np.isnan(values)
        if np.all(mask):
            return times, values
            
        # 執行插值
        if self.config.interpolation_method == 'linear':
            values = np.interp(times, times[mask], values[mask])
        else:
            # 可以添加其他插值方法
            pass
            
        return times, values
        
    def _downsample(self, times: np.ndarray, 
                    values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """降採樣數據"""
        target_size = self.config.downsample_threshold
        step = len(values) // target_size
        
        # 使用平均值降採樣
        times = times[::step]
        values = np.array([
            values[i:i + step].mean()
            for i in range(0, len(values), step)
        ])
        
        return times[:target_size], values[:target_size]
        
    def _smooth_data(self, data: np.ndarray) -> np.ndarray:
        """平滑化數據"""
        window = np.ones(self.config.smooth_window) / self.config.smooth_window
        return np.convolve(data, window, mode='valid')

class SignalProcessor:
    """信號處理器"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
    
    def detect_peaks(self, data: np.ndarray) -> List[int]:
        """檢測峰值"""
        # 使用scipy的峰值檢測
        peaks, _ = signal.find_peaks(
            data,
            distance=self.config.min_peak_distance
        )
        return peaks.tolist()
        
    def detect_valleys(self, data: np.ndarray) -> List[int]:
        """檢測谷值"""
        # 谷值就是-data的峰值
        valleys, _ = signal.find_peaks(
            -data,
            distance=self.config.min_peak_distance
        )
        return valleys.tolist()
        
    def calculate_derivatives(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """計算導數"""
        # 一階導數(速度)
        first_derivative = np.gradient(data)
        
        # 二階導數(加速度)
        second_derivative = np.gradient(first_derivative)
        
        return first_derivative, second_derivative

class EventProcessor:
    """事件處理器"""
    
    def __init__(self):
        self.event_types = set()
        self.severities = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1,
            'INFO': 0
        }
    
    def process_events(self, events: List[Dict]) -> Dict:
        """處理事件數據"""
        # 更新事件類型集合
        self.event_types.update(e['type'] for e in events)
        
        # 按時間排序
        sorted_events = sorted(events, key=lambda e: e['time'])
        
        # 計算事件統計
        stats = self._calculate_statistics(sorted_events)
        
        # 檢測事件模式
        patterns = self._detect_patterns(sorted_events)
        
        return {
            'statistics': stats,
            'patterns': patterns,
            'timeline': self._generate_timeline(sorted_events)
        }
        
    def _calculate_statistics(self, events: List[Dict]) -> Dict:
        """計算事件統計"""
        stats = {
            'total': len(events),
            'by_type': {},
            'by_severity': {},
            'by_hour': {},
            'intervals': []
        }
        
        # 統計計算
        for i, event in enumerate(events):
            # 按類型統計
            event_type = event['type']
            stats['by_type'][event_type] = stats['by_type'].get(event_type, 0) + 1
            
            # 按嚴重程度統計
            severity = event.get('severity', 'INFO')
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # 按小時統計
            hour = event['time'].hour
            stats['by_hour'][hour] = stats['by_hour'].get(hour, 0) + 1
            
            # 計算事件間隔
            if i > 0:
                interval = (event['time'] - events[i-1]['time']).total_seconds()
                stats['intervals'].append(interval)
                
        return stats
        
    def _detect_patterns(self, events: List[Dict]) -> List[Dict]:
        """檢測事件模式"""
        patterns = []
        window_size = 5
        
        # 使用滑動窗口檢測模式
        for i in range(len(events) - window_size + 1):
            window = events[i:i + window_size]
            
            # 檢查是否為重複模式
            if self._is_repetitive_pattern(window):
                patterns.append({
                    'type': 'repetitive',
                    'start': window[0]['time'],
                    'end': window[-1]['time'],
                    'events': [e['type'] for e in window]
                })
                
            # 檢查是否為嚴重度遞增模式
            if self._is_escalating_pattern(window):
                patterns.append({
                    'type': 'escalating',
                    'start': window[0]['time'],
                    'end': window[-1]['time'],
                    'events': [e['type'] for e in window]
                })
                
        return patterns
        
    def _is_repetitive_pattern(self, events: List[Dict]) -> bool:
        """檢查是否為重複模式"""
        types = [e['type'] for e in events]
        return len(set(types)) == 1
        
    def _is_escalating_pattern(self, events: List[Dict]) -> bool:
        """檢查是否為遞增模式"""
        severities = [
            self.severities.get(e.get('severity', 'INFO'), 0)
            for e in events
        ]
        return all(x <= y for x, y in zip(severities, severities[1:]))
        
    def _generate_timeline(self, events: List[Dict]) -> List[Dict]:
        """生成事件時間線"""
        timeline = []
        current_severity = 'INFO'
        
        for event in events:
            # 檢查嚴重程度變化
            severity = event.get('severity', 'INFO')
            if severity != current_severity:
                timeline.append({
                    'time': event['time'],
                    'type': 'severity_change',
                    'from': current_severity,
                    'to': severity
                })
                current_severity = severity
            
            # 添加事件
            timeline.append({
                'time': event['time'],
                'type': event['type'],
                'severity': severity,
                'description': event.get('description', '')
            })
            
        return timeline
