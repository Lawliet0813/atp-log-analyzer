# src/analyzer/atp_analyzer.py

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import pandas as pd
from pathlib import Path

from .exceptions import (
    AnalysisError,
    DataValidationError,
    ProcessingError
)
from .validators import DataValidator
from .processors import (
    SpeedProcessor,
    EventProcessor, 
    LocationProcessor
)
from .models import RURecord, AnalysisResult

logger = logging.getLogger(__name__)

class ATPAnalyzer:
    """ATP行車記錄分析器
    
    主要功能:
    1. 分析速度特性
    2. 分析事件記錄
    3. 分析位置資訊
    4. 產生分析報告
    
    使用方式:
    >>> analyzer = ATPAnalyzer()
    >>> result = analyzer.analyze(records)
    >>> report = analyzer.generate_report(result)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化分析器
        
        Args:
            config: 分析器配置
        """
        self.config = config or self._get_default_config()
        self.validator = DataValidator()
        self.speed_processor = SpeedProcessor()
        self.event_processor = EventProcessor()
        self.location_processor = LocationProcessor()
        
        # 設定運算參數
        self.chunk_size = self.config.get('chunk_size', 1000)
        self.speed_threshold = self.config.get('speed_threshold', 90.0)
        
        logger.info("ATP分析器初始化完成")
        
    def _get_default_config(self) -> Dict[str, Any]:
        """取得預設配置"""
        return {
            'chunk_size': 1000,
            'speed_threshold': 90.0,
            'cache_enabled': True,
            'parallel_enabled': True,
            'log_level': 'INFO'
        }
        
    def analyze(self, records: List[RURecord], 
                callback: Optional[callable] = None) -> AnalysisResult:
        """分析ATP記錄
        
        Args:
            records: ATP記錄列表
            callback: 進度回調函數
            
        Returns:
            AnalysisResult: 分析結果
            
        Raises:
            DataValidationError: 資料驗證錯誤
            AnalysisError: 分析過程錯誤
        """
        logger.info(f"開始分析 {len(records)} 筆記錄")
        
        try:
            # 驗證資料
            self.validator.validate_records(records)
            
            # 將記錄轉換為DataFrame
            df = self._records_to_dataframe(records)
            
            # 分析速度特性
            speed_stats = self.speed_processor.analyze(
                df,
                threshold=self.speed_threshold,
                chunk_size=self.chunk_size,
                callback=callback
            )
            
            # 分析事件記錄
            event_stats = self.event_processor.analyze(
                df,
                callback=callback
            )
            
            # 分析位置資訊
            location_stats = self.location_processor.analyze(
                df,
                callback=callback
            )
            
            # 整合分析結果
            result = AnalysisResult(
                max_speed=speed_stats['max_speed'],
                avg_speed=speed_stats['avg_speed'],
                total_distance=location_stats['total_distance'],
                total_time=location_stats['total_time'],
                over_speed_count=speed_stats['over_speed_count'],
                emergency_brake_count=event_stats['emergency_brake_count'],
                atp_down_count=event_stats['atp_down_count'],
                speed_stats=speed_stats,
                location_stats=location_stats,
                event_stats=event_stats
            )
            
            logger.info("分析完成")
            return result
            
        except DataValidationError as e:
            logger.error(f"資料驗證失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"分析過程發生錯誤: {e}", exc_info=True)
            raise AnalysisError(f"分析失敗: {e}")
            
    def _records_to_dataframe(self, records: List[RURecord]) -> pd.DataFrame:
        """將記錄轉換為DataFrame
        
        Args:
            records: ATP記錄列表
            
        Returns:
            pd.DataFrame: 記錄DataFrame
        """
        data = []
        for record in records:
            row = {
                'timestamp': record.timestamp,
                'log_type': record.log_type,
                'location': record.location / 100000.0,  # 轉換為km
                'speed': record.speed / 100.0,  # 轉換為km/h
                'data': record.data
            }
            data.append(row)
            
        return pd.DataFrame(data)
        
    def generate_report(self, result: AnalysisResult, 
                       report_type: str = 'summary') -> Dict[str, Any]:
        """產生分析報告
        
        Args:
            result: 分析結果
            report_type: 報告類型 (summary/detailed)
            
        Returns:
            Dict: 報告內容
        """
        logger.info(f"產生{report_type}報告")
        
        if report_type == 'summary':
            return {
                '基本統計': {
                    '最高速度': f"{result.max_speed:.1f} km/h",
                    '平均速度': f"{result.avg_speed:.1f} km/h",
                    '總距離': f"{result.total_distance:.1f} km",
                    '總時間': str(result.total_time),
                    '超速次數': result.over_speed_count,
                    '緊急煞車次數': result.emergency_brake_count,
                    'ATP關機次數': result.atp_down_count
                },
                '速度分布': result.speed_stats['速度分布'],
                '重要事件': result.event_stats['重要事件'][:5]
            }
        else:
            return {
                '基本統計': {
                    '最高速度': f"{result.max_speed:.1f} km/h",
                    '平均速度': f"{result.avg_speed:.1f} km/h",
                    '總距離': f"{result.total_distance:.1f} km",
                    '總時間': str(result.total_time),
                    '超速次數': result.over_speed_count,
                    '緊急煞車次數': result.emergency_brake_count,
                    'ATP關機次數': result.atp_down_count
                },
                '速度分析': {
                    '速度分布': result.speed_stats['速度分布'],
                    '加減速分析': result.speed_stats['加減速分析']
                },
                '位置分析': {
                    '站間運行時間': result.location_stats['站間運行時間'],
                    '位置分布': result.location_stats['位置分布']
                },
                '事件分析': {
                    '事件統計': result.event_stats['事件統計'],
                    '重要事件': result.event_stats['重要事件'],
                    '異常事件': result.event_stats['異常事件']
                }
            }
            
    def export_results(self, result: AnalysisResult,
                      export_dir: Path,
                      formats: List[str] = ['xlsx', 'csv']) -> Dict[str, Path]:
        """匯出分析結果
        
        Args:
            result: 分析結果
            export_dir: 匯出目錄
            formats: 匯出格式列表
            
        Returns:
            Dict[str, Path]: 匯出檔案路徑
        """
        logger.info(f"匯出分析結果至 {export_dir}")
        
        export_dir.mkdir(parents=True, exist_ok=True)
        exported_files = {}
        
        try:
            # 準備匯出資料
            export_data = {
                '基本統計': pd.DataFrame([{
                    '項目': k,
                    '數值': v
                } for k, v in result.get_basic_stats().items()]),
                
                '速度分析': pd.DataFrame([{
                    '區間': k,
                    '次數': v
                } for k, v in result.speed_stats['速度分布'].items()]),
                
                '事件統計': pd.DataFrame([{
                    '事件類型': k,
                    '發生次數': v
                } for k, v in result.event_stats['事件統計'].items()])
            }
            
            # 依格式匯出
            for fmt in formats:
                if fmt == 'xlsx':
                    excel_path = export_dir / 'analysis_result.xlsx'
                    with pd.ExcelWriter(excel_path) as writer:
                        for sheet_name, df in export_data.items():
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    exported_files['excel'] = excel_path
                    
                elif fmt == 'csv':
                    csv_dir = export_dir / 'csv'
                    csv_dir.mkdir(exist_ok=True)
                    for name, df in export_data.items():
                        csv_path = csv_dir / f'{name}.csv'
                        df.to_csv(csv_path, index=False)
                        exported_files[f'csv_{name}'] = csv_path
                        
            logger.info(f"匯出完成: {exported_files}")
            return exported_files
            
        except Exception as e:
            logger.error(f"匯出失敗: {e}", exc_info=True)
            raise ProcessingError(f"匯出結果失敗: {e}")
