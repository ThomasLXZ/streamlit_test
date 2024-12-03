import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import plotly.figure_factory as ff

__all__ = ['create_agent_dashboard']

def create_agent_dashboard(sales_df, agents_df, properties_df):
    """创建代理仪表板"""
    st.title('Agent Dashboard')
    
    # 添加KPI指标行
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # 确保sale_date是datetime类型
        sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
        
        # 获取数据集中最后一个日期
        last_date = sales_df['sale_date'].max()
        thirty_days_before = last_date - timedelta(days=30)
        
        monthly_sales = sales_df[
            sales_df['sale_date'].between(thirty_days_before, last_date)
        ]['sale_price'].sum()
        
        # 如果没有销售额，显示0
        monthly_sales = monthly_sales if not pd.isna(monthly_sales) else 0
        st.metric("Monthly Sales", f"${monthly_sales:,.0f}")
    
    with col2:
        avg_price = sales_df['sale_price'].mean()
        st.metric("Average Price", f"${avg_price:,.0f}")
    
    with col3:
        active_properties = len(properties_df)
        st.metric("Active Properties", f"{active_properties:,}")
    
    with col4:
        success_rate = len(sales_df) / len(properties_df) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["Sales Analytics", "Inventory", "Client Management"])
    
    with tab1:
        create_sales_analytics_tab(sales_df, agents_df)
    
    with tab2:
        create_inventory_tab(properties_df, sales_df)
    
    with tab3:
        create_client_management_tab()

def create_sales_analytics_tab(sales_df, agents_df):
    
    # Recent transactions table (using AgGrid)
    show_recent_transactions_grid(sales_df, agents_df)
    
    # Weekly sales trend
    fig_weekly = plot_weekly_trends(sales_df)
    st.plotly_chart(fig_weekly, use_container_width=True)

    # Top 10 agent sales distribution
    fig_top = plot_top_agents_sales(sales_df, agents_df)
    st.plotly_chart(fig_top, use_container_width=True)
    
    # Agent performance heatmap
    fig_heatmap = plot_agent_performance_heatmap(sales_df, agents_df)
    st.plotly_chart(fig_heatmap, use_container_width=True)

def create_inventory_tab(properties_df, sales_df):
    # Merge sales data with properties data
    merged_df = pd.merge(properties_df, sales_df[['property_id', 'sale_price']], 
                        on='property_id', how='left')
    
    # 隐藏销售价格为0或null的行
    merged_df = merged_df[merged_df['sale_price'].notna() & (merged_df['sale_price'] > 0)]
    
    # 定义要隐藏的列
    columns_to_hide = ['property_id', 'location_id', 'class_id', 'apartment_number']
    display_df = merged_df.drop(columns=columns_to_hide)
    
    # Define price tiers
    price_tiers = {
        "Below 100k": (0, 100000),
        "100k - 200k": (100000, 200000),
        "200k - 300k": (200000, 300000),
        "300k - 400k": (300000, 400000),
        "Above 400k": (400000, float("inf")),
    }
    
    # Add selection box in main page
    st.subheader("Inventory Filters")
    selected_tier = st.selectbox("Select Price Range", list(price_tiers.keys()))
    selected_range = price_tiers[selected_tier]
    
    # Filter data based on selected price tier
    filtered_properties = display_df[
        (merged_df['sale_price'] >= selected_range[0]) & 
        (merged_df['sale_price'] <= selected_range[1])
    ]
    
    # Display filtered inventory details
    st.subheader("Filtered Inventory Details")
    st.dataframe(filtered_properties)

def create_client_management_tab():
    # col1, col2 = st.columns([2, 1])
    
    # with col1:
    #     st.subheader("Appointment Requests")
    #     show_appointment_requests()
    
    # with col2:
    st.subheader("Client Statistics")
    show_client_statistics()
        

def show_recent_transactions_grid(sales_df, agents_df, n=10):
    """Use AgGrid to display recent transactions"""
    recent_sales = pd.merge(
        sales_df.nlargest(n, 'sale_date'),
        agents_df[['agent_id', 'full_name', 'email', 'mobile']],
        on='agent_id'
    )
    
    gb = GridOptionsBuilder.from_dataframe(recent_sales)
    gb.configure_pagination(enabled=True, paginationPageSize=5)
    gb.configure_column("sale_date", type=["dateColumnFilter"])
    gb.configure_column("sale_price", type=["numericColumn", "numberColumnFilter"])
    
    grid_options = gb.build()
    
    AgGrid(
        recent_sales,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=300
    )

def plot_price_distribution(sales_df):
    """Plot price distribution histogram"""
    fig = ff.create_distplot(
        [sales_df['sale_price']],
        ['Sale Price'],
        bin_size=1000000
    )
    fig.update_layout(title_text="Price Distribution")
    return fig

def show_client_statistics():
    """Display client statistics (example data)"""
    stats = {
        "Total Clients": 150,
        "Active Leads": 45,
        "Pending Appointments": 12,
        "Completed Viewings": 28
    }
    
    # 创建四列
    col1, col2, col3, col4 = st.columns(4)
    
    # 在每一列中显示一个统计信息
    with col1:
        st.metric("Total Clients", stats["Total Clients"])
    with col2:
        st.metric("Active Leads", stats["Active Leads"])
    with col3:
        st.metric("Pending Appointments", stats["Pending Appointments"])
    with col4:
        st.metric("Completed Viewings", stats["Completed Viewings"])

def plot_top_agents_sales(sales_df, agents_df):
    """Plot sales distribution of top 10 agents"""
    top_agents = pd.merge(
        sales_df.groupby('agent_id')['sale_price'].sum().reset_index(),
        agents_df[['agent_id', 'full_name']],
        on='agent_id'
    ).nlargest(10, 'sale_price')
    
    fig = px.bar(
        top_agents,
        x='full_name',
        y='sale_price',
        title='Sales Distribution by Top 10 Agents',
        labels={'sale_price': 'Total Sales ($)', 'full_name': 'Agent Name'}
    )
    return fig

def plot_agent_performance_heatmap(sales_df, agents_df):
    """Plot agent performance heatmap"""
    agent_performance = pd.merge(
        sales_df,
        agents_df[['agent_id', 'full_name']],
        on='agent_id'
    )
    
    heatmap_data = agent_performance.pivot_table(
        values='property_id',
        index='full_name',
        columns=agent_performance['sale_date'].dt.strftime('%Y-%m'),
        aggfunc='count',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        title='Agent Performance Heatmap (Units Sold)',
        xaxis_title='Month',
        yaxis_title='Agent Name'
    )
    return fig

def plot_weekly_trends(sales_df):
    """Plot weekly sales trend"""
    weekly_sales = sales_df.groupby(
        sales_df['sale_date'].dt.strftime('%Y-%W')
    )['sale_price'].sum().reset_index()
    
    fig = px.line(
        weekly_sales,
        x='sale_date',
        y='sale_price',
        title='Weekly Sales Trends',
        labels={'sale_price': 'Total Sales ($)', 'sale_date': 'Week'}
    )
    return fig

def show_inventory_status(properties_df):
    """Display inventory status overview"""
    total_units = properties_df['total_units'].sum()
    residential_units = properties_df['residential_units'].sum()
    commercial_units = properties_df['commercial_units'].sum()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Residential', 'Commercial'],
            values=[residential_units, commercial_units],
            title='Inventory Status Overview'
        )
    ])
    return fig

def show_appointment_requests():
    """Display client appointment requests"""
    # Create example data
    appointments = pd.DataFrame({
        'client_name': ['Zhang San', 'Li Si', 'Wang Wu'],
        'property_id': ['P001', 'P002', 'P003'],
        'appointment_date': ['2024-03-20', '2024-03-21', '2024-03-22'],
        'status': ['Pending', 'Confirmed', 'Pending']
    })
    
    if appointments.empty:
        st.warning("No appointment requests found.")
    else:
        st.dataframe(appointments)
