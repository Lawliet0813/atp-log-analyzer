import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    # 建立應用程式
    app = QApplication(sys.argv)
    
    # 設定應用程式樣式
    app.setStyle('Fusion')
    
    # 建立並顯示主視窗
    window = MainWindow()
    window.show()
    
    # 進入事件循環
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
