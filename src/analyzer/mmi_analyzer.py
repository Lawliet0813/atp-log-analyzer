from typing import List, Dict, Optional
import numpy as np
from datetime import datetime
from ..parsers.mmi_parser import MMIParser, MMIEventRecord, MMISpeedRecord

class MMIAnalyzer:
    """MMI資料分析器"""
    
    def __init__(self):
        self.speed_threshold = 90.0  # 速度閾值(km/h)
        
    def analyze_speed(self, records: List[MMISpeedRecord]) -> Dict:
        """分析速度記錄"""
        if not records:
            return {}
            
        speeds = [r.speed for r in records]
        times = [r.timestamp for r in records]
        
        # 基本統計
        stats = {
            'max_speed': max(speeds),
            'min_speed': min(speeds),
            'avg_speed': np.mean(speeds),
            'std_speed': np.std(speeds),
            'over_speed_count': sum(1 for s in speeds if s > self.speed_threshold),
            'total_time': (times[-1] - times[0]).total_seconds() / 3600  # 小時
        }
        
        # 速度分布
        hist, bins = np.histogram(speeds, bins=10)
        stats['speed_distribution'] = {
            f"{bins[i]:.1f}-{bins[i+1]:.1f}": int(count)
            for i, count in enumerate(hist)
        }
        
        # 加減速分析
        dt = np.diff([t.timestamp() for t in times])
        dv = np.diff(speeds)
        accelerations = dv/dt
        
        stats['acceleration'] = {
            'max_acceleration': float(np.max(accelerations)),
            'max_deceleration': float(np.min(accelerations)),
            'avg_acceleration': float(np.mean(accelerations[accelerations > 0])),
            'avg_deceleration': float(np.mean(accelerations[accelerations < 0]))
        }
        
        return stats
        
    def analyze_events(self, records: List[MMIEventRecord]) -> Dict:
        """分析事件記錄"""
        if not records:
            return {}
            
        # 事件統計
        event_counts = {}
        critical_events = []
        error_events = []
        
        for record in records:
            # 計算事件類型分布
            event_counts[record.event_type] = \
                event_counts.get(record.event_type, 0) + 1
                
            # 檢查重要事件
            if record.event_type == MMIParser.EVENT_ERROR:
                error_events.append({
                    'time': record.timestamp,
                    'data': record.event_data
                })
            elif record.event_type in [MMIParser.EVENT_SHUTDOWN, 
                                     MMIParser.EVENT_MODE_CHANGE]:
                critical_events.append({
                    'time': record.timestamp,
                    'type': record.event_type,
                    'data': record.event_data
                })
                
        return {
            'event_counts': event_counts,
            'critical_events': critical_events,
            'error_events': error_events,
            'total_events': len(records),
            'error_count': len(error_events)
        }
        
    def analyze_operation_modes(self, records: List[MMIEventRecord]) -> Dict:
        """分析運作模式變化"""
        mode_changes = []
        current_mode = None
        mode_durations = {}
        
        for record in records:
            if record.event_type == MMIParser.EVENT_MODE_CHANGE:
                mode = record.event_data[0]  # 假設第一個byte是模式代碼
                
                if current_mode is not None:
                    # 記錄模式變更
                    mode_changes.append({
                        'time': record.timestamp,
                        'from': current_mode,
                        'to': mode
                    })
                    
                    # 計算持續時間
                    if current_mode in mode_durations:
                        mode_durations[current_mode] += \
                            (record.timestamp - last_change).total_seconds()
                    else:
                        mode_durations[current_mode] = \
                            (record.timestamp - last_change).total_seconds()
                        
                current_mode = mode
                last_change = record.timestamp
                
        return {
            'mode_changes': mode_changes,
            'mode_durations': mode_durations,
            'total_changes': len(mode_changes)
        }
        
    def analyze_system_stability(self, records: List[MMIEventRecord]) -> Dict:
        """分析系統穩定性"""
        error_intervals = []
        last_error = None
        error_count = 0
        restart_count = 0
        
        for record in records:
            if record.event_type == MMIParser.EVENT_ERROR:
                error_count += 1
                if last_error:
                    interval = (record.timestamp - last_error).total_seconds()
                    error_intervals.append(interval)
                last_error = record.timestamp
                
            elif record.event_type == MMIParser.EVENT_STARTUP:
                restart_count += 1
                
        return {
            'error_count': error_count,
            'restart_count': restart_count,
            'avg_error_interval': np.mean(error_intervals) if error_intervals else 0,
            'min_error_interval': min(error_intervals) if error_intervals else 0,
            'error_intervals': error_intervals
        }
        
    def generate_summary(self, speed_stats: Dict, event_stats: Dict,
                        mode_stats: Dict, stability_stats: Dict) -> str:
        """產生分析摘要"""
        lines = [
            "MMI系統分析摘要",
            "-" * 40,
            f"最高速度: {speed_stats['max_speed']:.1f} km/h",
            f"平均速度: {speed_stats['avg_speed']:.1f} km/h",
            f"超速次數: {speed_stats['over_speed_count']}",
            f"總行駛時間: {speed_stats['total_time']:.1f} 小時",
            "",
            f"總事件數: {event_stats['total_events']}",
            f"錯誤事件: {event_stats['error_count']}",
            f"模式切換: {mode_stats['total_changes']}次",
            "",
            "系統穩定性:",
            f"- 系統重啟: {stability_stats['restart_count']}次",
            f"- 錯誤次數: {stability_stats['error_count']}次",
            f"- 平均錯誤間隔: {stability_stats['avg_error_interval']:.1f}秒"
        ]
        
        return "\n".join(lines)
