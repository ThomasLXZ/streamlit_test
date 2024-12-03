# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from stream_page.c_level_dashboard import create_c_level_dashboard
from stream_page.agent_dashboard import create_agent_dashboard

# 加载环境变量
load_dotenv()

# 创建数据库连接
def create_db_connection():
    db_params = {
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}/{db_params['database']}"
    return create_engine(connection_string)

def load_data():
    """从数据库加载所需的所有数据"""
    engine = create_db_connection()
    
    with st.sidebar:
        
        # 加载销售数据
        sales_df = pd.read_sql("SELECT * FROM sales", engine)
        sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
        
        # 加载代理人数据
        agents_df = pd.read_sql("SELECT * FROM agents", engine)
        if agents_df.empty:
            st.warning("No agents found in the database. Creating sample data...")
            # 从销售数据中获取唯一的代理人ID
            unique_agent_ids = sales_df['agent_id'].dropna().unique()
            agents_df = pd.DataFrame({
                'agent_id': unique_agent_ids,
                'full_name': [f'Agent {i}' for i in range(1, len(unique_agent_ids) + 1)],
                'experience': [5] * len(unique_agent_ids),
                'recommendations_count': [0] * len(unique_agent_ids),
                'email': [''] * len(unique_agent_ids),
                'photo_url': [''] * len(unique_agent_ids),
                'profile_url': [''] * len(unique_agent_ids),
                'social_media_urls': [''] * len(unique_agent_ids),
                'address': [''] * len(unique_agent_ids),
                'mobile': [''] * len(unique_agent_ids)
            })
        
        # 加载物业数据
        properties_df = pd.read_sql("SELECT * FROM properties", engine)
        
        # 加载位置数据
        locations_df = pd.read_sql("SELECT * FROM locations", engine)
                
        return sales_df, agents_df, properties_df, locations_df
            

def main():
    st.set_page_config(
        page_title="Real Estate Analytics Dashboard",
        page_icon="🏠",
        layout="wide"
    )
    
    # 从外部文件加载 CSS
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    # 加载数据
    sales_df, agents_df, properties_df, locations_df = load_data()
    
    # 使用 option_menu 创建导航栏
    with st.sidebar:
        selected_page = option_menu(
            menu_title="Navigation",
            options=["Executive", "Agent"],
            icons=["speedometer2", "person-workspace"],  # 更改了图标
            menu_icon="house-door",  # 更改了主菜单图标
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#333333", "font-size": "20px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px",
                    "--hover-color": "#eee"
                },
                "nav-link-selected": {"background-color": "#0066cc"},
                "menu-title": {"color": "#333333", "font-size": "18px", "font-weight": "bold"}
            }
        )
    
    # 根据选择显示对应仪表板
    if selected_page == "Executive":
        create_c_level_dashboard(sales_df, agents_df, properties_df, locations_df)
    else:
        create_agent_dashboard(sales_df, agents_df, properties_df)

if __name__ == "__main__":
    main()
