import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

class DatabaseConnection:
    def __init__(self):
        load_dotenv()
        
        # 从环境变量获取数据库连接信息
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        # 构建数据库URL
        self.db_url = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
        self.engine = None
    
    def get_engine(self):
        """获取数据库引擎实例"""
        if not self.engine:
            self.engine = create_engine(self.db_url)
        return self.engine
    
    def get_connection(self):
        """获取数据库连接"""
        return self.get_engine().connect()

if __name__ == "__main__":
    db = DatabaseConnection()
    try:
        with db.get_connection() as conn:
            conn.execute(text("SELECT 1"))
            print("数据库连接成功！")
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
