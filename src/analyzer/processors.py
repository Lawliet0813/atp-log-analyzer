# src/analyzer/processors.py

import logging
from typing import Dict, Any, Optional, List
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from .exceptions import ProcessingError

logger = logging.getLogger(__name__)

class BaseProcessor:
    """處理器基礎類別"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def _update_progress(self, current: int, total: int, 
                        callback: Optional[callable] = None):
        """更新進度"""
        if callback:
            progress = int(current * 100 / total)
            callback(progress)
            
class SpeedProcessor(BaseProcessor):
    """速度資料處理器"""
    
    def analyze(self, df: pd.DataFrame,
               threshold: float = 90.0,
               chunk_size: int = 1000,
               callback: Optional[callable] = None) -> Dict[str, Any]:
        """分析速度特性
        
        Args:
            df: 記錄DataFrame
            threshold: 速度閾值(km/h)
            chunk_size: 分批大小
            callback: 進度回調函數
            
        Returns:
            Dict: 速度分析結果
        """
        try:
            # 篩選速度記錄
            speed_df = df[df['log_type'] == 211].copy()
            
            if speed_df.empty:
                raise ProcessingError("找不到速度記錄")
                
            # 基本統計
            stats = {
                'max_speed': speed_df['speed'].max(),
                'avg_speed': speed_df['speed'].mean(),
                'over_speed_count': len(speed_df[speed_df['speed'] > threshold])
            }
            
            # 速度分布
            bins = [0, 20, 40, 60, 80, 100, 120]
            hist, _ = np.histogram(speed_df['speed'], bins=bins)
            stats['速度分布'] = {
                f"{bins[i]}-{bins[i+1]}km/h": int(count)
                for i, count in enumerate(hist)
            }
            
            # 加減速分析
            speed_arr = speed_df['speed'].values
            time_arr = speed_df['timestamp'].astype(np.int64) // 10**9
            
            time_diffs = np.diff(time_arr)
            speed_diffs = np.diff(speed_arr)
            
            # 避免除以零
            mask = time_diffs > 0
            accelerations = np.zeros_like(time_diffs)
            accelerations[mask] = speed_diffs[mask] / time_diffs[mask]
            
            stats['加減速分析'] = {
                '最大加速度': f"{np.max(accelerations):.2f} km/h/s",
                '最大減速度': f"{abs(np.min(accelerations)):.2f} km/h/s",
                '平均加速度': f"{np.mean(accelerations[accelerations > 0]):.2f} km/h/s",
                '平均減速度': f"{abs(np.mean(accelerations[accelerations < 0])):.2f} km/h/s"
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"速度分析失敗: {e}", exc_info=True)
            raise ProcessingError(f"速度分析失敗: {e}")

class EventProcessor(BaseProcessor):
    """事件資料處理器"""
    
    def analyze(self, df: pd.DataFrame,
               callback: Optional[callable] = None) -> Dict[str, Any]:
        """分析事件記錄
        
        Args:
            df: 記錄DataFrame
            callback: 進度回調函數
            
        Returns:
            Dict: 事件分析結果
        """
        try:
            # 事件統計
            event_counts = {}
            emergency_brake_count = 0
            atp_down_count = 0
            important_events = []
            abnormal_events = []
            
            # 處理每種事件類型
            for log_type in [2, 3, 91, 201]:
                events = df[df['log_type'] == log_type]
                
                # 更新進度
                self._update_progress(log_type, 201, callback)
                
                for _, event in events.iterrows():
                    event_info = self._parse_event(event)
                    
                    if event_info:
                        # 更新計數
                        event_type = event_info['type']
                        event_counts[event_type] = event_counts.get(event_type, 0) + 1
                        
                        # 檢查特殊事件
                        if event_info.get('is_emergency'):
                            emergency_brake_count += 1
                            important_events.append(event_info)
                        if event_info.get('is_atp_down'):
                            atp_down_count += 1
                            important_events.append(event_info)
                        if event_info.get('is_abnormal'):
                            abnormal_events.append(event_info)
            
            return {
                'event_counts': event_counts,
                'emergency_brake_count': emergency_brake_count,
                'atp_down_count': atp_down_count,
                '事件統計': event_counts,
                '重要事件': important_events,
                '異常事件': abnormal_events
            }
            
        except Exception as e:
            self.logger.error(f"事件分析失敗: {e}", exc_info=True)
            raise ProcessingError(f"事件分析失敗: {e}")
            
    def _parse_event(self, event) -> Optional[Dict[str, Any]]:
        """解析事件資訊"""
        try:
            if event['log_type'] == 2:  # ATP狀態
                data = event['data']
                status_code = data[0] if len(data) > 0 else None
                is_emergency = status_code == 2  # 緊急煞車
                
                return {
                    'type': 'ATP狀態變更',
                    'time': event['timestamp'],
                    'status': self._get_atp_status(status_code),
                    'is_emergency': is_emergency,
                    'is_abnormal': status_code in [2, 3, 4]  # 緊急煞車、故障、異常
                }
                
            elif event['log_type'] == 3:  # MMI狀態
                data = event['data']
                status_code = data[0] if len(data) > 0 else None
                
                return {
                    'type': 'MMI狀態變更',
                    'time': event['timestamp'],
                    'status': self._get_mmi_status(status_code),
                    'is_abnormal': status_code in [1, 2, 3]  # 顯示異常、按鍵故障、記憶體不足
                }
                
            elif event['log_type'] == 91:  # PRS事件
                data = event['data']
                event_code = data[0] if len(data) > 0 else None
                
                return {
                    'type': 'PRS事件',
                    'time': event['timestamp'],
                    'event': self._get_prs_event(event_code),
                    'is_abnormal': event_code in [3, 4, 5]  # CRC錯誤、編號不符、通訊逾時
                }
                
            elif event['log_type'] == 201:  # ATP關機
                return {
                    'type': 'ATP關機',
                    'time': event['timestamp'],
                    'is_atp_down': True
                }
                
        except Exception as e:
            self.logger.warning(f"事件解析失敗: {e}")
            return None
            
    def _get_atp_status(self, code: int) -> str:
        """取得ATP狀態描述"""
        status_map = {
            0: "正常",
            1: "常用緊軔",
            2: "緊急緊軔",
            3: "系統故障",
            4: "通訊異常",
            5: "感應子異常"
        }
        return status_map.get(code, f"未知狀態({code})")
        
    def _get_mmi_status(self, code: int) -> str:
        """取得MMI狀態描述"""
        status_map = {
            0: "正常",
            1: "顯示異常",
            2: "按鍵故障",
            3: "記憶體不足",
            4: "通訊中斷",
            5: "系統重啟"
        }
        return status_map.get(code, f"未知狀態({code})")
        
    def _get_prs_event(self, code: int) -> str:
        """取得PRS事件描述"""
        event_map = {
            0: "通訊正常",
            1: "列車編號設定",
            2: "CRC錯誤",
            3: "通訊逾時",
            4: "編號不符",
            5: "連線中斷",
            6: "連線恢復"
        }
        return event_map.get(code, f"未知事件({code})")

class LocationProcessor(BaseProcessor):
    """位置資料處理器"""
    
    def analyze(self, df: pd.DataFrame,
               callback: Optional[callable] = None) -> Dict[str, Any]:
        """分析位置資訊
        
        Args:
            df: 記錄DataFrame
            callback: 進度回調函數
            
        Returns:
            Dict: 位置分析結果
        """
        try:
            # 篩選位置記錄
            loc_df = df[df['log_type'] == 211].copy()
            
            if loc_df.empty:
                raise ProcessingError("找不到位置記錄")
                
            # 計算總距離
            total_distance = loc_df['location'].max() - loc_df['location'].min()
            
            # 計算總時間
            total_time = loc_df['timestamp'].max() - loc_df['timestamp'].min()
            
            # 位置分布
            bins = np.arange(0, loc_df['location'].max() + 10, 10)
            hist, _ = np.histogram(loc_df['location'], bins=bins)
            location_dist = {
                f"{bins[i]:.0f}-{bins[i+1]:.0f}km": int(count)
                for i, count in enumerate(hist)
            }
            
            # 計算站間運行時間
            station_times = self._calculate_station_times(df)
            
            return {
                'total_distance': total_distance,
                'total_time': total_time,
                '位置分布': location_dist,
                '站間運行時間': station_times
            }
            
        except Exception as e:
            self.logger.error(f"位置分析失敗: {e}", exc_info=True)
            raise ProcessingError(f"位置分析失敗: {e}")
            
    def _calculate_station_times(self, df: pd.DataFrame) -> Dict[str, str]:
        """計算站間運行時間"""
        station_times = {}
        current_station = None
        station_entry_time = None
        
        # 篩選PRS事件(到站)
        station_events = df[df['log_type'] == 91].sort_values('timestamp')
        
        for _, event in station_events.iterrows():
            try:
                station_name = event['data'].decode('ascii').strip()
                if not station_name:
                    continue
                    
                if current_station and station_entry_time:
                    duration = event['timestamp'] - station_entry_time
                    key = f"{current_station}->{station_name}"
                    station_times[key] = f"{duration.total_seconds()/60:.1f}分鐘"
                    
                current_station = station_name
                station_entry_time = event['timestamp']
                
            except Exception as e:
                self.logger.warning(f"站點資料解析失敗: {e}")
                continue
                
        return station_times
