# src/analyzer/resources/templates/excel_template.py

"""
此檔案用於生成 Excel 報表範本
執行此檔案將會在同目錄下生成 excel_template.xlsx
"""

import xlsxwriter
from pathlib import Path

def create_excel_template():
    """建立Excel報表範本"""
    template_path = Path(__file__).parent / 'excel_template.xlsx'
    
    # 建立活頁簿
    workbook = xlsxwriter.Workbook(str(template_path))
    
    # 設定格式
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#D0D8E8',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'font_size': 11,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'font_size': 11,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '#,##0.00'
    })
    
    # 1. 摘要工作表
    ws_summary = workbook.add_worksheet('摘要')
    ws_summary.set_column('A:A', 20)
    ws_summary.set_column('B:B', 30)
    
    # 標題
    ws_summary.merge_range('A1:B1', 'ATP行車記錄分析報告', title_format)
    
    # 基本統計欄位
    headers = ['分析項目', '數值']
    for col, header in enumerate(headers):
        ws_summary.write(1, col, header, header_format)
    
    # 2. 速度分析工作表
    ws_speed = workbook.add_worksheet('速度分析')
    ws_speed.set_column('A:E', 15)
    
    # 速度分布
    ws_speed.merge_range('A1:B1', '速度分布統計', title_format)
    ws_speed.write(1, 0, '速度區間', header_format)
    ws_speed.write(1, 1, '次數', header_format)
    
    # 加減速分析
    ws_speed.merge_range('D1:E1', '加減速分析', title_format)
    ws_speed.write(1, 3, '分析項目', header_format)
    ws_speed.write(1, 4, '數值', header_format)
    
    # 3. 事件分析工作表
    ws_event = workbook.add_worksheet('事件分析')
    ws_event.set_column('A:D', 20)
    
    # 事件統計
    ws_event.merge_range('A1:B1', '事件統計', title_format)
    ws_event.write(1, 0, '事件類型', header_format)
    ws_event.write(1, 1, '發生次數', header_format)
    
    # 重要事件列表
    ws_event.merge_range('A8:D8', '重要事件列表', title_format)
    event_headers = ['時間', '事件類型', '位置', '描述']
    for col, header in enumerate(event_headers):
        ws_event.write(9, col, header, header_format)
    
    # 4. 位置分析工作表
    ws_location = workbook.add_worksheet('位置分析')
    ws_location.set_column('A:B', 20)
    
    # 站間運行時間
    ws_location.merge_range('A1:B1', '站間運行時間', title_format)
    ws_location.write(1, 0, '區間', header_format)
    ws_location.write(1, 1, '時間', header_format)
    
    # 位置分布
    ws_location.merge_range('A8:B8', '位置分布統計', title_format)
    ws_location.write(9, 0, '位置區間', header_format)
    ws_location.write(9, 1, '次數', header_format)
    
    workbook.close()
    print(f"Excel範本已建立: {template_path}")

if __name__ == '__main__':
    create_excel_template()
