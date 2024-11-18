# ATP Log Analyzer

ATP(Automatic Train Protection)行車紀錄分析系統，用於解析與分析列車ATP運行記錄。

## 功能特點

- ATP RU檔案解析與驗證
- 速度曲線分析與視覺化
- ATP事件記錄分析
- 行車安全指標統計
- 分析報表匯出

## 系統需求

- Python 3.8+
- PyQt6
- numpy
- pandas
- pyqtgraph

## 安裝方式

```bash
pip install -r requirements.txt
使用說明

執行主程式：

bashCopypython src/main.py

載入RU檔案進行分析
查看分析結果與報表

注意事項

本系統僅供ATP記錄分析使用
不包含任何列車控制功能
分析結果僅供參考，實際運行以ATP系統為準
