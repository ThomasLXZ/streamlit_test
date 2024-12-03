from .connection import DatabaseConnection
from .data_loader import DataLoader
from .models import create_tables, drop_tables
from .processors.agent_processor import AgentProcessor
from .processors.location_processor import LocationProcessor
from .processors.building_processor import BuildingProcessor
from .processors.property_processor import PropertyProcessor
from .processors.sales_processor import SalesProcessor

class DataMigration:
    def __init__(self, data_dir='dataset'):
        self.db_connection = DatabaseConnection()
        self.engine = self.db_connection.get_engine()
        self.data_loader = DataLoader(data_dir)
        
        # 初始化所有处理器
        self.agent_processor = AgentProcessor(self.engine)
        self.location_processor = LocationProcessor(self.engine)
        self.building_processor = BuildingProcessor(self.engine)
        self.property_processor = PropertyProcessor(self.engine)
        self.sales_processor = SalesProcessor(self.engine)

    def create_tables(self):
        """创建数据库表"""
        print("Creating tables...")
        create_tables(self.engine)

    def drop_tables(self):
        """删除数据库表"""
        print("Dropping tables...")
        drop_tables(self.engine)

    def migrate_data(self):
        """执行数据迁移"""
        try:
            print("Migrating data...")
            
            # 加载数据
            print("Loading data...")
            inventory_df, sales_df, agents_df = self.data_loader.load_excel_files()
            
            # 处理数据
            agents_data = self.agent_processor.process_agents(agents_df)
            locations_data = self.location_processor.process_locations(inventory_df, sales_df)
            building_classes_data = self.building_processor.process_building_classes(inventory_df, sales_df)
            properties_data = self.property_processor.process_properties(
                inventory_df, locations_data, building_classes_data
            )
            sales_data = self.sales_processor.process_sales(
                sales_df, properties_data, agents_data
            )
            
            print("Data migration completed successfully!")
            
        except Exception as e:
            print(f"Error during data migration: {str(e)}")
            raise

    def verify_data(self):
        """验证数据迁移结果"""
        try:
            print("Verifying data...")
            
            with self.engine.connect() as connection:
                # 检查各表的记录数
                tables = ['locations', 'building_classes', 'agents', 'properties', 'sales']
                for table in tables:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"Table {table}: {count} records")
                
                # 检查空值
                print("\nChecking for NULL values:")
                # 检查properties表中的空值
                result = connection.execute(text("SELECT COUNT(*) FROM properties WHERE class_id IS NULL"))
                print(f"Properties with NULL class_id: {result.scalar()}")
                
                # 检查sales表中的空值
                result = connection.execute(text("""
                    SELECT COUNT(*) 
                    FROM sales 
                    WHERE property_id IS NULL OR agent_id IS NULL
                """))
                null_refs = result.scalar()
                print(f"Sales with NULL property_id or agent_id: {null_refs}")
                
                # 检查具体的NULL情况
                result = connection.execute(text("""
                    SELECT 
                        COUNT(*) as total_sales,
                        SUM(CASE WHEN property_id IS NULL THEN 1 ELSE 0 END) as null_property,
                        SUM(CASE WHEN agent_id IS NULL THEN 1 ELSE 0 END) as null_agent,
                        SUM(CASE WHEN property_id IS NULL AND agent_id IS NULL THEN 1 ELSE 0 END) as both_null
                    FROM sales
                """))
                stats = result.fetchone()
                print("\nDetailed NULL analysis in sales:")
                print(f"Total sales: {stats[0]}")
                print(f"Records with NULL property_id: {stats[1]} ({stats[1]/stats[0]*100:.1f}%)")
                print(f"Records with NULL agent_id: {stats[2]} ({stats[2]/stats[0]*100:.1f}%)")
                print(f"Records with both NULL: {stats[3]} ({stats[3]/stats[0]*100:.1f}%)")
                
        except Exception as e:
            print(f"Error verifying data: {str(e)}")
            raise
