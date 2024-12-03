from sqlalchemy import text
import pandas as pd

class AgentProcessor:
    def __init__(self, engine):
        self.engine = engine

    def process_agents(self, agents_df):
        """处理代理数据"""
        try:
            # 确保必要的列存在
            required_columns = {
                'agent_id': 'int',
                'full_name': 'str',
                'email': 'str',
                'mobile': 'str',
                'address': 'str',
                'photo_url': 'str',
                'profile_url': 'str',
                'social_media_urls': 'str',
                'recommendations_count': 'int',
                'experience': 'int'
            }
            
            # 检查Excel文件中的列名
            print("Available columns in Excel:", agents_df.columns.tolist())
            
            # 初始化处理后的数据框
            processed_df = pd.DataFrame()
            
            # 处理每一列
            for col, dtype in required_columns.items():
                if col in agents_df.columns:
                    processed_df[col] = agents_df[col]
                else:
                    # 如果列不存在，创建默认值
                    if dtype == 'int':
                        processed_df[col] = 0
                    elif dtype == 'str':
                        processed_df[col] = ''
            
            # 转换数据类型
            processed_df['agent_id'] = pd.to_numeric(processed_df['agent_id'], errors='coerce').fillna(0).astype(int)
            processed_df['recommendations_count'] = pd.to_numeric(processed_df['recommendations_count'], errors='coerce').fillna(0).astype(int)
            processed_df['experience'] = pd.to_numeric(processed_df['experience'], errors='coerce').fillna(0).astype(int)
            
            # 确保字符串列不包含 NULL 值
            str_columns = ['full_name', 'email', 'mobile', 'address', 'photo_url', 'profile_url', 'social_media_urls']
            for col in str_columns:
                processed_df[col] = processed_df[col].fillna('')
            
            return processed_df
            
        except Exception as e:
            print(f"Error processing agents data: {e}")
            raise
