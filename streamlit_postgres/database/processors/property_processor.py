from sqlalchemy import text
import pandas as pd
from ..utils.address_utils import AddressStandardizer

class PropertyProcessor:
    def __init__(self, engine):
        self.engine = engine
        self.address_standardizer = AddressStandardizer()

    def process_properties(self, inventory_df, locations_df, building_classes_df):
        """处理并插入房产数据"""
        try:
            print("\nProcessing properties...")
            
            # 标准化地址
            inventory_df['std_address'] = inventory_df['address'].apply(self.address_standardizer.standardize_address)
            
            # 准备属性数据
            properties_data = []
            for _, row in inventory_df.iterrows():
                # 查找location_id
                location_mask = (
                    (locations_df['borough'] == row['borough']) &
                    (locations_df['neighborhood'] == row['neighborhood']) &
                    (locations_df['zip_code'] == str(row['zip_code']))
                )
                location_id = locations_df[location_mask]['location_id'].iloc[0] if any(location_mask) else None
                
                # 查找class_id
                class_mask = (
                    (building_classes_df['building_class_category'] == row['building_class_category']) &
                    (building_classes_df['building_class_code'] == row['building_class_at_present']) &
                    (building_classes_df['tax_class'] == row['tax_class_at_present'])
                )
                class_id = building_classes_df[class_mask]['class_id'].iloc[0] if any(class_mask) else None
                
                if location_id and class_id:
                    property_data = {
                        'location_id': location_id,
                        'class_id': class_id,
                        'block': str(row['block']),
                        'lot': str(row['lot']),
                        'address': row['std_address'],
                        'apartment_number': str(row['apartment_number']),
                        'residential_units': row['residential_units'],
                        'commercial_units': row['commercial_units'],
                        'total_units': row['total_units'],
                        'land_square_feet': row['land_square_feet'],
                        'gross_square_feet': row['gross_square_feet'],
                        'year_built': row['year_built']
                    }
                    properties_data.append(property_data)
            
            print(f"\nTotal properties to insert: {len(properties_data)}")
            print("\nSample of properties data:")
            print(pd.DataFrame(properties_data).head())
            
            # 插入数据
            with self.engine.connect() as connection:
                result = connection.execute(
                    text("""
                        INSERT INTO properties (
                            location_id, class_id, block, lot, address,
                            apartment_number, residential_units, commercial_units,
                            total_units, land_square_feet, gross_square_feet, year_built
                        )
                        VALUES (
                            :location_id, :class_id, :block, :lot, :address,
                            :apartment_number, :residential_units, :commercial_units,
                            :total_units, :land_square_feet, :gross_square_feet, :year_built
                        )
                        RETURNING *
                    """),
                    properties_data
                )
                
                # 获取插入的数据示例
                inserted_properties = pd.DataFrame(result.fetchall())
                print("\nSample of inserted properties:")
                print(inserted_properties.head())
                
                # 检查空值
                print("\nNull values in properties data:")
                print(pd.DataFrame(properties_data).isnull().sum())
                
                # 检查缺失的外键
                print("\nProperties without location_id:", 
                      len([p for p in properties_data if not p['location_id']]))
                print("Properties without class_id:", 
                      len([p for p in properties_data if not p['class_id']]))
                
                connection.commit()
                
            return inserted_properties
            
        except Exception as e:
            print(f"Error processing properties: {str(e)}")
            raise
