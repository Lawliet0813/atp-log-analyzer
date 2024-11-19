#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui import MainWindow, init_gui
from gui.dialogs import handle_exception

# 設定基本logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('atp_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ATP分析系統')

def setup_exception_handling():
    """設定全域異常處理"""
    def handle_global_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        logger.error("未捕獲的異常:", exc_info=(exc_type, exc_value, exc_traceback))
        handle_exception(exc_value)
        
    sys.excepthook = handle_global_exception

def init_system():
    """系統初始化"""
    try:
        # 建立必要的目錄
        Path('logs').mkdir(exist_ok=True)
        Path('reports').mkdir(exist_ok=True)
        Path('exports').mkdir(exist_ok=True)
        
        # 初始化GUI系統
        init_gui()
        
        logger.info("系統初始化完成")
        
    except Exception as e:
        logger.error(f"系統初始化失敗: {str(e)}")
        raise

def main():
    """主程式進入點"""
    try:
        # 設定異常處理
        setup_exception_handling()
        
        # 建立QApplication實例
        app = QApplication(sys.argv)
        
        # 設定應用程式資訊
        app.setApplicationName("ATP行車紀錄分析系統")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TRA")
        app.setOrganizationDomain("tra.gov.tw")
        
        # 系統初始化
        init_system()
        
        # 建立並顯示主視窗
        window = MainWindow()
        window.show()
        
        # 進入事件迴圈
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"程式啟動失敗: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
