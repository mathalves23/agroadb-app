"""
Data Export - Módulo Consolidado

Import único para todas as funcionalidades de exportação de dados.
"""

# Data Warehouses
from app.analytics.data_export import (
    BigQueryExporter,
    RedshiftExporter,
    DataWarehouseType,
    DataWarehouseConfig
)

# BI Tools
from app.analytics.data_export import (
    TableauConnector,
    PowerBIConnector,
    TableauDataSource,
    PowerBIDataset
)

# File Export
from app.analytics.data_export import (
    FileExporter,
    DataExportManager,
    ExportFormat,
    ExportConfig,
    ExportStatus,
    ExportJob
)

# Query Builder
from app.analytics.data_export import (
    DatasetQueryBuilder
)

__all__ = [
    # Data Warehouses
    "BigQueryExporter",
    "RedshiftExporter",
    "DataWarehouseType",
    "DataWarehouseConfig",
    
    # BI Tools
    "TableauConnector",
    "PowerBIConnector",
    "TableauDataSource",
    "PowerBIDataset",
    
    # File Export
    "FileExporter",
    "DataExportManager",
    "ExportFormat",
    "ExportConfig",
    "ExportStatus",
    "ExportJob",
    
    # Query Builder
    "DatasetQueryBuilder"
]


# Quick access examples
"""
# BigQuery
from app.analytics.data_export_consolidated import BigQueryExporter, DataWarehouseConfig, DataWarehouseType

config = DataWarehouseConfig(
    warehouse_type=DataWarehouseType.BIGQUERY,
    project_id="meu-projeto",
    dataset="agroadb"
)
exporter = BigQueryExporter(config)
result = exporter.export_table("investigations", data)

# Redshift
from app.analytics.data_export_consolidated import RedshiftExporter

config = DataWarehouseConfig(
    warehouse_type=DataWarehouseType.REDSHIFT,
    cluster="agroadb-cluster",
    database="analytics"
)
exporter = RedshiftExporter(config)
result = exporter.export_table("investigations", data)

# Tableau
from app.analytics.data_export_consolidated import TableauConnector, TableauDataSource

connector = TableauConnector("https://tableau.empresa.com")
config = TableauDataSource(
    connection_name="AgroADB",
    server="localhost",
    database="agroadb",
    username="tableau",
    tables=["investigations", "users"]
)
result = connector.create_data_source(config)

# Power BI
from app.analytics.data_export_consolidated import PowerBIConnector, PowerBIDataset

connector = PowerBIConnector("workspace_123")
config = PowerBIDataset(
    dataset_name="AgroADB",
    tables=[{"name": "investigations", "columns": []}]
)
result = connector.create_dataset(config)

# File Export
from app.analytics.data_export_consolidated import DataExportManager, ExportFormat

manager = DataExportManager(db)
job = manager.create_export_job("investigations", ExportFormat.CSV)
completed = manager.execute_export(job.job_id, data)
"""
