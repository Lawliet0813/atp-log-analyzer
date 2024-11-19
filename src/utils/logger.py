import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import json
from pathlib import Path
from typing import Optional, Dict

class ATPLogger:
    """ATP系統日誌管理器"""
    
    def __init__(self, log_dir: str = "logs"):
        # 建立日誌目錄
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 設定日誌格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 初始化各種日誌記錄器
        self.system_logger = self._setup_logger("system")
        self.event_logger = self._setup_logger("event")
        self.error_logger = self._setup_logger("error")
        self.analysis_logger = self._setup_logger("analysis")
        
        # 記錄初始化
        self.system_logger.info("ATP記錄系統初始化完成")
        
    def _setup_logger(self, name: str) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # 檔案處理器
        file_handler = RotatingFileHandler(
            self.log_dir / f"{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(self.formatter)
        logger.addHandler(file_handler)
        
        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        logger.addHandler(console_handler)
        
        return logger
        
    def log_system_event(self, event: str, details: Optional[Dict] = None):
        """記錄系統事件"""
        if details:
            self.system_logger.info(f"{event} - {json.dumps(details, ensure_ascii=False)}")
        else:
            self.system_logger.info(event)
            
    def log_atp_event(self, event_type: str, event_data: Dict):
        """記錄ATP事件"""
        event_info = {
            'type': event_type,
            'time': datetime.now().isoformat(),
            **event_data
        }
        self.event_logger.info(json.dumps(event_info, ensure_ascii=False))
        
    def log_error(self, error: str, details: Optional[Dict] = None):
        """記錄錯誤"""
        if details:
            self.error_logger.error(f"{error} - {json.dumps(details, ensure_ascii=False)}")
        else:
            self.error_logger.error(error)
            
    def log_analysis(self, analysis_type: str, results: Dict):
        """記錄分析結果"""
        analysis_info = {
            'type': analysis_type,
            'time': datetime.now().isoformat(),
            'results': results
        }
        self.analysis_logger.info(json.dumps(analysis_info, ensure_ascii=False))
        
    def log_file_operation(self, operation: str, filename: str, status: str):
        """記錄檔案操作"""
        operation_info = {
            'operation': operation,
            'filename': filename,
            'status': status,
            'time': datetime.now().isoformat()
        }
        self.system_logger.info(f"檔案操作 - {json.dumps(operation_info, ensure_ascii=False)}")
        
    def log_user_action(self, action: str, user: str = "system"):
        """記錄使用者操作"""
        action_info = {
            'action': action,
            'user': user,
            'time': datetime.now().isoformat()
        }
        self.system_logger.info(f"使用者操作 - {json.dumps(action_info, ensure_ascii=False)}")
        
    def log_performance(self, operation: str, duration: float):
        """記錄效能資訊"""
        performance_info = {
            'operation': operation,
            'duration': duration,
            'time': datetime.now().isoformat()
        }
        self.system_logger.info(f"效能紀錄 - {json.dumps(performance_info, ensure_ascii=False)}")
        
    def log_config_change(self, setting: str, old_value: any, new_value: any):
        """記錄設定變更"""
        config_info = {
            'setting': setting,
            'old_value': old_value,
            'new_value': new_value,
            'time': datetime.now().isoformat()
        }
        self.system_logger.info(f"設定變更 - {json.dumps(config_info, ensure_ascii=False)}")
        
    def get_recent_events(self, event_type: str = None, limit: int = 100) -> list:
        """取得最近事件記錄"""
        events = []
        log_file = self.log_dir / "event.log"
        
        if not log_file.exists():
            return events
            
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-limit:]:
                try:
                    # 解析日誌行
                    parts = line.split(" - ", 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        event_data = json.loads(parts[3])
                        
                        if event_type is None or event_data.get('type') == event_type:
                            events.append({
                                'timestamp': timestamp,
                                **event_data
                            })
                except:
                    continue
                    
        return events
        
    def get_recent_errors(self, limit: int = 50) -> list:
        """取得最近錯誤記錄"""
        errors = []
        log_file = self.log_dir / "error.log"
        
        if not log_file.exists():
            return errors
            
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-limit:]:
                try:
                    # 解析日誌行
                    parts = line.split(" - ", 3)
                    if len(parts) >= 3:
                        timestamp = parts[0]
                        error_message = parts[2]
                        
                        errors.append({
                            'timestamp': timestamp,
                            'message': error_message.strip()
                        })
                except:
                    continue
                    
        return errors
        
    def get_analysis_history(self, analysis_type: str = None, limit: int = 20) -> list:
        """取得分析歷史記錄"""
        history = []
        log_file = self.log_dir / "analysis.log"
        
        if not log_file.exists():
            return history
            
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-limit:]:
                try:
                    # 解析日誌行
                    parts = line.split(" - ", 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        analysis_data = json.loads(parts[3])
                        
                        if analysis_type is None or analysis_data.get('type') == analysis_type:
                            history.append({
                                'timestamp': timestamp,
                                **analysis_data
                            })
                except:
                    continue
                    
        return history
        
    def cleanup_old_logs(self, days: int = 30):
        """清理舊日誌檔案"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log.*"):
            if os.path.getmtime(log_file) < cutoff:
                try:
                    os.remove(log_file)
                    self.system_logger.info(f"已清理舊日誌檔案: {log_file.name}")
                except Exception as e:
                    self.error_logger.error(f"清理日誌檔案失敗: {log_file.name} - {str(e)}")
                    
    def export_logs(self, export_dir: str, start_date: datetime = None, end_date: datetime = None):
        """匯出日誌"""
        export_path = Path(export_dir)
        export_path.mkdir(exist_ok=True)
        
        for log_type in ["system", "event", "error", "analysis"]:
            source_file = self.log_dir / f"{log_type}.log"
            if not source_file.exists():
                continue
                
            # 建立目標檔案名稱
            if start_date and end_date:
                target_file = export_path / f"{log_type}_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.log"
            else:
                target_file = export_path / f"{log_type}_{datetime.now().strftime('%Y%m%d')}.log"
                
            try:
                # 讀取並過濾日誌內容
                with open(source_file, 'r', encoding='utf-8') as f:
                    logs = f.readlines()
                    
                if start_date and end_date:
                    filtered_logs = []
                    for log in logs:
                        try:
                            log_time = datetime.strptime(log[:19], '%Y-%m-%d %H:%M:%S')
                            if start_date <= log_time <= end_date:
                                filtered_logs.append(log)
                        except:
                            continue
                    logs = filtered_logs
                    
                # 寫入目標檔案
                with open(target_file, 'w', encoding='utf-8') as f:
                    f.writelines(logs)
                    
                self.system_logger.info(f"已匯出日誌: {target_file.name}")
                
            except Exception as e:
                self.error_logger.error(f"匯出日誌失敗: {log_type} - {str(e)}")
                
    def set_log_level(self, level: str):
        """設定日誌等級"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        log_level = level_map.get(level.upper(), logging.INFO)
        
        for logger in [self.system_logger, self.event_logger, 
                      self.error_logger, self.analysis_logger]:
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)
                
        self.system_logger.info(f"日誌等級已設為: {level}")
