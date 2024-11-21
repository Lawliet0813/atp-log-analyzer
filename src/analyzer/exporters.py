# src/analyzer/exporters.py

import logging
from pathlib import Path
from typing import Dict, Any, List, Union, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import json
import xlsxwriter
from .exceptions import ExportError
from .models import AnalysisResult, EventRecord, SpeedProfile
from .utils import format_number, format_time

logger = logging.getLogger(__name__)

class BaseExporter:
    """匯出器基礎類別"""
    
    def __init__(self, output_dir: Union[str, Path]):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def export(self, result: AnalysisResult):
        """匯出分析結果"""
        raise NotImplementedError
        
    def _ensure_directory(self, directory: Path):
        """確保目錄存在"""
        directory.mkdir(parents=True, exist_ok=True)
        
    def _get_timestamp(self) -> str:
        """取得時間戳記"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

class ExcelExporter(BaseExporter):
    """Excel報表匯出器"""
    
    def export(self, result: AnalysisResult, 
              filename: Optional[str] = None) -> Path:
        """匯出Excel報表
        
        Args:
            result: 分析結果
            filename: 檔案名稱(可選)
            
        Returns:
            Path: 匯出檔案路徑
        """
        try:
            if filename is None:
                filename = f"ATP分析報告_{self._get_timestamp()}.xlsx"
                
            filepath = self.output_dir / filename
            
            # 建立Excel檔案
            with xlsxwriter.Workbook(str(filepath)) as workbook:
                # 設定格式
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center',
                    'bg_color': '#4F81BD',
                    'font_color': 'white'
                })
                
                header_format = workbook.add_format({
                    'bold': True,
                    'font_size': 11,
                    'align': 'center',
                    'bg_color': '#D0D8E8'
                })
                
                cell_format = workbook.add_format({
                    'font_size': 11,
                    'align': 'center'
                })
                
                # 基本資訊工作表
                self._create_summary_sheet(
                    workbook, result, 
                    title_format, header_format, cell_format
                )
                
                # 速度分析工作表
                self._create_speed_sheet(
                    workbook, result,
                    title_format, header_format, cell_format
                )
                
                # 事件分析工作表
                self._create_event_sheet(
                    workbook, result,
                    title_format, header_format, cell_format
                )
                
                # 位置分析工作表
                self._create_location_sheet(
                    workbook, result,
                    title_format, header_format, cell_format
                )
                
            self.logger.info(f"Excel報表已匯出至: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"匯出Excel報表失敗: {e}", exc_info=True)
            raise ExportError(f"匯出Excel報表失敗: {e}")
            
    def _create_summary_sheet(self, workbook: xlsxwriter.Workbook,
                            result: AnalysisResult,
                            title_format, header_format, cell_format):
        """建立摘要工作表"""
        worksheet = workbook.add_worksheet('基本資訊')
        
        # 設定欄寬
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 30)
        
        # 標題
        worksheet.merge_range('A1:B1', 'ATP行車記錄分析報告', title_format)
        
        # 基本統計資料
        row = 2
        worksheet.write(row, 0, '分析項目', header_format)
        worksheet.write(row, 1, '數值', header_format)
        
        stats = result.get_basic_stats()
        for item, value in stats.items():
            row += 1
            worksheet.write(row, 0, item, cell_format)
            worksheet.write(row, 1, value, cell_format)
            
    def _create_speed_sheet(self, workbook: xlsxwriter.Workbook,
                           result: AnalysisResult,
                           title_format, header_format, cell_format):
        """建立速度分析工作表"""
        worksheet = workbook.add_worksheet('速度分析')
        
        # 設定欄寬
        worksheet.set_column('A:B', 15)
        
        # 標題
        worksheet.merge_range('A1:B1', '速度分布統計', title_format)
        
        # 速度分布
        row = 2
        worksheet.write(row, 0, '速度區間', header_format)
        worksheet.write(row, 1, '次數', header_format)
        
        for interval, count in result.speed_stats['速度分布'].items():
            row += 1
            worksheet.write(row, 0, interval, cell_format)
            worksheet.write(row, 1, count, cell_format)
            
        # 加減速分析
        row += 2
        worksheet.merge_range(f'A{row}:B{row}', '加減速分析', title_format)
        
        row += 1
        worksheet.write(row, 0, '分析項目', header_format)
        worksheet.write(row, 1, '數值', header_format)
        
        for item, value in result.speed_stats['加減速分析'].items():
            row += 1
            worksheet.write(row, 0, item, cell_format)
            worksheet.write(row, 1, value, cell_format)
            
    def _create_event_sheet(self, workbook: xlsxwriter.Workbook,
                           result: AnalysisResult,
                           title_format, header_format, cell_format):
        """建立事件分析工作表"""
        worksheet = workbook.add_worksheet('事件分析')
        
        # 設定欄寬
        worksheet.set_column('A:D', 20)
        
        # 事件統計
        worksheet.merge_range('A1:B1', '事件統計', title_format)
        
        row = 2
        worksheet.write(row, 0, '事件類型', header_format)
        worksheet.write(row, 1, '發生次數', header_format)
        
        for event_type, count in result.event_stats['事件統計'].items():
            row += 1
            worksheet.write(row, 0, event_type, cell_format)
            worksheet.write(row, 1, count, cell_format)
            
        # 重要事件列表
        row += 2
        worksheet.merge_range(f'A{row}:D{row}', '重要事件列表', title_format)
        
        row += 1
        worksheet.write(row, 0, '時間', header_format)
        worksheet.write(row, 1, '事件類型', header_format)
        worksheet.write(row, 2, '位置', header_format)
        worksheet.write(row, 3, '描述', header_format)
        
        for event in result.event_stats['重要事件']:
            row += 1
            worksheet.write(row, 0, format_time(event['time']), cell_format)
            worksheet.write(row, 1, event['type'], cell_format)
            worksheet.write(row, 2, f"{event.get('location', 0):.3f}km", cell_format)
            worksheet.write(row, 3, event.get('description', ''), cell_format)
            
    def _create_location_sheet(self, workbook: xlsxwriter.Workbook,
                             result: AnalysisResult,
                             title_format, header_format, cell_format):
        """建立位置分析工作表"""
        worksheet = workbook.add_worksheet('位置分析')
        
        # 設定欄寬
        worksheet.set_column('A:B', 20)
        
        # 站間運行時間
        worksheet.merge_range('A1:B1', '站間運行時間', title_format)
        
        row = 2
        worksheet.write(row, 0, '區間', header_format)
        worksheet.write(row, 1, '時間', header_format)
        
        for section, time in result.location_stats['站間運行時間'].items():
            row += 1
            worksheet.write(row, 0, section, cell_format)
            worksheet.write(row, 1, time, cell_format)
            
        # 位置分布
        row += 2
        worksheet.merge_range(f'A{row}:B{row}', '位置分布統計', title_format)
        
        row += 1
        worksheet.write(row, 0, '位置區間', header_format)
        worksheet.write(row, 1, '次數', header_format)
        
        for interval, count in result.location_stats['位置分布'].items():
            row += 1
            worksheet.write(row, 0, interval, cell_format)
            worksheet.write(row, 1, count, cell_format)

class CSVExporter(BaseExporter):
    """CSV報表匯出器"""
    
    def export(self, result: AnalysisResult) -> Dict[str, Path]:
        """匯出CSV報表
        
        Args:
            result: 分析結果
            
        Returns:
            Dict[str, Path]: CSV檔案路徑字典
        """
        try:
            timestamp = self._get_timestamp()
            csv_dir = self.output_dir / f"csv_{timestamp}"
            csv_dir.mkdir(parents=True, exist_ok=True)
            
            exported_files = {}
            
            # 匯出基本統計
            basic_stats = pd.DataFrame([
                {'項目': k, '數值': v}
                for k, v in result.get_basic_stats().items()
            ])
            basic_stats_path = csv_dir / 'basic_stats.csv'
            basic_stats.to_csv(basic_stats_path, index=False, encoding='utf-8')
            exported_files['basic_stats'] = basic_stats_path
            
            # 匯出速度分布
            speed_dist = pd.DataFrame([
                {'區間': k, '次數': v}
                for k, v in result.speed_stats['速度分布'].items()
            ])
            speed_dist_path = csv_dir / 'speed_distribution.csv'
            speed_dist.to_csv(speed_dist_path, index=False, encoding='utf-8')
            exported_files['speed_distribution'] = speed_dist_path
            
            # 匯出事件統計
            event_stats = pd.DataFrame([
                {'事件類型': k, '次數': v}
                for k, v in result.event_stats['事件統計'].items()
            ])
            event_stats_path = csv_dir / 'event_stats.csv'
            event_stats.to_csv(event_stats_path, index=False, encoding='utf-8')
            exported_files['event_stats'] = event_stats_path
            
            # 匯出位置統計
            location_stats = pd.DataFrame([
                {'區間': k, '運行時間': v}
                for k, v in result.location_stats['站間運行時間'].items()
            ])
            location_stats_path = csv_dir / 'location_stats.csv'
            location_stats.to_csv(location_stats_path, index=False, encoding='utf-8')
            exported_files['location_stats'] = location_stats_path
            
            self.logger.info(f"CSV報表已匯出至: {csv_dir}")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"匯出CSV報表失敗: {e}", exc_info=True)
            raise ExportError(f"匯出CSV報表失敗: {e}")

class JSONExporter(BaseExporter):
    """JSON報表匯出器"""
    
    def export(self, result: AnalysisResult) -> Path:
        """匯出JSON報表
        
        Args:
            result: 分析結果
            
        Returns:
            Path: JSON檔案路徑
        """
        try:
            filepath = self.output_dir / f"analysis_result_{self._get_timestamp()}.json"
            
            with filepath.open('w', encoding='utf-8') as f:
                json.dump(
                    result.to_dict(),
                    f,
                    ensure_ascii=False,
                    indent=2
                )
                
            self.logger.info(f"JSON報表已匯出至: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"匯出JSON報表失敗: {e}", exc_info=True)
            raise ExportError(f"匯出JSON報表失敗: {e}")

def create_exporter(format_type: str, output_dir: Union[str, Path]) -> BaseExporter:
    """建立匯出器實例
    
    Args:
        format_type: 匯出格式類型('excel'/'csv'/'json')
        output_dir: 輸出目錄
        
    Returns:
        BaseExporter: 匯出器實例
    """
    exporters = {
        'excel': ExcelExporter,
        'csv': CSVExporter,
        'json': JSONExporter
    }
    
    exporter_class = exporters.get(format_type.lower())
    if not exporter_class:
        raise ValueError(f"不支援的匯出格式: {format_type}")
        
    return exporter_class(output_dir)
