from typing import List, Dict, Tuple
import numpy as np
from datetime import datetime, timedelta
from ..parsers.ru_parser import RUParser, RURecord
from ..parsers.mmi_parser import MMIParser, MMIRecord

class CombinedAnalyzer:
    """ATP與MMI整合分析器"""
    
    def __init__(self):
        self.time_tolerance = 1.0  # 時間匹配容許誤差(秒)
        self.speed_tolerance = 2.0  # 速度匹配容許誤差(km/h)
        
    def analyze_speed_correlation(self, 
                                ru_speeds: List[Tuple[datetime, float]],
                                mmi_speeds: List[Tuple[datetime, float]]) -> Dict:
        """分析速度相關性"""
        # 查找最接近的時間點進行速度比對
        differences = []
        matched_points = []
        
        for ru_time, ru_speed in ru_speeds:
            # 尋找最接近的MMI記錄
            closest_mmi = min(
                mmi_speeds,
                key=lambda x: abs((x[0] - ru_time).total_seconds()),
                default=None
            )
            
            if closest_mmi:
                time_diff = (closest_mmi[0] - ru_time).total_seconds()
                if abs(time_diff) <= self.time_tolerance:
                    speed_diff = closest_mmi[1] - ru_speed
                    differences.append(speed_diff)
                    matched_points.append({
                        'time': ru_time,
                        'ru_speed': ru_speed,
                        'mmi_speed': closest_mmi[1],
                        'difference': speed_diff
                    })
                    
        return {
            'avg_difference': float(np.mean(differences)),
            'max_difference': float(np.max(np.abs(differences))),
            'std_difference': float(np.std(differences)),
            'match_count': len(matched_points),
            'abnormal_points': [
                p for p in matched_points
                if abs(p['difference']) > self.speed_tolerance
            ]
        }
        
    def analyze_event_correlation(self,
                                ru_events: List[Dict],
                                mmi_events: List[Dict]) -> Dict:
        """分析事件相關性"""
        # 配對相關事件
        correlated_events = []
        unpaired_ru_events = []
        unpaired_mmi_events = []
        
        for ru_event in ru_events:
            # 尋找時間相近的MMI事件
            matched = False
            ru_time = ru_event['time']
            
            for mmi_event in mmi_events:
                mmi_time = mmi_event['time']
                time_diff = (mmi_time - ru_time).total_seconds()
                
                if abs(time_diff) <= self.time_tolerance:
                    # 檢查是否為相關事件
                    if self._are_events_related(ru_event, mmi_event):
                        correlated_events.append({
                            'time': ru_time,
                            'ru_event': ru_event,
                            'mmi_event': mmi_event,
                            'time_diff': time_diff
                        })
                        matched = True
                        break
                        
            if not matched:
                unpaired_ru_events.append(ru_event)
                
        # 找出未配對的MMI事件
        paired_mmi_times = {e['mmi_event']['time'] for e in correlated_events}
        unpaired_mmi_events = [
            e for e in mmi_events
            if e['time'] not in paired_mmi_times
        ]
        
        return {
            'correlated_events': correlated_events,
            'unpaired_ru_events': unpaired_ru_events,
            'unpaired_mmi_events': unpaired_mmi_events,
            'correlation_rate': len(correlated_events) / len(ru_events)
                              if ru_events else 0
        }
        
    def analyze_system_consistency(self,
                                 ru_records: List[RURecord],
                                 mmi_records: List[MMIRecord]) -> Dict:
        """分析系統一致性"""
        # 檢查記錄時間範圍
        ru_times = [r.timestamp for r in ru_records]
        mmi_times = [r.timestamp for r in mmi_records]
        
        ru_start, ru_end = min(ru_times), max(ru_times)
        mmi_start, mmi_end = min(mmi_times), max(mmi_times)
        
        time_coverage = {
            'ru_start': ru_start,
            'ru_end': ru_end,
            'mmi_start': mmi_start,
            'mmi_end': mmi_end,
            'overlap_start': max(ru_start, mmi_start),
            'overlap_end': min(ru_end, mmi_end)
        }
        
        # 檢查記錄完整性
        ru_gaps = self._find_time_gaps(ru_times)
        mmi_gaps = self._find_time_gaps(mmi_times)
        
        # 檢查系統狀態一致性
        state_inconsistencies = []
        current_ru_state = None
        current_mmi_state = None
        
        # ... (實作狀態一致性檢查邏輯)
        
        return {
            'time_coverage': time_coverage,
            'ru_gaps': ru_gaps,
            'mmi_gaps': mmi_gaps,
            'state_inconsistencies': state_inconsistencies
        }
        
    def _are_events_related(self, ru_event: Dict, mmi_event: Dict) -> bool:
        """判斷兩個事件是否相關"""
        # 定義事件對應關係
        related_events = {
            # RU事件類型: [對應的MMI事件類型]
            2: [MMIParser.EVENT_ERROR],  # ATP狀態變更 vs MMI錯誤
            3: [MMIParser.EVENT_MODE_CHANGE],  # MMI狀態變更 vs 模式切換
            91: [MMIParser.EVENT_USER_ACTION]  # PRS事件 vs 使用者操作
        }
        
        return ru_event.get('type') in related_events and \
               mmi_event.get('event_type') in related_events[ru_event['type']]
               
    def _find_time_gaps(self, timestamps: List[datetime],
                       max_interval: float = 5.0) -> List[Dict]:
        """尋找時間序列中的間隔"""
        gaps = []
        for t1, t2 in zip(timestamps[:-1], timestamps[1:]):
            interval = (t2 - t1).total_seconds()
            if interval > max_interval:
                gaps.append({
                    'start': t1,
                    'end': t2,
                    'duration': interval
                })
        return gaps
        
    def generate_analysis_report(self, speed_corr: Dict,
                               event_corr: Dict,
                               system_cons: Dict) -> str:
        """產生分析報告"""
        lines = [
            "ATP與MMI整合分析報告",
            "=" * 50,
            "\n速度記錄分析:
"ATP與MMI整合分析報告",
            "=" * 50,
            "\n速度記錄分析:",
            f"- 平均速度差異: {speed_corr['avg_difference']:.2f} km/h",
            f"- 最大速度差異: {speed_corr['max_difference']:.2f} km/h",
            f"- 標準差: {speed_corr['std_difference']:.2f} km/h",
            f"- 匹配點數: {speed_corr['match_count']}",
            f"- 異常點數: {len(speed_corr['abnormal_points'])}",
            
            "\n事件對應分析:",
            f"- 事件對應率: {event_corr['correlation_rate']:.1%}",
            f"- 對應事件數: {len(event_corr['correlated_events'])}",
            f"- 未配對ATP事件: {len(event_corr['unpaired_ru_events'])}",
            f"- 未配對MMI事件: {len(event_corr['unpaired_mmi_events'])}",
            
            "\n系統一致性分析:",
            "時間覆蓋範圍:",
            f"- ATP: {system_cons['time_coverage']['ru_start']} 至 {system_cons['time_coverage']['ru_end']}",
            f"- MMI: {system_cons['time_coverage']['mmi_start']} 至 {system_cons['time_coverage']['mmi_end']}",
            f"- 重疊時間: {system_cons['time_coverage']['overlap_start']} 至 {system_cons['time_coverage']['overlap_end']}",
            
            "\nATP記錄間隔:",
            *[f"- {gap['start']} 至 {gap['end']} (間隔{gap['duration']:.1f}秒)"
              for gap in system_cons['ru_gaps']],
              
            "\nMMI記錄間隔:",
            *[f"- {gap['start']} 至 {gap['end']} (間隔{gap['duration']:.1f}秒)"
              for gap in system_cons['mmi_gaps']],
              
            "\n狀態不一致:",
            *[f"- {inc['time']}: {inc['description']}"
              for inc in system_cons['state_inconsistencies']]
        ]
        return "\n".join(lines)
