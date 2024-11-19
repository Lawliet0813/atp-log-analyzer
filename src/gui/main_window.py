from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QFileDialog)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """設置主視窗UI"""
        self.setWindowTitle("ATP記錄分析系統")
        self.setGeometry(100, 100, 1200, 800)
        
        # 主要元件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 添加功能按鈕
        self.load_button = QPushButton("載入記錄檔")
        self.load_button.clicked.connect(self.on_load_file)
        layout.addWidget(self.load_button)
        
        # 添加速度曲線圖
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', '速度 (km/h)')
        self.plot_widget.setLabel('bottom', '時間')
        layout.addWidget(self.plot_widget)
        
    def on_load_file(self):
        """載入RU檔案"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "選擇ATP記錄檔",
            "",
            "RU Files (*.RU);;All Files (*)"
        )
        if filename:
            self.load_ru_file(filename)
            
    def load_ru_file(self, filename):
        """處理RU檔案載入"""
        pass  # 實作檔案載入邏輯
def create_visualization_tab(self):
    """創建視覺化頁面"""
    tab = QWidget()
    layout = QVBoxLayout()
    
    # 視圖選擇
    view_group = QGroupBox("視圖選擇")
    view_layout = QHBoxLayout()
    
    self.view_combo = QComboBox()
    self.view_combo.addItems([
        "速度曲線",
        "事件分布",
        "綜合儀表板"
    ])
    self.view_combo.currentTextChanged.connect(self.switch_visualization)
    
    view_layout.addWidget(QLabel("視圖類型:"))
    view_layout.addWidget(self.view_combo)
    view_group.setLayout(view_layout)
    layout.addWidget(view_group)
    
    # 視圖堆疊
    self.view_stack = QStackedWidget()
    
    # 添加各種視圖
    self.speed_view = self.create_speed_view()
    self.event_view = self.create_event_view()
    self.dashboard_view = self.create_dashboard_view()
    
    self.view_stack.addWidget(self.speed_view)
    self.view_stack.addWidget(self.event_view)
    self.view_stack.addWidget(self.dashboard_view)
    
    layout.addWidget(self.view_stack)
    tab.setLayout(layout)
    return tab

def create_speed_view(self):
    """創建速度視圖"""
    view = QWidget()
    layout = QVBoxLayout()
    
    # 速度曲線
    self.visualizer = ATPDataVisualizer()
    self.speed_plot = self.visualizer.create_speed_plot()
    layout.addWidget(self.speed_plot)
    
    # 控制選項
    control_group = QGroupBox("顯示選項")
    control_layout = QHBoxLayout()
    
    self.show_limit = QCheckBox("顯示速限")
    self.show_limit.toggled.connect(self.update_speed_view)
    
    self.show_events = QCheckBox("顯示事件標記")
    self.show_events.toggled.connect(self.update_speed_view)
    
    control_layout.addWidget(self.show_limit)
    control_layout.addWidget(self.show_events)
    control_group.setLayout(control_layout)
    
    layout.addWidget(control_group)
    view.setLayout(layout)
    return view

使用方式：

pythonCopy# 範例使用程式碼

# 建立視覺化工具
visualizer = ATPDataVisualizer()

# 創建儀表板
dashboard = visualizer.create_dashboard()

# 更新數據
data = {
    'speeds': speed_list,
    'times': time_list,
    'limits': limit_
