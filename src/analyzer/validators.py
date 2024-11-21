# src/analyzer/validators.py

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import numpy as np

from .exceptions import DataValidationError
from .models import RURecord

logger = logging.getLogger(__name__)

class DataValidator:
    """ATP記錄資料驗證器"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # 設定驗證參數
        self.max_speed = 200.0  # 最大合理速度(km/h)
        self.max_time_gap = 300  # 最大時間間隔(秒)
        self.min_records = 10    # 最小記錄數
        
    def validate_records(self, records: List[RURecord]):
        """驗證記錄資料的有效性
        
        Args:
            records: ATP記錄列表
            
        Raises:
            DataValidationError: 資料驗證失敗時拋出
        """
        try:
            self.logger.info(f"開始驗證 {len(records)} 筆記錄")
            
            # 1. 基本檢查
            self._validate_basic(records)
            
            # 2. 時間序列檢查
            self._validate_timestamps(records)
            
            # 3. 速度資料檢查
            self._validate_speeds(records)
            
            # 4. 位置資料檢查
            self._validate_locations(records)
            
            # 5. 事件資料檢查
            self._validate_events(records)
            
            self.logger.info("資料驗證通過")
            
        except DataValidationError:
            raise
        except Exception as e:
            self.logger.error(f"資料驗證過程發生錯誤: {e}", exc_info=True)
            raise DataValidationError(f"資料驗證失敗: {e}")
            
    def _validate_basic(self, records: List[RURecord]):
        """基本資料檢查"""
        # 檢查記錄數量
        if not records:
            raise DataValidationError("沒有記錄資料")
            
        if len(records) < self.min_records:
            raise DataValidationError(
                f"記錄數量不足: {len(records)} < {self.min_records}"
            )
            
        # 檢查必要欄位
        for i, record in enumerate(records):
            if not hasattr(record, 'log_type'):
                raise DataValidationError(f"記錄 {i} 缺少log_type欄位")
            if not hasattr(record, 'timestamp'):
                raise DataValidationError(f"記錄 {i} 缺少timestamp欄位")
            if not hasattr(record, 'data'):
                raise DataValidationError(f"記錄 {i} 缺少data欄位")
                
    def _validate_timestamps(self, records: List[RURecord]):
        """時間序列檢查"""
        timestamps = [r.timestamp for r in records]
        
        # 檢查時間順序
        if not all(t1 <= t2 for t1, t2 in zip(timestamps[:-1], timestamps[1:])):
            raise DataValidationError("時間序列不是遞增的")
            
        # 檢查時間間隔
        time_gaps = np.diff([t.timestamp() for t in timestamps])
        max_gap = np.max(time_gaps)
        
        if max_gap > self.max_time_gap:
            raise DataValidationError(
                f"時間間隔過大: {max_gap:.1f}秒 > {self.max_time_gap}秒"
            )
            
        # 檢查時間範圍合理性
        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = end_time - start_time
        
        if duration > timedelta(days=1):
            raise DataValidationError(
                f"記錄時間範圍過大: {duration.total_seconds()/3600:.1f}小時"
            )
            
    def _validate_speeds(self, records: List[RURecord]):
        """速度資料檢查"""
        speed_records = [r for r in records if r.log_type == 211]
        
        if not speed_records:
            raise DataValidationError("找不到速度記錄")
            
        speeds = [r.speed/100.0 for r in speed_records]  # 轉換為km/h
        
        # 檢查速度範圍
        max_speed = max(speeds)
        if max_speed > self.max_speed:
            raise DataValidationError(
                f"速度值超出合理範圍: {max_speed:.1f} > {self.max_speed} km/h"
            )
            
        # 檢查速度變化
        speed_diffs = np.diff(speeds)
        max_acc = max(speed_diffs)  # 最大加速度(km/h/s)
        max_dec = min(speed_diffs)  # 最大減速度(km/h/s)
        
        if max_acc > 5.0:  # 加速度過大
            raise DataValidationError(
                f"加速度異常: {max_acc:.1f} km/h/s"
            )
            
        if max_dec < -5.0:  # 減速度過大
            raise DataValidationError(
                f"減速度異常: {max_dec:.1f} km/h/s"
            )
            
    def _validate_locations(self, records: List[RURecord]):
        """位置資料檢查"""
        location_records = [r for r in records if r.log_type == 211]
        
        if not location_records:
            raise DataValidationError("找不到位置記錄")
            
        locations = [r.location/100000.0 for r in location_records]  # 轉換為km
        
        # 檢查位置遞增
        if not all(l1 <= l2 for l1, l2 in zip(locations[:-1], locations[1:])):
            raise DataValidationError("位置序列不是單調遞增的")
            
        # 檢查位置變化合理性
        location_diffs = np.diff(locations)
        max_diff = max(location_diffs)
        
        if max_diff > 1.0:  # 1km/s = 3600km/h
            raise DataValidationError(
                f"位置變化異常: {max_diff*3600:.1f} km/h"
            )
            
    def _validate_events(self, records: List[RURecord]):
        """事件資料檢查"""
        event_types = {2, 3, 91, 201}  # 有效的事件類型
        
        event_records = [r for r in records if r.log_type in event_types]
        
        # 檢查事件類型
        invalid_types = set(r.log_type for r in event_records) - event_types
        if invalid_types:
            raise DataValidationError(
                f"發現無效的事件類型: {invalid_types}"
            )
            
        # 檢查事件資料
        for record in event_records:
            if not record.data:
                raise DataValidationError(
                    f"事件記錄缺少資料: type={record.log_type}, "
                    f"time={record.timestamp}"
                )
                
            # 特定事件類型的資料長度檢查
            if record.log_type == 2 and len(record.data) < 1:
                raise DataValidationError(
                    f"ATP狀態事件資料不完整: time={record.timestamp}"
                )
            elif record.log_type == 3 and len(record.data) < 1:
                raise DataValidationError(
                    f"MMI狀態事件資料不完整: time={record.timestamp}"
                )
            elif record.log_type == 91 and len(record.data) < 1:
                raise DataValidationError(
                    f"PRS事件資料不完整: time={record.timestamp}"
                )
            elif record.log_type == 201 and len(record.data) < 8:
                raise DataValidationError(
                    f"ATP關機事件資料不完整: time={record.timestamp}"
                )
                
    def validate_configuration(self, config: Dict[str, Any]):
        """驗證分析器配置
        
        Args:
            config: 分析器配置字典
            
        Raises:
            DataValidationError: 配置驗證失敗時拋出
        """
        required_keys = {
            'chunk_size': int,
            'speed_threshold': float,
            'cache_enabled': bool,
            'parallel_enabled': bool,
            'log_level': str
        }
        
        # 檢查必要的配置項
        for key, type_ in required_keys.items():
            if key not in config:
                raise DataValidationError(f"缺少必要的配置項: {key}")
                
            if not isinstance(config[key], type_):
                raise DataValidationError(
                    f"配置項 {key} 的類型錯誤: "
                    f"期望 {type_.__name__}, "
                    f"實際 {type(config[key]).__name__}"
                )
                
        # 檢查數值範圍
        if config['chunk_size'] < 100 or config['chunk_size'] > 10000:
            raise DataValidationError(
                f"chunk_size 超出有效範圍: {config['chunk_size']}"
            )
            
        if config['speed_threshold'] < 0 or config['speed_threshold'] > 200:
            raise DataValidationError(
                f"speed_threshold 超出有效範圍: {config['speed_threshold']}"
            )
            
        # 檢查日誌等級
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if config['log_level'] not in valid_log_levels:
            raise DataValidationError(
                f"無效的日誌等級: {config['log_level']}"
            )
