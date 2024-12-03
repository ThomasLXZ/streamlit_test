from sqlalchemy import text
import pandas as pd

class BuildingProcessor:
    def __init__(self, engine):
        self.engine = engine

    def process_building_classes(self, inventory_df, sales_df):
        """处理并插入建筑类别数据"""
        try:
            print("\nProcessing building classes...")
            
            # 合并并去重建筑类别数据
            building_classes = pd.concat([
                inventory_df[['building_class_category', 'building_class_at_present', 'tax_class_at_present']],
                sales_df[['building_class_category', 'building_class_at_present', 'tax_class_at_present']]
            ]).drop_duplicates()
            
            # 重命名列
            building_classes = building_classes.rename(columns={
                'building_class_at_present': 'building_class_code',
                'tax_class_at_present': 'tax_class'
            })
            
            print("\nSample of building classes data:")
            print(building_classes.head())
            
            # 检查空值
            print("\nNull values in building classes:")
            print(building_classes.isnull().sum())
            
            # 准备插入数据
            building_classes_data = building_classes.to_dict('records')
            print(f"\nTotal building classes to insert: {len(building_classes_data)}")
            
            # 插入数据
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("""
                        INSERT INTO building_classes (
                            building_class_category,
                            building_class_code,
                            tax_class
                        )
                        VALUES (
                            :building_class_category,
                            :building_class_code,
                            :tax_class
                        )
                        RETURNING *
                    """),
                    building_classes_data
                )
                
                # 获取插入的数据示例
                inserted_classes = pd.DataFrame(result.fetchall())
                print("\nSample of inserted building classes:")
                print(inserted_classes.head())
                
                connection.commit()
                print(f"Inserted {len(building_classes_data)} building classes")
                print("Building classes processed successfully")
                
            return inserted_classes
            
        except Exception as e:
            print(f"Error processing building classes: {str(e)}")
            raise
