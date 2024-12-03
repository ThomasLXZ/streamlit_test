import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

__all__ = ['create_c_level_dashboard']

def create_c_level_dashboard(sales_df, agents_df, properties_df, locations_df):
    """创建C-Level仪表板"""
    st.title('C-Level Dashboard')
    
    # 基础统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sales", f"${sales_df['sale_price'].sum():,.0f}")
    with col2:
        st.metric("Active Agents", f"{len(agents_df):,}")
    with col3:
        st.metric("Total Properties", f"{len(properties_df):,}")
    with col4:
        st.metric("Regions Covered", f"{len(locations_df['neighborhood'].unique()):,}")
    
    # 销售业绩前20名和后20名员工
    fig_top, fig_bottom = plot_top_bottom_employees(sales_df, agents_df)
    st.plotly_chart(fig_top, use_container_width=True)
    st.plotly_chart(fig_bottom, use_container_width=True)
    
    # 月度总销售额
    fig_monthly = plot_monthly_sales(sales_df)
    st.plotly_chart(fig_monthly, use_container_width=True)

     # 2023年vs2024年销售对比
    fig_year = plot_year_comparison(sales_df)
    st.plotly_chart(fig_year, use_container_width=True)
    
    col5, col6 = st.columns(2)
    with col5:
        # 住宅与商业单位分布
        fig_units = plot_residential_vs_commercial(properties_df)
        st.plotly_chart(fig_units, use_container_width=True)
    
    with col6:
        # 销售热力图
        fig_heatmap = plot_sales_heatmap(sales_df, locations_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
   

def plot_top_bottom_employees(sales_df, agents_df):
    """绘制销售业绩前20名和后20名员工"""
    # 计算每个代理的总销售额
    agent_performance = pd.merge(
        sales_df.groupby('agent_id')['sale_price'].sum().reset_index(),
        agents_df[['agent_id', 'full_name']],
        on='agent_id'
    ).sort_values('sale_price', ascending=False)
    
    # Top 20
    fig_top = px.bar(
        agent_performance.head(20),
        x='full_name',
        y='sale_price',
        title='Top 20 Employees by Sales',
        labels={'sale_price': 'Total Sales ($)', 'full_name': 'Agent Name'}
    )
    fig_top.update_layout(xaxis_tickangle=-45)
    
    # Bottom 20
    fig_bottom = px.bar(
        agent_performance.tail(20),
        x='full_name',
        y='sale_price',
        title='Bottom 20 Employees by Sales',
        labels={'sale_price': 'Total Sales ($)', 'full_name': 'Agent Name'}
    )
    fig_bottom.update_layout(xaxis_tickangle=-45)
    
    return fig_top, fig_bottom

def plot_monthly_sales(sales_df):
    """绘制月度总销售额"""
    monthly_sales = sales_df.groupby(
        sales_df['sale_date'].dt.strftime('%Y-%m')
    )['sale_price'].sum().reset_index()
    
    fig = px.line(
        monthly_sales,
        x='sale_date',
        y='sale_price',
        title='Monthly Total Sales',
        labels={'sale_price': 'Total Sales ($)', 'sale_date': 'Month'}
    )
    return fig

def plot_residential_vs_commercial(properties_df):
    """绘制住宅与商业单位分布"""
    unit_types = pd.DataFrame({
        'Type': ['Residential', 'Commercial'],
        'Units': [
            properties_df['residential_units'].sum(),
            properties_df['commercial_units'].sum()
        ]
    })
    
    fig = px.pie(
        unit_types,
        values='Units',
        names='Type',
        title='Distribution of Residential vs Commercial Units'
    )
    return fig

def plot_sales_heatmap(sales_df, locations_df):
    """绘制销售热力图（按地区和月份）"""
    # 合并销售和位置数据
    sales_location = pd.merge(
        sales_df,
        locations_df,
        left_on='property_id',
        right_on='location_id'
    )
    
    # 获取前20个社区
    top_neighborhoods = sales_location.groupby('neighborhood')['sale_price'].sum()\
        .nlargest(20).index
    
    # 准备热力图数据
    heatmap_data = sales_location[
        sales_location['neighborhood'].isin(top_neighborhoods)
    ].pivot_table(
        values='sale_price',
        index='neighborhood',
        columns=sales_location['sale_date'].dt.strftime('%Y-%m'),
        aggfunc='sum',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        title='Sales Heatmap by Region and Month (Top 20 Neighborhoods)',
        xaxis_title='Month',
        yaxis_title='Neighborhood'
    )
    return fig

def plot_year_comparison(sales_df):
    """绘制年度销售对比"""
    # 准备2023和2024年的数据
    sales_df['year'] = sales_df['sale_date'].dt.year
    sales_df['month'] = sales_df['sale_date'].dt.month
    
    # 过滤掉无效数据
    valid_sales = sales_df[
        (sales_df['agent_id'].notna())     # 过滤掉没有代理人的记录
    ]
    
    yearly_comparison = valid_sales[valid_sales['year'].isin([2023, 2024])].groupby(
        ['year', 'month']
    )['sale_price'].sum().reset_index()
    
    fig = px.line(
        yearly_comparison,
        x='month',
        y='sale_price',
        color='year',
        title='2023 vs 2024 Sales Comparison',
        labels={
            'sale_price': 'Total Sales ($)',
            'month': 'Month',
            'year': 'Year'
        }
    )
    
    # 添加更好的图表格式
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),  # 显示所有月份
        yaxis_title="Total Sales ($)",
        xaxis_title="Month"
    )
    
    return fig
