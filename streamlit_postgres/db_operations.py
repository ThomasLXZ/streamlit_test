from database.data_migration import DataMigration

def main():
    """主函数：执行数据迁移流程"""
    try:
        # 创建数据迁移实例
        data_migration = DataMigration()
        
        # 执行数据迁移流程
        print("Creating tables...")
        data_migration.create_tables()
        
        print("Migrating data...")
        data_migration.migrate_data()
        
        print("Verifying data...")
        data_migration.verify_data()
        
        print("Data migration completed successfully!")
        
    except Exception as e:
        print(f"Error during data migration: {str(e)}")
        raise

if __name__ == "__main__":
    main()
