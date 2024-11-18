import unittest
from datetime import datetime
from src.ru_parser.ru_file import RUParser, RUHeader, RURecord

class TestRUParser(unittest.TestCase):
    def setUp(self):
        self.parser = RUParser()
    
    def test_parse_header(self):
        # 測試標頭解析
        test_data = (
            b'WSH001--' +  # 工作班別
            b'TR1234--' +  # 列車號
            b'DRV001--' +  # 司機員ID
            b'V1234-' +    # 車輛ID
            b'123456'      # 時間
        )
        
        with open('test.ru', 'wb') as f:
            f.write(test_data)
            
        with open('test.ru', 'rb') as f:
            header = self.parser._parse_header(f)
            
        self.assertEqual(header.work_shift, 'WSH001')
        self.assertEqual(header.train_no, 'TR1234')
        self.assertEqual(header.driver_id, 'DRV001')
        self.assertEqual(header.vehicle_id, 'V1234')
