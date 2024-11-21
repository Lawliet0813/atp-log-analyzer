# src/analyzer/templates.py

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .exceptions import ExportError

logger = logging.getLogger(__name__)

class TemplateManager:
    """範本管理器"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """初始化範本管理器
        
        Args:
            template_dir: 範本目錄路徑(可選)
        """
        self.template_dir = template_dir or Path(__file__).parent / 'resources' / 'templates'
        self._setup_environment()
        
    def _setup_environment(self):
        """設定Jinja2環境"""
        try:
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # 添加自定義過濾器
            self.env.filters.update({
                'format_number': self._format_number,
                'format_time': self._format_time
            })
            
            logger.info(f"範本環境已初始化: {self.template_dir}")
            
        except Exception as e:
            logger.error(f"範本環境初始化失敗: {e}", exc_info=True)
            raise ExportError(f"範本環境初始化失敗: {e}")
            
    def render_report(self, data: Dict[str, Any], output_path: Path) -> None:
        """渲染完整報表
        
        Args:
            data: 報表資料
            output_path: 輸出檔案路徑
        """
        try:
            # 載入主要範本
            template = self.env.get_template('report_template.html')
            
            # 載入其他範本內容
            chart_scripts = self._load_template('chart_scripts.html')
            interactive_scripts = self._load_template('interactive_scripts.html')
            styles = self._load_template('print_styles.html')
            
            # 合併所有範本內容
            context = {
                **data,
                'chart_scripts': chart_scripts,
                'interactive_scripts': interactive_scripts,
                'styles': styles
            }
            
            # 渲染範本
            content = template.render(**context)
            
            # 寫入檔案
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            
            logger.info(f"HTML報表已生成: {output_path}")
            
        except Exception as e:
            logger.error(f"HTML報表生成失敗: {e}", exc_info=True)
            raise ExportError(f"HTML報表生成失敗: {e}")
            
    def _load_template(self, name: str) -> str:
        """載入範本檔案內容
        
        Args:
            name: 範本檔案名稱
            
        Returns:
            str: 範本內容
        """
        try:
            template_path = self.template_dir / name
            return template_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"載入範本失敗 {name}: {e}")
            return ""
            
    @staticmethod
    def _format_number(value: float, precision: int = 2) -> str:
        """格式化數字
        
        Args:
            value: 數值
            precision: 精確度
            
        Returns:
            str: 格式化後的字串
        """
        try:
            return f"{float(value):.{precision}f}"
        except (ValueError, TypeError):
            return str(value)
            
    @staticmethod
    def _format_time(value: Any) -> str:
        """格式化時間
        
        Args:
            value: 時間值
            
        Returns:
            str: 格式化後的字串
        """
        try:
            if hasattr(value, 'strftime'):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            return str(value)
        except Exception:
            return str(value)

class ReportBuilder:
    """報表建構器"""
    
    def __init__(self, template_manager: TemplateManager):
        """初始化報表建構器
        
        Args:
            template_manager: 範本管理器實例
        """
        self.template_manager = template_manager
        self.data = {
            'speed_data': {},
            'speed_dist_data': {},
            'event_data': {},
            'stats': {},
            'events': []
        }
        
    def add_speed_data(self, speeds: Dict[str, Any]):
        """添加速度資料"""
        self.data['speed_data'] = speeds
        
    def add_speed_distribution(self, distribution: Dict[str, Any]):
        """添加速度分布資料"""
        self.data['speed_dist_data'] = distribution
        
    def add_event_data(self, events: Dict[str, Any]):
        """添加事件資料"""
        self.data['event_data'] = events
        
    def add_statistics(self, stats: Dict[str, Any]):
        """添加統計資料"""
        self.data['stats'] = stats
        
    def add_events(self, events: list):
        """添加事件列表"""
        self.data['events'] = events
        
    def build(self, output_path: Path) -> None:
        """建構並輸出報表
        
        Args:
            output_path: 輸出檔案路徑
        """
        self.template_manager.render_report(self.data, output_path)

def create_report(data: Dict[str, Any], output_path: Path):
    """建立報表的便捷函數
    
    Args:
        data: 報表資料
        output_path: 輸出檔案路徑
    """
    template_manager = TemplateManager()
    builder = ReportBuilder(template_manager)
    
    # 添加資料
    builder.add_speed_data(data.get('speed_data', {}))
    builder.add_speed_distribution(data.get('speed_dist_data', {}))
    builder.add_event_data(data.get('event_data', {}))
    builder.add_statistics(data.get('stats', {}))
    builder.add_events(data.get('events', []))
    
    # 建構報表
    builder.build(output_path)
