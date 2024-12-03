from sqlalchemy import text
import pandas as pd

class LocationProcessor:
    def __init__(self, engine):
        self.engine = engine
        
        # Borough 映射字典
        self.borough_id_mapping = {
            '1': 'Manhattan',
            '2': 'Bronx',
            '3': 'Brooklyn',
            '4': 'Queens',
            '5': 'Staten Island'
        }
        
        self.borough_name_mapping = {
            'MANHATTAN': 'Manhattan',
            'BRONX': 'Bronx',
            'BROOKLYN': 'Brooklyn',
            'QUEENS': 'Queens',
            'STATEN ISLAND': 'Staten Island'
        }

    def process_locations(self, inventory_df, sales_df):
        """处理位置数据"""
        try:
            # 打印可用的列名，帮助调试
            print("Available columns in inventory_df:", inventory_df.columns.tolist())
            
            # 初始化位置数据框
            locations_df = pd.DataFrame()
            
            # 根据实际的列名映射数据
            # 假设实际的列名可能是 'BOROUGH', 'NEIGHBORHOOD' 等
            column_mapping = {
                'BOROUGH': 'borough',
                'NEIGHBORHOOD': 'neighborhood',
                'POSTAL CODE': 'zip_code',  # 或其他可能的邮编列名
            }
            
            # 创建位置数据框
            for excel_col, db_col in column_mapping.items():
                if excel_col in inventory_df.columns:
                    locations_df[db_col] = inventory_df[excel_col]
                else:
                    # 如果列不存在，创建空列
                    locations_df[db_col] = ''
            
            # 清理数据
            locations_df = locations_df.fillna('')
            
            # 删除重复的位置
            locations_df = locations_df.drop_duplicates()
            
            # 添加位置ID
            locations_df.insert(0, 'location_id', range(1, len(locations_df) + 1))
            
            print("Processed locations data sample:")
            print(locations_df.head())
            
            return locations_df
            
        except Exception as e:
            print(f"Error processing locations data: {e}")
            raise
