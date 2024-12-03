import re

class AddressStandardizer:
    def __init__(self):
        self.direction_mapping = {
            'NORTH': 'N',
            'SOUTH': 'S',
            'EAST': 'E',
            'WEST': 'W',
            'N.': 'N',
            'S.': 'S',
            'E.': 'E',
            'W.': 'W'
        }
        
        self.street_type_mapping = {
            'STREET': 'ST',
            'AVENUE': 'AVE',
            'BOULEVARD': 'BLVD',
            'PLACE': 'PL',
            'ROAD': 'RD',
            'LANE': 'LN',
            'DRIVE': 'DR',
            'COURT': 'CT',
            'CIRCLE': 'CIR',
            'TERRACE': 'TER',
            'HIGHWAY': 'HWY'
        }
    
    def standardize_address(self, address):
        """标准化地址格式"""
        if not isinstance(address, str):
            return address
            
        # 转换为大写
        address = address.upper()
        
        # 提取并标准化方向
        for full, abbr in self.direction_mapping.items():
            address = re.sub(r'\b' + full + r'\b', abbr, address)
        
        # 提取并标准化街道类型
        for full, abbr in self.street_type_mapping.items():
            address = re.sub(r'\b' + full + r'\b', abbr, address)
        
        # 处理公寓号
        address = re.sub(r'\bAPT\b|\bUNIT\b|\b#\b', 'APT', address)
        
        # 删除多余的空格
        address = ' '.join(address.split())
        
        return address
    
    def extract_building_number(self, address):
        """从地址中提取建筑号码"""
        match = re.match(r'^(\d+)', address)
        if match:
            return match.group(1)
        return None
