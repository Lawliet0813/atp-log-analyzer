from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QWidget, QGroupBox, QLabel,
                           QPushButton, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from ...analyzer.mmi_analyzer import MMIAnalyzer
from ..widgets.mmi_indicator import MMIEventList

class MMIAnalysisDialog(QDialog):
    """MMI分析對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = MMIAnalyzer()
        self.setup_ui()
        
    def setup_ui(self):
        """設置UI"""
        self.setWindowTitle("MMI系統分析")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # 建立分頁
        self.tab_widget = QTabWidget()
        
        # 速度分析分頁
        self.tab_widget.addTab(self._create_speed_tab(), "速度分析")
        
        # 事件分析分頁
        self.tab_widget.addTab(self._create_event_tab(), "事件分析")
        
        # 系統穩定性分頁
        self.tab_widget.addTab(self._create_stability_tab(), "系統穩定性")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按鈕
        button_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("開始分析")
        self.analyze_btn.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.analyze_btn)
        
        self.export_btn = QPushButton("匯出結果")
        self.export_btn.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def _create_speed_tab(self) -> QWidget:
        """建立速度分析分頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 速度曲線圖
        plot_group = QGroupBox("速度曲線")
        plot_layout = QVBoxLayout()
        
        self.speed_plot = pg.PlotWidget()
        self.speed_plot.setBackground('w')
        self.speed_plot.showGrid(x=True, y=True)
        self.speed_plot.setLabel('left', '速度', units='km/h')
        self.speed_plot.setLabel('bottom', '時間')
        
        plot_layout.addWidget(self.speed_plot)
        plot_group.setLayout(plot_layout)
        layout.addWidget(plot_group)
        
        # 速度統計
        stats_group = QGroupBox("速度統計")
        stats_layout = QHBoxLayout()
        
        self.speed_stats = QTableWidget()
        self.speed_stats.setColumnCount(2)
        self.speed_stats.setHorizontalHeaderLabels(["項目", "數值"])
        stats_layout.addWidget(self.speed_stats)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        tab.setLayout(layout)
        return tab
        
    def _create_event_tab(self) -> QWidget:
        """建立事件分析分頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 事件列表
        self.event_list = MMIEventList()
        layout.addWidget(self.event_list)
        
        # 事件統計
        stats_group = QGroupBox("事件統計")
        stats_layout = Q
      # 事件統計
        stats_group = QGroupBox("事件統計")
        stats_layout = QHBoxLayout()
        
        self.event_stats = QTableWidget()
        self.event_stats.setColumnCount(2)
        self.event_stats.setHorizontalHeaderLabels(["事件類型", "次數"])
        stats_layout.addWidget(self.event_stats)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        tab.setLayout(layout)
        return tab
        
    def _create_stability_tab(self) -> QWidget:
        """建立系統穩定性分頁"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 系統狀態圖
        status_group = QGroupBox("系統狀態")
        status_layout = QVBoxLayout()
        
        self.status_plot = pg.PlotWidget()
        self.status_plot.setBackground('w')
        self.status_plot.showGrid(x=True, y=True)
        self.status_plot.setLabel('left', '狀態')
        self.status_plot.setLabel('bottom', '時間')
        
        status_layout.addWidget(self.status_plot)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 穩定性指標
        metrics_group = QGroupBox("穩定性指標")
        metrics_layout = QHBoxLayout()
        
        self.stability_metrics = QTableWidget()
        self.stability_metrics.setColumnCount(2)
        self.stability_metrics.setHorizontalHeaderLabels(["指標", "數值"])
        metrics_layout.addWidget(self.stability_metrics)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        tab.setLayout(layout)
        return tab
        
    def set_data(self, records: list):
        """設置分析資料"""
        self.records = records
        self.update_display()
        
    def update_display(self):
        """更新顯示"""
        try:
            # 更新速度曲線
            speed_records = [r for r in self.records 
                           if hasattr(r, 'speed')]
            
            if speed_records:
                times = [(r.timestamp - speed_records[0].timestamp).total_seconds()
                        for r in speed_records]
                speeds = [r.speed for r in speed_records]
                
                self.speed_plot.clear()
                self.speed_plot.plot(times, speeds, pen='b')
                
            # 更新事件列表
            event_records = [r for r in self.records 
                           if hasattr(r, 'event_type')]
            
            self.event_list.clear_events()
            for record in event_records:
                self.event_list.add_event({
                    'time': record.timestamp,
                    'type': self._get_event_name(record.event_type),
                    'description': self._get_event_description(record)
                })
                
            # 更新系統狀態圖
            self._update_status_plot()
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "錯誤", f"更新顯示失敗: {str(e)}")
            
    def start_analysis(self):
        """開始分析"""
        try:
            # 分析速度記錄
            speed_records = [r for r in self.records 
                           if hasattr(r, 'speed')]
            speed_stats = self.analyzer.analyze_speed(speed_records)
            
            # 更新速度統計表
            self.speed_stats.setRowCount(0)
            for item, value in speed_stats.items():
                if item != 'speed_distribution':
                    row = self.speed_stats.rowCount()
                    self.speed_stats.insertRow(row)
                    self.speed_stats.setItem(row, 0, QTableWidgetItem(item))
                    self.speed_stats.setItem(row, 1, 
                                           QTableWidgetItem(str(value)))
            
            # 分析事件記錄
            event_records = [r for r in self.records 
                           if hasattr(r, 'event_type')]
            event_stats = self.analyzer.analyze_events(event_records)
            
            # 更新事件統計表
            self.event_stats.setRowCount(0)
            for event_type, count in event_stats['event_counts'].items():
                row = self.event_stats.rowCount()
                self.event_stats.insertRow(row)
                self.event_stats.setItem(row, 0, 
                                       QTableWidgetItem(self._get_event_name(event_type)))
                self.event_stats.setItem(row, 1, 
                                       QTableWidgetItem(str(count)))
                
            # 分析系統穩定性
            stability_stats = self.analyzer.analyze_system_stability(event_records)
            
            # 更新穩定性指標
            self.stability_metrics.setRowCount(0)
            metrics = {
                '系統重啟次數': stability_stats['restart_count'],
                '錯誤事件次數': stability_stats['error_count'],
                '平均錯誤間隔': f"{stability_stats['avg_error_interval']:.1f}秒",
                '最短錯誤間隔': f"{stability_stats['min_error_interval']:.1f}秒"
            }
            
            for metric, value in metrics.items():
                row = self.stability_metrics.rowCount()
                self.stability_metrics.insertRow(row)
                self.stability_metrics.setItem(row, 0, QTableWidgetItem(metric))
                self.stability_metrics.setItem(row, 1, QTableWidgetItem(str(value)))
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "錯誤", f"分析失敗: {str(e)}")
            
    def export_results(self):
        """匯出分析結果"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "匯出分析結果",
                "",
                "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if not filename:
                return
                
            if filename.endswith('.xlsx'):
                self._export_excel(filename)
            else:
                self._export_csv(filename)
                
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "錯誤", f"匯出失敗: {str(e)}")
            
    def _export_excel(self, filename: str):
        """匯出Excel格式"""
        import pandas as pd
        
        # 建立Excel writer
        with pd.ExcelWriter(filename) as writer:
            # 速度統計
            speed_data = []
            for row in range(self.speed_stats.rowCount()):
                item = self.speed_stats.item(row, 0).text()
                value = self.speed_stats.item(row, 1).text()
                speed_data.append({'項目': item, '數值': value})
                
            pd.DataFrame(speed_data).to_excel(
                writer, 
                sheet_name='速度統計',
                index=False
            )
            
            # 事件統計
            event_data = []
            for row in range(self.event_stats.rowCount()):
                event_type = self.event_stats.item(row, 0).text()
                count = self.event_stats.item(row, 1).text()
                event_data.append({'事件類型': event_type, '次數': count})
                
            pd.DataFrame(event_data).to_excel(
                writer,
                sheet_name='事件統計',
                index=False
            )
            
            # 穩定性指標
            stability_data = []
            for row in range(self.stability_metrics.rowCount()):
                metric = self.stability_metrics.item(row, 0).text()
                value = self.stability_metrics.item(row, 1).text()
                stability_data.append({'指標': metric, '數值': value})
                
            pd.DataFrame(stability_data).to_excel(
                writer,
                sheet_name='穩定性指標',
                index=False
            )
            
    def _export_csv(self, filename: str):
        """匯出CSV格式"""
        import pandas as pd
        
        # 建立所有統計資料的DataFrame
        data = {
            '速度統計': pd.DataFrame([
                {'項目': self.speed_stats.item(row, 0).text(),
                 '數值': self.speed_stats.item(row, 1).text()}
                for row in range(self.speed_stats.rowCount())
            ]),
            '事件統計': pd.DataFrame([
                {'事件類型': self.event_stats.item(row, 0).text(),
                 '次數': self.event_stats.item(row, 1).text()}
                for row in range(self.event_stats.rowCount())
            ]),
            '穩定性指標': pd.DataFrame([
                {'指標': self.stability_metrics.item(row, 0).text(),
                 '數值': self.stability_metrics.item(row, 1).text()}
                for row in range(self.stability_metrics.rowCount())
            ])
        }
        
        # 寫入CSV文件
        with open(filename, 'w', encoding='utf-8') as f:
            for name, df in data.items():
                f.write(f"# {name}\n")
                df.to_csv(f, index=False)
                f.write("\n")
                
    def _update_status_plot(self):
        """更新系統狀態圖"""
        # 取得事件記錄
        event_records = [r for r in self.records 
                        if hasattr(r, 'event_type')]
        
        if not event_records:
            return
            
        # 繪製狀態變化
        self.status_plot.clear()
        
        # 定義狀態值
        status_values = {
            'STARTUP': 3,
            'NORMAL': 2,
            'WARNING': 1,
            'ERROR': 0
        }
        
        times = []
        states = []
        current_state = 'NORMAL'
        
        for record in event_records:
            # 判斷事件影響的狀態
            if record.event_type == MMIParser.EVENT_STARTUP:
                current_state = 'STARTUP'
            elif record.event_type == MMIParser.EVENT_ERROR:
                current_state = 'ERROR'
            elif record.event_type == MMIParser.EVENT_MODE_CHANGE:
                current_state = 'NORMAL'
                
            time = (record.timestamp - event_records[0].timestamp).total_seconds()
            times.append(time)
            states.append(status_values[current_state])
            
        # 繪製狀態曲線
        self.status_plot.plot(times, states, pen='b', symbol='o')
        
        # 設置Y軸刻度
        axis = self.status_plot.getAxis('left')
        axis.setTicks([[(v, k) for k, v in status_values.items()]])
        
    def _get_event_name(self, event_type: int) -> str:
        """取得事件類型名稱"""
        event_names = {
            MMIParser.EVENT_STARTUP: "系統啟動",
            MMIParser.EVENT_SHUTDOWN: "系統關機",
            MMIParser.EVENT_MODE_CHANGE: "模式切換",
            MMIParser.EVENT_ERROR: "系統錯誤",
            MMIParser.EVENT_USER_ACTION: "使用者操作"
        }
        return event_names.get(event_type, f"未知事件({event_type})")
        
    def _get_event_description(self, event_record) -> str:
        """取得事件描述"""
        # 依事件類型產生描述
        if event_record.event_type == MMIParser.EVENT_ERROR:
            return f"錯誤代碼: {event_record.event_data[0]}"
        elif event_record.event_type == MMIParser.EVENT_MODE_CHANGE:
            mode_names = {
                0: "初始化",
                1: "全監控",
                2: "目視行車",
                3: "調車模式"
            }
            mode = event_record.event_data[0]
            return f"切換至{mode_names.get(mode, f'未知模式({mode})')}"
        elif event_record.event_type == MMIParser.EVENT_USER_ACTION:
            action_names = {
                1: "按鈕操作",
                2: "觸控操作",
                3: "功能切換"
            }
            action = event_record.event_data[0]
            return f"{action_names.get(action, f'未知操作({action})')}"
            
        return ""
