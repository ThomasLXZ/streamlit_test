import pandas as pd
import os

class DataLoader:
    def __init__(self, data_dir='dataset'):
        # 使用传入的data_dir构建文件路径
        self.inventory_path = f'{data_dir}/Inventory.xlsx'
        self.sales_path = f'{data_dir}/Sales.xlsx'
        self.agents_path = f'{data_dir}/Agent.xlsx'

    def load_excel_files(self):
        """加载Excel文件数据"""
        try:
            print("Loading Excel files...")
            inventory_df = pd.read_excel(self.inventory_path)
            sales_df = pd.read_excel(self.sales_path)
            agents_df = pd.read_excel(self.agents_path)
            
            return inventory_df, sales_df, agents_df
            
        except FileNotFoundError as e:
            print(f"Error loading Excel files: {e}")
            raise
