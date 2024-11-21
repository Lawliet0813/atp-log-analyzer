#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QLabel, QLineEdit, QPushButton, QComboBox,
                           QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox,
                           QTabWidget, QWidget, QFormLayout, QDialogButtonBox,
                           QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import json
from pathlib import Path
from typing import Dict, Optional

class BaseDialog(QDialog):
    """對話框基礎類別"""
    
    def __init__(self, parent=None, title: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """設置UI"""
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # 建立按鈕列
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)
        
    def setup_connections(self):
        """設置信號連接"""
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
    def get_data(self) -> Dict:
        """獲取對話框數據"""
        return {}
        
    def set_data(self, data: Dict):
        """設置對話框數據"""
        pass

class SettingsDialog(BaseDialog):
    """設定對話框"""
    
    settings_changed = pyqtSignal(dict)  # 設定變更信號
    
    def __init__(self, parent=None):
        super().__init__(parent, "系統設定")
        self.resize(500, 400)
        self.config_file = Path("config/settings.json")
        self.load_settings()
        
    def setup_ui(self):
        """設置UI"""
        super().setup_ui()
        
        # 建立分頁
        self.tab_widget = QTabWidget()
        self.main_layout.insertWidget(0, self.tab_widget)
        
        # 一般設定頁面
        self.create_general_tab()
        
        # ATP 設定頁面
        self.create_atp_tab()
        
        # 分析設定頁面
        self.create_analysis_tab()
        
        # 視覺化設定頁面
        self.create_visualization_tab()
        
    def create_general_tab(self):
        """建立一般設定頁面"""
        tab = QWidget()
        layout = QFormLayout()
        
        # 檔案路徑設定
        self.log_path = QLineEdit()
        browse_log = QPushButton("瀏覽...")
        browse_log.clicked.connect(lambda: self._browse_path(self.log_path))
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.log_path)
        path_layout.addWidget(browse_log)
        
        layout.addRow("日誌檔案路徑:", path_layout)
        
        # 介面設定
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["明亮", "暗色", "系統"])
        layout.addRow("介面主題:", self.theme_combo)
        
        # 語言設定
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["繁體中文", "English"])
        layout.addRow("系統語言:", self.lang_combo)
        
        # 自動更新設定
        self.auto_update = QCheckBox("啟用自動更新")
        layout.addRow("更新設定:", self.auto_update)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "一般設定")
        
    def create_atp_tab(self):
        """建立 ATP 設定頁面"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 速度設定群組
        speed_group = QGroupBox("速度設定")
        speed_layout = QFormLayout()
        
        self.speed_limit = QSpinBox()
        self.speed_limit.setRange(0, 200)
        self.speed_limit.setValue(90)
        speed_layout.addRow("速度限制 (km/h):", self.speed_limit)
        
        self.warning_speed = QSpinBox()
        self.warning_speed.setRange(0, 200)
        self.warning_speed.setValue(80)
        speed_layout.addRow("警告速度 (km/h):", self.warning_speed)
        
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)
        
        # 系統設定群組
        system_group = QGroupBox("系統設定")
        system_layout = QFormLayout()
        
        self.check_interval = QSpinBox()
        self.check_interval.setRange(1, 60)
        self.check_interval.setValue(5)
        system_layout.addRow("檢查間隔 (秒):", self.check_interval)
        
        self.auto_reconnect = QCheckBox("自動重新連線")
        system_layout.addRow("連線設定:", self.auto_reconnect)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "ATP 設定")
        
    def create_analysis_tab(self):
        """建立分析設定頁面"""
        tab = QWidget()
        layout = QFormLayout()
        
        # 分析參數設定
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(100, 10000)
        self.chunk_size.setValue(1000)
        layout.addRow("分批大小:", self.chunk_size)
        
        self.smooth_window = QSpinBox()
        self.smooth_window.setRange(1, 20)
        self.smooth_window.setValue(5)
        layout.addRow("平滑視窗大小:", self.smooth_window)
        
        self.outlier_threshold = QDoubleSpinBox()
        self.outlier_threshold.setRange(1.0, 5.0)
        self.outlier_threshold.setValue(3.0)
        layout.addRow("異常值閾值:", self.outlier_threshold)
        
        # 分析功能設定
        self.enable_cache = QCheckBox("啟用快取")
        layout.addRow("快取設定:", self.enable_cache)
        
        self.parallel_processing = QCheckBox("啟用平行處理")
        layout.addRow("平行處理:", self.parallel_processing)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "分析設定")
        
    def create_visualization_tab(self):
        """建立視覺化設定頁面"""
        tab = QWidget()
        layout = QFormLayout()
        
        # 圖表設定
        self.show_grid = QCheckBox("顯示網格")
        layout.addRow("網格設定:", self.show_grid)
        
        self.line_width = QSpinBox()
        self.line_width.setRange(1, 5)
        self.line_width.setValue(2)
        layout.addRow("線條寬度:", self.line_width)
        
        self.marker_size = QSpinBox()
        self.marker_size.setRange(4, 20)
        self.marker_size.setValue(8)
        layout.addRow("標記大小:", self.marker_size)
        
        # 動畫設定
        self.enable_animation = QCheckBox("啟用動畫")
        layout.addRow("動畫設定:", self.enable_animation)
        
        self.animation_duration = QSpinBox()
        self.animation_duration.setRange(100, 1000)
        self.animation_duration.setValue(200)
        layout.addRow("動畫時間 (毫秒):", self.animation_duration)
        
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "視覺化設定")
        
    def _browse_path(self, line_edit: QLineEdit):
        """瀏覽路徑"""
        path = QFileDialog.getExistingDirectory(
            self,
            "選擇目錄",
            str(Path(line_edit.text()).parent)
        )
        if path:
            line_edit.setText(path)
            
    def load_settings(self):
        """載入設定"""
        try:
            if self.config_file.exists():
                settings = json.loads(self.config_file.read_text(encoding='utf-8'))
                self.set_data(settings)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"載入設定失敗: {str(e)}")
            
    def save_settings(self):
        """儲存設定"""
        try:
            settings = self.get_data()
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            self.config_file.write_text(
                json.dumps(settings, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            self.settings_changed.emit(settings)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"儲存設定失敗: {str(e)}")
            
    def accept(self):
        """確認按鈕處理"""
        self.save_settings()
        super().accept()
        
    def get_data(self) -> Dict:
        """獲取設定數據"""
        return {
            'general': {
                'log_path': self.log_path.text(),
                'theme': self.theme_combo.currentText(),
                'language': self.lang_combo.currentText(),
                'auto_update': self.auto_update.isChecked()
            },
            'atp': {
                'speed_limit': self.speed_limit.value(),
                'warning_speed': self.warning_speed.value(),
                'check_interval': self.check_interval.value(),
                'auto_reconnect': self.auto_reconnect.isChecked()
            },
            'analysis': {
                'chunk_size': self.chunk_size.value(),
                'smooth_window': self.smooth_window.value(),
                'outlier_threshold': self.outlier_threshold.value(),
                'enable_cache': self.enable_cache.isChecked(),
                'parallel_processing': self.parallel_processing.isChecked()
            },
            'visualization': {
                'show_grid': self.show_grid.isChecked(),
                'line_width': self.line_width.value(),
                'marker_size': self.marker_size.value(),
                'enable_animation': self.enable_animation.isChecked(),
                'animation_duration': self.animation_duration.value()
            }
        }
        
    def set_data(self, data: Dict):
        """設置設定數據"""
        if not data:
            return
            
        # 一般設定
        general = data.get('general', {})
        self.log_path.setText(general.get('log_path', ''))
        self.theme_combo.setCurrentText(general.get('theme', '明亮'))
        self.lang_combo.setCurrentText(general.get('language', '繁體中文'))
        self.auto_update.setChecked(general.get('auto_update', True))
        
        # ATP 設定
        atp = data.get('atp', {})
        self.speed_limit.setValue(atp.get('speed_limit', 90))
        self.warning_speed.setValue(atp.get('warning_speed', 80))
        self.check_interval.setValue(atp.get('check_interval', 5))
        self.auto_reconnect.setChecked(atp.get('auto_reconnect', True))
        
        # 分析設定
        analysis = data.get('analysis', {})
        self.chunk_size.setValue(analysis.get('chunk_size', 1000))
        self.smooth_window.setValue(analysis.get('smooth_window', 5))
        self.outlier_threshold.setValue(analysis.get('outlier_threshold', 3.0))
        self.enable_cache.setChecked(analysis.get('enable_cache', True))
        self.parallel_processing.setChecked(analysis.get('parallel_processing', True))
        
        # 視覺化設定
        visualization = data.get('visualization', {})
        self.show_grid.setChecked(visualization.get('show_grid', True))
        self.line_width.setValue(visualization.get('line_width', 2))
        self.marker_size.setValue(visualization.get('marker_size', 8))
        self.enable_animation.setChecked(visualization.get('enable_animation', True))
        self.animation_duration.setValue(visualization.get('animation_duration', 200))
class SpeedAnalysisDialog(BaseDialog):
    """速度分析對話框"""
    
    analysis_requested = pyqtSignal(dict)  # 分析請求信號
    
    def __init__(self, parent=None):
        super().__init__(parent, "速度分析")
        self.resize(800, 600)
        self.setup_plot()
        
    def setup_ui(self):
        """設置UI"""
        super().setup_ui()
        
        # 主要佈局
        content = QHBoxLayout()
        self.main_layout.insertLayout(0, content)
        
        # 左側控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        
        # 分析參數群組
        param_group = QGroupBox("分析參數")
        param_layout = QFormLayout()
        
        # 速度閾值
        self.speed_threshold = QDoubleSpinBox()
        self.speed_threshold.setRange(0, 200)
        self.speed_threshold.setValue(90)
        param_layout.addRow("速度閾值 (km/h):", self.speed_threshold)
        
        # 時間範圍
        self.time_range = QComboBox()
        self.time_range.addItems(["全部", "最近一小時", "最近30分鐘"])
        param_layout.addRow("時間範圍:", self.time_range)
        
        # 分析選項
        self.enable_smoothing = QCheckBox("啟用平滑化")
        self.enable_smoothing.setChecked(True)
        param_layout.addRow("數據處理:", self.enable_smoothing)
        
        self.remove_outliers = QCheckBox("移除異常值")
        param_layout.addRow("", self.remove_outliers)
        
        param_group.setLayout(param_layout)
        control_layout.addWidget(param_group)
        
        # 統計結果群組
        stats_group = QGroupBox("統計結果")
        stats_layout = QFormLayout()
        
        self.stats_labels = {
            'max_speed': QLabel("---"),
            'avg_speed': QLabel("---"),
            'std_speed': QLabel("---"),
            'over_speed_count': QLabel("---"),
            'over_speed_ratio': QLabel("---")
        }
        
        stats_layout.addRow("最高速度:", self.stats_labels['max_speed'])
        stats_layout.addRow("平均速度:", self.stats_labels['avg_speed'])
        stats_layout.addRow("標準差:", self.stats_labels['std_speed'])
        stats_layout.addRow("超速次數:", self.stats_labels['over_speed_count'])
        stats_layout.addRow("超速比例:", self.stats_labels['over_speed_ratio'])
        
        stats_group.setLayout(stats_layout)
        control_layout.addWidget(stats_group)
        
        # 分析按鈕
        analyze_btn = QPushButton("開始分析")
        analyze_btn.clicked.connect(self.start_analysis)
        control_layout.addWidget(analyze_btn)
        
        # 匯出按鈕
        export_btn = QPushButton("匯出結果")
        export_btn.clicked.connect(self.export_results)
        control_layout.addWidget(export_btn)
        
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        content.addWidget(control_panel)
        
        # 右側圖表區域
        plot_panel = QWidget()
        plot_layout = QVBoxLayout()
        
        # 速度曲線圖
        speed_group = QGroupBox("速度曲線")
        speed_layout = QVBoxLayout()
        speed_layout.addWidget(self.speed_plot)
        speed_group.setLayout(speed_layout)
        plot_layout.addWidget(speed_group)
        
        # 速度分布圖
        dist_group = QGroupBox("速度分布")
        dist_layout = QVBoxLayout()
        self.dist_plot = pg.PlotWidget()
        dist_layout.addWidget(self.dist_plot)
        dist_group.setLayout(dist_layout)
        plot_layout.addWidget(dist_group)
        
        plot_panel.setLayout(plot_layout)
        content.addWidget(plot_panel)
        
        # 設置比例
        content.setStretch(0, 1)  # 控制面板
        content.setStretch(1, 3)  # 圖表區域
        
    def setup_plot(self):
        """設置圖表"""
        # 速度曲線圖
        self.speed_plot = pg.PlotWidget()
        self.speed_plot.setBackground('w')
        self.speed_plot.showGrid(x=True, y=True)
        self.speed_plot.setLabel('left', '速度', units='km/h')
        self.speed_plot.setLabel('bottom', '時間')
        
        # 添加圖例
        self.speed_plot.addLegend()
        
        # 添加速度曲線
        self.speed_curve = self.speed_plot.plot(
            name='實際速度',
            pen=pg.mkPen('b', width=2)
        )
        
        # 添加速限線
        self.limit_line = self.speed_plot.plot(
            name='速度限制',
            pen=pg.mkPen('r', width=2, style=Qt.PenStyle.DashLine)
        )
        
    def start_analysis(self):
        """開始分析"""
        # 獲取分析參數
        params = {
            'speed_threshold': self.speed_threshold.value(),
            'time_range': self.time_range.currentText(),
            'enable_smoothing': self.enable_smoothing.isChecked(),
            'remove_outliers': self.remove_outliers.isChecked()
        }
        
        # 發送分析請求信號
        self.analysis_requested.emit(params)
        
    def update_results(self, results: Dict):
        """更新分析結果"""
        # 更新統計標籤
        stats = results.get('statistics', {})
        
        if 'max_speed' in stats:
            self.stats_labels['max_speed'].setText(f"{stats['max_speed']:.1f} km/h")
        if 'avg_speed' in stats:
            self.stats_labels['avg_speed'].setText(f"{stats['avg_speed']:.1f} km/h")
        if 'std_speed' in stats:
            self.stats_labels['std_speed'].setText(f"{stats['std_speed']:.2f}")
        if 'over_speed_count' in stats:
            self.stats_labels['over_speed_count'].setText(str(stats['over_speed_count']))
        if 'over_speed_ratio' in stats:
            self.stats_labels['over_speed_ratio'].setText(f"{stats['over_speed_ratio']:.1f}%")
            
        # 更新速度曲線
        if 'speed_data' in results:
            data = results['speed_data']
            self.speed_curve.setData(data['x'], data['y'])
            
        # 更新速限線
        threshold = self.speed_threshold.value()
        if len(data['x']) > 0:
            self.limit_line.setData(
                [data['x'][0], data['x'][-1]],
                [threshold, threshold]
            )
            
        # 更新速度分布圖
        if 'speed_distribution' in results:
            dist = results['speed_distribution']
            self.dist_plot.clear()
            self.dist_plot.plot(
                x=list(range(len(dist))),
                y=list(dist.values()),
                stepMode=True,
                fillLevel=0,
                brush=(0,0,255,50)
            )
            
    def export_results(self):
        """匯出分析結果"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "匯出結果",
            "",
            "Excel檔案 (*.xlsx);;CSV檔案 (*.csv);;所有檔案 (*)"
        )
        
        if filename:
            try:
                # 獲取當前分析結果
                results = self.get_data()
                
                # 根據檔案類型匯出
                if filename.endswith('.xlsx'):
                    self._export_excel(filename, results)
                else:
                    self._export_csv(filename, results)
                    
                QMessageBox.information(self, "成功", "分析結果匯出完成")
                
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"匯出失敗: {str(e)}")
                
    def _export_excel(self, filename: str, results: Dict):
        """匯出Excel"""
        import pandas as pd
        
        # 建立Excel writer
        with pd.ExcelWriter(filename) as writer:
            # 統計資料
            stats_df = pd.DataFrame([{
                '項目': k,
                '數值': v
            } for k, v in results['statistics'].items()])
            stats_df.to_excel(writer, sheet_name='統計資料', index=False)
            
            # 速度數據
            speed_df = pd.DataFrame({
                '時間': results['speed_data']['x'],
                '速度': results['speed_data']['y']
            })
            speed_df.to_excel(writer, sheet_name='速度數據', index=False)
            
            # 速度分布
            dist_df = pd.DataFrame([{
                '速度區間': k,
                '次數': v
            } for k, v in results['speed_distribution'].items()])
            dist_df.to_excel(writer, sheet_name='速度分布', index=False)
            
    def _export_csv(self, filename: str, results: Dict):
        """匯出CSV"""
        import pandas as pd
        
        # 合併所有數據
        data = {
            '統計資料': pd.DataFrame([results['statistics']]),
            '速度數據': pd.DataFrame({
                '時間': results['speed_data']['x'],
                '速度': results['speed_data']['y']
            }),
            '速度分布': pd.DataFrame([results['speed_distribution']])
        }
        
        # 寫入CSV
        with open(filename, 'w', encoding='utf-8') as f:
            for name, df in data.items():
                f.write(f"# {name}\n")
                df.to_csv(f, index=False)
                f.write("\n")
class EventAnalysisDialog(BaseDialog):
    """事件分析對話框"""
    
    analysis_requested = pyqtSignal(dict)  # 分析請求信號
    
    def __init__(self, parent=None):
        super().__init__(parent, "事件分析")
        self.resize(800, 600)
        self.setup_plot()
        
    def setup_ui(self):
        """設置UI"""
        super().setup_ui()
        
        # 主要佈局
        content = QHBoxLayout()
        self.main_layout.insertLayout(0, content)
        
        # 左側控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        
        # 過濾條件群組
        filter_group = QGroupBox("過濾條件")
        filter_layout = QFormLayout()
        
        # 事件類型
        self.event_type = QComboBox()
        self.event_type.addItems([
            "全部",
            "ATP狀態",
            "MMI狀態",
            "PRS事件",
            "緊急煞車",
            "超速警告"
        ])
        filter_layout.addRow("事件類型:", self.event_type)
        
        # 嚴重程度
        self.severity = QComboBox()
        self.severity.addItems([
            "全部",
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
            "INFO"
        ])
        filter_layout.addRow("嚴重程度:", self.severity)
        
        # 時間範圍
        self.time_range = QComboBox()
        self.time_range.addItems([
            "全部",
            "最近一小時",
            "最近30分鐘",
            "自定義"
        ])
        filter_layout.addRow("時間範圍:", self.time_range)
        
        filter_group.setLayout(filter_layout)
        control_layout.addWidget(filter_group)
        
        # 統計結果群組
        stats_group = QGroupBox("事件統計")
        stats_layout = QFormLayout()
        
        self.stats_labels = {
            'total_events': QLabel("---"),
            'critical_events': QLabel("---"),
            'high_events': QLabel("---"),
            'emergency_brake': QLabel("---"),
            'over_speed': QLabel("---")
        }
        
        stats_layout.addRow("總事件數:", self.stats_labels['total_events'])
        stats_layout.addRow("危急事件:", self.stats_labels['critical_events'])
        stats_layout.addRow("高度警示:", self.stats_labels['high_events'])
        stats_layout.addRow("緊急煞車:", self.stats_labels['emergency_brake'])
        stats_layout.addRow("超速警告:", self.stats_labels['over_speed'])
        
        stats_group.setLayout(stats_layout)
        control_layout.addWidget(stats_group)
        
        # 分析按鈕
        analyze_btn = QPushButton("開始分析")
        analyze_btn.clicked.connect(self.start_analysis)
        control_layout.addWidget(analyze_btn)
        
        # 匯出按鈕
        export_btn = QPushButton("匯出結果")
        export_btn.clicked.connect(self.export_results)
        control_layout.addWidget(export_btn)
        
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        content.addWidget(control_panel)
        
        # 右側圖表與列表區域
        display_panel = QWidget()
        display_layout = QVBoxLayout()
        
        # 事件分布圖
        plot_group = QGroupBox("事件分布")
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.event_plot)
        plot_group.setLayout(plot_layout)
        display_layout.addWidget(plot_group)
        
        # 事件列表
        list_group = QGroupBox("事件列表")
        list_layout = QVBoxLayout()
        
        # 建立表格
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        self.event_table = QTableWidget()
        self.event_table.setColumnCount(5)
        self.event_table.setHorizontalHeaderLabels([
            "時間", "類型", "嚴重程度", "位置", "描述"
        ])
        
        # 設置表格樣式
        header = self.event_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        list_layout.addWidget(self.event_table)
        list_group.setLayout(list_layout)
        display_layout.addWidget(list_group)
        
        display_panel.setLayout(display_layout)
        content.addWidget(display_panel)
        
        # 設置比例
        content.setStretch(0, 1)  # 控制面板
        content.setStretch(1, 2)  # 顯示區域
        
    def setup_plot(self):
        """設置圖表"""
        self.event_plot = pg.PlotWidget()
        self.event_plot.setBackground('w')
        self.event_plot.showGrid(x=True, y=True)
        self.event_plot.setLabel('left', '事件類型')
        self.event_plot.setLabel('bottom', '時間')
        
        # 添加圖例
        self.event_plot.addLegend()
        
    def start_analysis(self):
        """開始分析"""
        # 獲取分析參數
        params = {
            'event_type': self.event_type.currentText(),
            'severity': self.severity.currentText(),
            'time_range': self.time_range.currentText()
        }
        
        # 發送分析請求信號
        self.analysis_requested.emit(params)
        
    def update_results(self, results: Dict):
        """更新分析結果"""
        # 更新統計標籤
        stats = results.get('statistics', {})
        
        if 'total_events' in stats:
            self.stats_labels['total_events'].setText(str(stats['total_events']))
        if 'critical_events' in stats:
            self.stats_labels['critical_events'].setText(str(stats['critical_events']))
        if 'high_events' in stats:
            self.stats_labels['high_events'].setText(str(stats['high_events']))
        if 'emergency_brake' in stats:
            self.stats_labels['emergency_brake'].setText(str(stats['emergency_brake']))
        if 'over_speed' in stats:
            self.stats_labels['over_speed'].setText(str(stats['over_speed']))
            
        # 更新事件分布圖
        if 'event_data' in results:
            self.plot_events(results['event_data'])
            
        # 更新事件列表
        if 'events' in results:
            self.update_event_table(results['events'])
            
    def plot_events(self, event_data: Dict):
        """繪製事件分布圖"""
        self.event_plot.clear()
        
        # 設置Y軸刻度
        event_types = sorted(set(e['type'] for e in event_data['events']))
        y_ticks = [(i, t) for i, t in enumerate(event_types)]
        self.event_plot.getAxis('left').setTicks([y_ticks])
        
        # 依嚴重程度分類繪製
        severity_colors = {
            'CRITICAL': (255, 0, 0),    # 紅色
            'HIGH': (255, 165, 0),      # 橙色
            'MEDIUM': (255, 255, 0),    # 黃色
            'LOW': (0, 0, 255),         # 藍色
            'INFO': (0, 255, 0)         # 綠色
        }
        
        for severity in severity_colors:
            events = [e for e in event_data['events'] if e['severity'] == severity]
            if events:
                x = [e['timestamp'] for e in events]
                y = [event_types.index(e['type']) for e in events]
                
                self.event_plot.plot(
                    x=x,
                    y=y,
                    pen=None,
                    symbol='o',
                    symbolPen=None,
                    symbolBrush=severity_colors[severity],
                    symbolSize=8,
                    name=severity
                )
                
    def update_event_table(self, events: List[Dict]):
        """更新事件列表"""
        self.event_table.setRowCount(len(events))
        
        for row, event in enumerate(events):
            # 時間
            time_item = QTableWidgetItem(
                event['time'].strftime("%Y-%m-%d %H:%M:%S")
            )
            self.event_table.setItem(row, 0, time_item)
            
            # 類型
            type_item = QTableWidgetItem(event['type'])
            self.event_table.setItem(row, 1, type_item)
            
            # 嚴重程度
            severity_item = QTableWidgetItem(event['severity'])
            severity_item.setBackground(self._get_severity_color(event['severity']))
            self.event_table.setItem(row, 2, severity_item)
            
            # 位置
            location_item = QTableWidgetItem(
                f"{event.get('location', 0):.3f} km"
            )
            self.event_table.setItem(row, 3, location_item)
            
            # 描述
            desc_item = QTableWidgetItem(event.get('description', ''))
            self.event_table.setItem(row, 4, desc_item)
            
    def _get_severity_color(self, severity: str):
        """獲取嚴重程度對應的顏色"""
        from PyQt6.QtGui import QColor
        
        colors = {
            'CRITICAL': QColor(255, 200, 200),  # 淡紅色
            'HIGH': QColor(255, 230, 200),      # 淡橙色
            'MEDIUM': QColor(255, 255, 200),    # 淡黃色
            'LOW': QColor(200, 200, 255),       # 淡藍色
            'INFO': QColor(200, 255, 200)       # 淡綠色
        }
        return colors.get(severity, QColor(255, 255, 255))  # 預設白色
            
    def export_results(self):
        """匯出分析結果"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "匯出結果",
            "",
            "Excel檔案 (*.xlsx);;CSV檔案 (*.csv);;所有檔案 (*)"
        )
        
        if filename:
            try:
                # 獲取當前分析結果
                results = self.get_data()
                
                # 根據檔案類型匯出
                if filename.endswith('.xlsx'):
                    self._export_excel(filename, results)
                else:
                    self._export_csv(filename, results)
                    
                QMessageBox.information(self, "成功", "分析結果匯出完成")
                
            except Exception as e:
                QMessageBox.warning(self, "錯誤", f"匯出失敗: {str(e)}")
dialogs.py 
def create_brake_tab(self):
        """建立煞車設定分頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 煞車參數設定
        param_group = QGroupBox("煞車參數")
        param_layout = QFormLayout()
        
        # 最大煞車力
        self.max_brake_force = QDoubleSpinBox()
        self.max_brake_force.setRange(0, 100)
        self.max_brake_force.setValue(85)
        self.max_brake_force.setSuffix(" %")
        param_layout.addRow("最大煞車力:", self.max_brake_force)
        
        # 常用煞車力
        self.normal_brake_force = QDoubleSpinBox()
        self.normal_brake_force.setRange(0, 100)
        self.normal_brake_force.setValue(60)
        self.normal_brake_force.setSuffix(" %")
        param_layout.addRow("常用煞車力:", self.normal_brake_force)
        
        # 煞車反應時間
        self.brake_response = QDoubleSpinBox()
        self.brake_response.setRange(0, 5)
        self.brake_response.setValue(0.8)
        self.brake_response.setSuffix(" 秒")
        param_layout.addRow("反應時間:", self.brake_response)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)
        
        # 緊急煞車設定
        emergency_group = QGroupBox("緊急煞車")
        emergency_layout = QFormLayout()
        
        # 緊急煞車啟動條件
        self.emergency_conditions = QComboBox()
        self.emergency_conditions.addItems([
            "超速且無反應",
            "僅超速",
            "手動觸發"
        ])
        emergency_layout.addRow("啟動條件:", self.emergency_conditions)
        
        # 延遲時間
        self.emergency_delay = QDoubleSpinBox()
        self.emergency_delay.setRange(0, 5)
        self.emergency_delay.setValue(1.0)
        self.emergency_delay.setSuffix(" 秒")
        emergency_layout.addRow("延遲時間:", self.emergency_delay)
        
        # 解除條件
        self.release_conditions = QComboBox()
        self.release_conditions.addItems([
            "速度降至安全值",
            "司機確認後",
            "系統重置後"
        ])
        emergency_layout.addRow("解除條件:", self.release_conditions)
        
        emergency_group.setLayout(emergency_layout)
        layout.addWidget(emergency_group)
        
        # 測試功能
        test_group = QGroupBox("測試功能")
        test_layout = QFormLayout()
        
        # 自動測試
        self.auto_test = QCheckBox("啟用自動測試")
        test_layout.addRow("自動測試:", self.auto_test)
        
        # 測試週期
        self.test_interval = QSpinBox()
        self.test_interval.setRange(1, 30)
        self.test_interval.setValue(7)
        self.test_interval.setSuffix(" 天")
        test_layout.addRow("測試週期:", self.test_interval)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "煞車設定")
        
    def create_advanced_tab(self):
        """建立進階設定分頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # PRS通訊設定
        prs_group = QGroupBox("PRS通訊")
        prs_layout = QFormLayout()
        
        # 連接模式
        self.prs_mode = QComboBox()
        self.prs_mode.addItems([
            "雙工模式",
            "單工模式",
            "備援模式"
        ])
        prs_layout.addRow("連接模式:", self.prs_mode)
        
        # 連接埠
        self.prs_port = QLineEdit()
        self.prs_port.setPlaceholderText("COM1")
        prs_layout.addRow("連接埠:", self.prs_port)
        
        # 波特率
        self.baud_rate = QComboBox()
        self.baud_rate.addItems([
            "9600",
            "19200",
            "38400",
            "57600",
            "115200"
        ])
        prs_layout.addRow("波特率:", self.baud_rate)
        
        prs_group.setLayout(prs_layout)
        layout.addWidget(prs_group)
        
        # 資料處理設定
        data_group = QGroupBox("資料處理")
        data_layout = QFormLayout()
        
        # 資料壓縮
        self.data_compression = QCheckBox("啟用壓縮")
        data_layout.addRow("資料壓縮:", self.data_compression)
        
        # 資料備份
        self.data_backup = QCheckBox("自動備份")
        data_layout.addRow("資料備份:", self.data_backup)
        
        # 保留時間
        self.data_retention = QSpinBox()
        self.data_retention.setRange(1, 365)
        self.data_retention.setValue(90)
        self.data_retention.setSuffix(" 天")
        data_layout.addRow("保留時間:", self.data_retention)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        # 進階選項
        advanced_group = QGroupBox("進階選項")
        advanced_layout = QFormLayout()
        
        # 診斷模式
        self.diagnostic_mode = QCheckBox("啟用診斷模式")
        advanced_layout.addRow("診斷模式:", self.diagnostic_mode)
        
        # 效能模式
        self.performance_mode = QComboBox()
        self.performance_mode.addItems([
            "平衡模式",
            "效能優先",
            "節能模式"
        ])
        advanced_layout.addRow("效能模式:", self.performance_mode)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, "進階設定")
        
    def load_settings(self):
        """載入設定"""
        try:
            settings_file = Path("config/atp_settings.json")
            if settings_file.exists():
                settings = json.loads(settings_file.read_text(encoding='utf-8'))
                self.set_data(settings)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"載入設定失敗: {str(e)}")
            
    def save_settings(self):
        """儲存設定"""
        try:
            settings = self.get_data()
            settings_file = Path("config/atp_settings.json")
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            settings_file.write_text(
                json.dumps(settings, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            self.settings_changed.emit(settings)
            QMessageBox.information(self, "成功", "設定已儲存")
        except Exception as e:
            QMessageBox.warning(self, "警告", f"儲存設定失敗: {str(e)}")
            
    def get_data(self) -> Dict:
        """獲取設定數據"""
        return {
            'main': {
                'mode': self.mode_combo.currentText(),
                'mode_auth': self.mode_auth.currentText(),
                'atp_id': self.atp_id.text(),
                'mmi_id': self.mmi_id.text(),
                'check_interval': self.check_interval.value(),
                'auto_reconnect': self.auto_reconnect.isChecked(),
                'reconnect_limit': self.reconnect_limit.value(),
                'log_level': self.log_level.currentText(),
                'log_retention': self.log_retention.value(),
                'log_path': self.log_path.text()
            },
            'speed': {
                'max_speed': self.max_speed.value(),
                'normal_speed': self.normal_speed.value(),
                'shunting_speed': self.shunting_speed.value(),
                'warning_threshold': self.warning_threshold.value(),
                'monitor_interval': self.monitor_interval.value(),
                'sampling_rate': self.sampling_rate.value()
            },
            'brake': {
                'max_force': self.max_brake_force.value(),
                'normal_force': self.normal_brake_force.value(),
                'response_time': self.brake_response.value(),
                'emergency_condition': self.emergency_conditions.currentText(),
                'emergency_delay': self.emergency_delay.value(),
                'release_condition': self.release_conditions.currentText(),
                'auto_test': self.auto_test.isChecked(),
                'test_interval': self.test_interval.value()
            },
            'advanced': {
                'prs_mode': self.prs_mode.currentText(),
                'prs_port': self.prs_port.text(),
                'baud_rate': self.baud_rate.currentText(),
                'data_compression': self.data_compression.isChecked(),
                'data_backup': self.data_backup.isChecked(),
                'data_retention': self.data_retention.value(),
                'diagnostic_mode': self.diagnostic_mode.isChecked(),
                'performance_mode': self.performance_mode.currentText()
            }
        }
        
    def set_data(self, data: Dict):
        """設置設定數據"""
        if not data:
            return
            
        # 主要設定
        main = data.get('main', {})
        self.mode_combo.setCurrentText(main.get('mode', '全監控'))
        self.mode_auth.setCurrentText(main.get('mode_auth', '司機員'))
        self.atp_id.setText(main.get('atp_id', ''))
        self.mmi_id.setText(main.get('mmi_id', ''))
        self.check_interval.setValue(main.get('check_interval', 5))
        self.auto_reconnect.setChecked(main.get('auto_reconnect', True))
        self.reconnect_limit.setValue(main.get('reconnect_limit', 3))
        self.log_level.setCurrentText(main.get('log_level', 'INFO'))
        self.log_retention.setValue(main.get('log_retention', 30))
        self.log_path.setText(main.get('log_path', ''))
        
        # 速度設定
        speed = data.get('speed', {})
        self.max_speed.setValue(speed.get('max_speed', 130))
        self.normal_speed.setValue(speed.get('normal_speed', 90))
        self.shunting_speed.setValue(speed.get('shunting_speed', 25))
        self.warning_threshold.setValue(speed.get('warning_threshold', 90))
        self.monitor_interval.setValue(speed.get('monitor_interval', 0.5))
        self.sampling_rate.setValue(speed.get('sampling_rate', 10))
        
        # 煞車設定
        brake = data.get('brake', {})
        self.max_brake_force.setValue(brake.get('max_force', 85))
        self.normal_brake_force.setValue(brake.get('normal_force', 60))
        self.brake_response.setValue(brake.get('response_time', 0.8))
        self.emergency_conditions.setCurrentText(brake.get('emergency_condition', '超速且無反應'))
        self.emergency_delay.setValue(brake.get('emergency_delay', 1.0))
        self.release_conditions.setCurrentText(brake.get('release_condition', '速度降至安全值'))
        self.auto_test.setChecked(brake.get('auto_test', False))
        self.test_interval.setValue(brake.get('test_interval', 7))
        
        # 進階設定
        advanced = data.get('advanced', {})
        self.prs_mode.setCurrentText(advanced.get('prs_mode', '雙工模式'))
        self.prs_port.setText(advanced.get('prs_port', 'COM1'))
        self.baud_rate.setCurrentText(advanced.get('baud_rate', '115200'))
        self.data_compression.setChecked(advanced.get('data_compression', False))
        self.data_backup.setChecked(advanced.get('data_backup', True))
        self.data_retention.setValue(advanced.get('data_retention', 90))
        self.diagnostic_mode.setChecked(advanced.get('diagnostic_mode', False))
        self.performance_mode.setCurrentText(advanced.get('performance_mode', '平衡模式'))
        
    def _browse_path(self, line_edit: QLineEdit):
        """瀏覽路徑"""
        path = QFileDialog.getExistingDirectory(
            self,
            "選擇目錄",
            str(Path(line_edit.text()).parent)
        )
        if path:
            line_edit.setText(path)
            
    def accept(self):
        """確認按鈕處理"""
        self.save_settings()
        super().accept()
