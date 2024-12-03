# Real Estate Database Management System

基于 Python、PostgreSQL 和 Streamlit 的房地产数据库管理系统。

## 功能特点

- 数据迁移和处理
- 代理数据分析仪表板
- 管理层数据分析仪表板
- 地址标准化
- 数据验证和清洗

## 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd streamlit_postgres
   ```

2. **创建并激活虚拟环境**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**
   - 安装 PostgreSQL
   - 创建数据库：
     ```sql
     CREATE DATABASE real_estate_db;
     ```
   - 复制 `.env.example` 到 `.env` 并更新配置：
     ```
     DB_HOST=localhost
     DB_NAME=real_estate_db
     DB_USER=postgres
     DB_PASSWORD=你的密码
     ```

5. **数据迁移**
   ```bash
   python db_operations.py
   ```

6. **运行应用**
   ```bash
   streamlit run app.py
   ```

## 项目结构

```
streamlit_postgres/
├── database/                    # 数据库模块
│   ├── __init__.py
│   ├── connection.py           # 数据库连接管理
│   ├── models.py              # 数据表模型定义
│   ├── data_loader.py         # 数据加载功能
│   ├── data_migration.py      # 数据迁移协调器
│   ├── processors/            # 数据处理模块
│   │   ├── __init__.py
│   │   ├── agent_processor.py
│   │   ├── location_processor.py
│   │   ├── property_processor.py
│   │   ├── sales_processor.py
│   │   └── building_processor.py
│   └── utils/                 # 工具函数
│       ├── __init__.py
│       ├── address_utils.py
│       └── data_validation.py
├── app.py                     # Streamlit主应用
├── agent_dashboard.py         # 代理仪表板
├── c_level_dashboard.py       # 管理层仪表板
├── db_operations.py          # 数据迁移脚本
├── requirements.txt          # 项目依赖
└── .env                      # 环境配置
```

## 使用说明

1. **数据迁移**
   - 运行 `python db_operations.py` 执行数据迁移
   - 迁移过程包括：创建表、数据清洗、数据导入

2. **启动应用**
   - 运行 `streamlit run app.py` 启动主应用
   - 访问 http://localhost:8501 查看仪表板

## 注意事项

1. 确保 PostgreSQL 服务正在运行
2. 检查 `.env` 文件中的数据库配置是否正确
3. 数据迁移可能需要几分钟时间，请耐心等待
4. 如遇问题，请检查日志输出
