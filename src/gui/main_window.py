# src/gui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QGroupBox, QFormLayout,
                           QTableWidget, QHeaderView, QFileDialog, QTableWidgetItem,
                           QMessageBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from datetime import datetime
import pandas as pd
from ru_parser.ru_file import RUParser
from analyzer.atp_analyzer import ATPAnalyzer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ru_parser = RUParser()
        self.analyzer = ATPAnalyzer()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("ATP記錄分析系統")
        self.setGeometry(100, 100, 1600, 900)
        
        # 主要元件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 上方工具列
        toolbar = self.create_toolbar()
        main_layout.addLayout(toolbar)
        
        # 速度曲線圖
        self.create_speed_plot()
        main_layout.addWidget(self.speed_plot)
        
        # 下方事件列表
        self.create_event_table()
        main_layout.addWidget(self.event_table)
        
        # 設定佈局比例
        main_layout.setStretch(0, 1)  # 工具列
        main_layout.setStretch(1, 4)  # 速度圖
        main_layout.setStretch(2, 2)  # 事件列表
        
    def create_toolbar(self):
        """建立工具列"""
        toolbar = QHBoxLayout()
        
        # 檔案資訊群組
        file_group = QGroupBox("檔案資訊")
        file_layout = QFormLayout()
        
        self.train_label = QLabel()
        self.date_label = QLabel()
        self.driver_label = QLabel()
        
        file_layout.addRow("列車號:", self.train_label)
        file_layout.addRow("日期:", self.date_label)
        file_layout.addRow("司機員:", self.driver_label)
        
        file_group.setLayout(file_layout)
        toolbar.addWidget(file_group)
        
        # 分析工具群組
        tool_group = QGroupBox("分析工具")
        tool_layout = QHBoxLayout()
        
        self.load_button = QPushButton("載入記錄檔")
        self.analyze_button = QPushButton("開始分析")
        self.export_button = QPushButton("匯出報表")
        
        self.load_button.clicked.connect(self.on_load_file)
        self.analyze_button.clicked.connect(self.on_analyze)
        self.export_button.clicked.connect(self.on_export)
        
        tool_layout.addWidget(self.load_button)
        tool_layout.addWidget(self.analyze_button)
        tool_layout.addWidget(self.export_button)
        
        tool_group.setLayout(tool_layout)
        toolbar.addWidget(tool_group)
        
        return toolbar

    def create_speed_plot(self):
        """建立速度曲線圖"""
        self.speed_plot = pg.PlotWidget()
        self.speed_plot.setBackground('black')
        self.speed_plot.showGrid(x=True, y=True)
        
        # 設定座標軸
        self.speed_plot.getAxis('left').setLabel('速度 (km/h)')
        self.speed_plot.getAxis('bottom').setLabel('時間')
        
        # 設定Y軸刻度
        y_ticks = [(i, str(i)) for i in range(0, 121, 20)]
        self.speed_plot.getAxis('left').setTicks([y_ticks])
        
        # 設定Y軸範圍
        self.speed_plot.setYRange(0, 120)
        
        # 新增曲線
        self.speed_curve = self.speed_plot.plot(name='實際速度', pen=pg.mkPen('g', width=2))
        self.limit_curve = self.speed_plot.plot(name='速限', pen=pg.mkPen('r', width=2))
        self.signal_curve = self.speed_plot.plot(name='號誌', pen=pg.mkPen('c', width=2))
        
        # 新增圖例
        self.speed_plot.addLegend()

    def create_event_table(self):
        """建立事件列表"""
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(4)
        self.event_table.setHorizontalHeaderLabels(['時間', '事件', '位置', '狀態'])
        
        # 設定欄位寬度
        header = self.event_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
    
    def on_load_file(self):
        """載入RU檔案"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "選擇ATP記錄檔",
            "",
            "RU Files (*.RU);;All Files (*)"
        )
        
        if filename:
            try:
                # 解析RU檔案
                self.ru_parser.parse_file(filename)
                
                # 更新檔案資訊
                self.update_file_info()
                
                # 更新速度曲線
                self.update_speed_plot()
                
                # 更新事件列表 
                self.update_event_table()
                
                # 啟用分析按鈕
                self.analyze_button.setEnabled(True)
                self.export_button.setEnabled(True)
                
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"檔案載入失敗: {str(e)}")
    
    def update_file_info(self):
        """更新檔案資訊"""
        if self.ru_parser.header:
            self.train_label.setText(self.ru_parser.header.train_no)
            self.date_label.setText(self.ru_parser.header.date.strftime("%Y-%m-%d"))
            self.driver_label.setText(self.ru_parser.header.driver_id)
    
    def update_speed_plot(self):
        """更新速度曲線圖"""
        # 取得速度資料
        times, speeds = self.ru_parser.get_speed_data()
        
        if times and speeds:
            # 轉換時間為相對時間(秒)
            t0 = times[0]
            rel_times = [t - t0 for t in times]
            
            # 更新速度曲線
            self.speed_plot.speed_curve.setData(rel_times, speeds)
            
            # 設定X軸範圍
            self.speed_plot.setXRange(0, rel_times[-1])
            
            # 更新X軸標籤格式
            def format_time(x):
                seconds = int(x)
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
            self.speed_plot.getAxis('bottom').setTicks([
                [(i, format_time(i)) for i in range(0, int(rel_times[-1]), 600)]
            ])
    
    def update_event_table(self):
        """更新事件列表"""
        # 清空表格
        self.event_table.setRowCount(0)
        
        # 取得事件資料
        events = self.ru_parser.get_events()
        
        # 填入事件資料
        for event in events:
            row = self.event_table.rowCount()
            self.event_table.insertRow(row)
            
            # 時間
            time_item = QTableWidgetItem(
                event['time'].strftime("%H:%M:%S")
            )
            self.event_table.setItem(row, 0, time_item)
            
            # 事件
            event_item = QTableWidgetItem(event['event'])
            self.event_table.setItem(row, 1, event_item)
            
            # 位置
            location_item = QTableWidgetItem(
                f"{event['location']/100000:.2f}km"
            )
            self.event_table.setItem(row, 2, location_item)
            
            # 狀態
            status_item = QTableWidgetItem(event['status'])
            self.event_table.setItem(row, 3, status_item)
    
    def on_analyze(self):
        """分析資料"""
        try:
            from analyzer.atp_analyzer import ATPAnalyzer
            
            # 建立分析器
            analyzer = ATPAnalyzer()
            
            # 執行分析
            result = analyzer.analyze(self.ru_parser.records)
            
            # 顯示分析結果
            msg = [
                "基本統計:",
                f"最高速度: {result.max_speed:.1f} km/h",
                f"平均速度: {result.avg_speed:.1f} km/h",
                f"總距離: {result.total_distance:.1f} km",
                f"總時間: {result.total_time}",
                f"超速次數: {result.over_speed_count}次",
                f"緊急煞車: {result.emergency_brake_count}次",
                f"ATP關機: {result.atp_down_count}次",
                "",
                "速度分布:",
                *[f"{k}: {v}次" for k,v in result.speed_stats['速度分布'].items()],
                "",
                "加減速分析:",
                *[f"{k}: {v}" for k,v in result.speed_stats['加減速分析'].items()],
                "",
                "站間運行時間:",
                *[f"{k}: {v}" for k,v in result.location_stats['站間運行時間'].items()]
            ]
            
            QMessageBox.information(self, "分析結果", "\n".join(msg))
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"分析失敗: {str(e)}")
    
    def on_export(self):
        """匯出報表"""
        try:
            filename, filetype = QFileDialog.getSaveFileName(
                self,
                "儲存報表",
                "",
                "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if not filename:
                return
                
            # 準備報表資料
            report_data = {
                '時間': [],
                '速度(km/h)': [],
                '位置(km)': []
            }
            
            # 填入速度記錄
            for record in self.ru_parser.records:
                if record.log_type == 211:
                    report_data['時間'].append(record.timestamp)
                    report_data['速度(km/h)'].append(record.speed/100.0)
                    report_data['位置(km)'].append(record.location/100000.0)
            
            # 轉換為DataFrame
            df = pd.DataFrame(report_data)
            
            # 依檔案類型匯出
            if filename.endswith('.xlsx'):
                df.to_excel(filename, index=False)
            else:
                df.to_csv(filename, index=False)
            
            QMessageBox.information(self, "成功", "報表匯出完成")
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"報表匯出失敗: {str(e)}")
