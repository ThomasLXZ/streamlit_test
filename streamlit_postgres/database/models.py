from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Date, ForeignKey, text

metadata = MetaData()

# 位置表
locations = Table(
    'locations', metadata,
    Column('location_id', Integer, primary_key=True),
    Column('borough', String),
    Column('neighborhood', String),
    Column('zip_code', String)
)

# 建筑类别表
building_classes = Table(
    'building_classes', metadata,
    Column('class_id', Integer, primary_key=True),
    Column('building_class_category', String),
    Column('building_class_code', String),
    Column('tax_class', Integer)
)

# 代理表
agents = Table(
    'agents', metadata,
    Column('agent_id', Integer, primary_key=True),
    Column('full_name', String),
    Column('email', String),
    Column('experience', Integer),
    Column('photo_url', String),
    Column('recommendations_count', Integer),
    Column('profile_url', String),
    Column('social_media_urls', String),
    Column('address', String),
    Column('mobile', String)
)

# 房产表
properties = Table(
    'properties', metadata,
    Column('property_id', Integer, primary_key=True),
    Column('location_id', Integer, ForeignKey('locations.location_id')),
    Column('class_id', Integer, ForeignKey('building_classes.class_id')),
    Column('block', String),
    Column('lot', String),
    Column('address', String),
    Column('apartment_number', String),
    Column('residential_units', Integer),
    Column('commercial_units', Integer),
    Column('total_units', Integer),
    Column('land_square_feet', Float),
    Column('gross_square_feet', Float),
    Column('year_built', Integer)
)

# 销售表
sales = Table(
    'sales', metadata,
    Column('sale_id', Integer, primary_key=True),
    Column('property_id', Integer, ForeignKey('properties.property_id')),
    Column('agent_id', Integer, ForeignKey('agents.agent_id')),
    Column('sale_date', Date),
    Column('sale_price', Float)
)

def create_tables(engine):
    """创建所有数据表"""
    metadata.create_all(engine)

def drop_tables(engine):
    """删除所有数据表"""
    metadata.drop_all(engine)
