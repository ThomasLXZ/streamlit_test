from sqlalchemy import text
import pandas as pd
from ..utils.address_utils import AddressStandardizer
from fuzzywuzzy import fuzz

class SalesProcessor:
    def __init__(self, engine):
        self.engine = engine
        self.address_standardizer = AddressStandardizer()

    def match_properties(self, sales_df, properties_df):
        """匹配销售记录与房产"""
        print("\nMatching properties...")
        
        # 标准化地址
        sales_df['std_address'] = sales_df['address'].apply(self.address_standardizer.standardize_address)
        
        # 创建匹配键
        sales_df['match_key'] = sales_df.apply(
            lambda x: f"{x['block']}|{x['lot']}|{x['std_address']}", axis=1
        )
        properties_df['match_key'] = properties_df.apply(
            lambda x: f"{x['block']}|{x['lot']}|{x['address']}", axis=1
        )
        
        # 第一步：精确匹配
        merged_df = sales_df.merge(
            properties_df[['property_id', 'match_key']],
            on='match_key',
            how='left'
        )
        
        # 打印匹配统计
        total_sales = len(sales_df)
        matched_sales = merged_df['property_id'].notna().sum()
        match_rate = (matched_sales / total_sales) * 100
        
        print("\nProperty matching statistics:")
        print(f"Total sales records: {total_sales}")
        print(f"Matched properties: {matched_sales} ({match_rate:.1f}%)")
        
        # 打印未匹配记录示例
        print("\nSample of unmatched records:")
        unmatched = merged_df[merged_df['property_id'].isna()][['block', 'lot', 'std_address', 'match_key']].head()
        print(unmatched)
        
        return merged_df

    def process_sales(self, sales_df, properties_df, agents_df):
        """处理并插入销售数据"""
        try:
            print("\nProcessing sales data...")
            
            # 匹配属性
            matched_sales = self.match_properties(sales_df, properties_df)
            
            # 准备销售数据
            sales_data = []
            for _, row in matched_sales.iterrows():
                # 尝试匹配代理
                agent_id = None
                if pd.notna(row['responsible_agent']):
                    agent_mask = agents_df['full_name'].str.lower() == row['responsible_agent'].lower()
                    if any(agent_mask):
                        agent_id = agents_df[agent_mask]['agent_id'].iloc[0]
                
                sale_data = {
                    'property_id': row['property_id'],
                    'agent_id': agent_id,
                    'sale_date': row['sale_date'],
                    'sale_price': row['sale_price']
                }
                sales_data.append(sale_data)
            
            print(f"\nTotal sales to insert: {len(sales_data)}")
            print("\nSample of sales data:")
            print(pd.DataFrame(sales_data).head())
            
            # 插入数据
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("""
                        INSERT INTO sales (property_id, agent_id, sale_date, sale_price)
                        VALUES (:property_id, :agent_id, :sale_date, :sale_price)
                        RETURNING *
                    """),
                    sales_data
                )
                
                # 获取插入的数据示例
                inserted_sales = pd.DataFrame(result.fetchall())
                print("\nSample of inserted sales:")
                print(inserted_sales.head())
                
                # 打印数据质量统计
                total_sales = len(sales_data)
                matched_properties = sum(1 for s in sales_data if s['property_id'] is not None)
                matched_agents = sum(1 for s in sales_data if s['agent_id'] is not None)
                
                print("\nSales data quality:")
                print(f"Total sales records: {total_sales}")
                print(f"Matched properties: {matched_properties} ({matched_properties/total_sales*100:.1f}%)")
                print(f"Matched agents: {matched_agents} ({matched_agents/total_sales*100:.1f}%)")
                print(f"Successfully inserted: {matched_properties}")
                
                connection.commit()
                
            return inserted_sales
            
        except Exception as e:
            print(f"Error processing sales: {str(e)}")
            raise
