"""
Data Export API Routes - Endpoints para exportação de dados

API completa para exportação para Data Warehouses e BI Tools
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.database import get_db
from app.models import User
from app.auth import require_role

from .data_export import (
    BigQueryExporter,
    RedshiftExporter,
    TableauConnector,
    PowerBIConnector,
    DataExportManager,
    DatasetQueryBuilder,
    FileExporter,
    DataWarehouseType,
    DataWarehouseConfig,
    ExportFormat,
    ExportConfig,
    TableauDataSource,
    PowerBIDataset,
    ExportJob
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics/export", tags=["Data Export"])


# ============================================================================
# DATA WAREHOUSE ENDPOINTS
# ============================================================================

@router.post("/warehouse/bigquery")
async def export_to_bigquery(
    project_id: str = Query(..., description="Google Cloud Project ID"),
    dataset: str = Query(..., description="BigQuery dataset"),
    table_name: str = Query(..., description="Nome da tabela"),
    data_source: str = Query("investigations", description="Fonte de dados"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Exporta dados para Google BigQuery
    
    **Fontes de dados disponíveis:**
    - investigations: Dados de investigações
    - users_activity: Atividade de usuários
    - performance_metrics: Métricas de performance
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/warehouse/bigquery?project_id=my-project&dataset=agroadb&table_name=investigations
    ```
    """
    try:
        # Configuração
        config = DataWarehouseConfig(
            warehouse_type=DataWarehouseType.BIGQUERY,
            project_id=project_id,
            dataset=dataset
        )
        
        # Obter dados
        query_builder = DatasetQueryBuilder(db)
        
        if data_source == "investigations":
            data = query_builder.get_investigations_dataset(start_date, end_date)
        elif data_source == "users_activity":
            data = query_builder.get_users_activity_dataset()
        elif data_source == "performance_metrics":
            data = query_builder.get_performance_metrics_dataset()
        else:
            raise HTTPException(status_code=400, detail=f"Fonte de dados inválida: {data_source}")
        
        # Exportar
        exporter = BigQueryExporter(config)
        result = exporter.export_table(table_name, data)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"BigQuery export by {current_user.username}: {table_name} ({len(data)} records)")
        
        return {
            "success": True,
            "warehouse": "bigquery",
            "table_id": result["table_id"],
            "records_exported": result["records_inserted"],
            "schema": result["schema"],
            "timestamp": result["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na exportação BigQuery: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/warehouse/redshift")
async def export_to_redshift(
    cluster: str = Query(..., description="Redshift cluster"),
    database: str = Query(..., description="Database name"),
    table_name: str = Query(..., description="Nome da tabela"),
    schema: str = Query("public", description="Schema"),
    data_source: str = Query("investigations", description="Fonte de dados"),
    create_table: bool = Query(True, description="Criar tabela se não existir"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Exporta dados para Amazon Redshift
    
    **Processo:**
    1. Dados são exportados para S3 (staging)
    2. Comando COPY carrega do S3 para Redshift
    3. Tabela é criada automaticamente se necessário
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/warehouse/redshift?cluster=agroadb&database=analytics&table_name=investigations
    ```
    """
    try:
        # Configuração
        config = DataWarehouseConfig(
            warehouse_type=DataWarehouseType.REDSHIFT,
            cluster=cluster,
            database=database,
            schema=schema
        )
        
        # Obter dados
        query_builder = DatasetQueryBuilder(db)
        
        if data_source == "investigations":
            data = query_builder.get_investigations_dataset(start_date, end_date)
        elif data_source == "users_activity":
            data = query_builder.get_users_activity_dataset()
        elif data_source == "performance_metrics":
            data = query_builder.get_performance_metrics_dataset()
        else:
            raise HTTPException(status_code=400, detail=f"Fonte de dados inválida: {data_source}")
        
        # Exportar
        exporter = RedshiftExporter(config)
        result = exporter.export_table(table_name, data, create_table)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"Redshift export by {current_user.username}: {table_name} ({len(data)} records)")
        
        return {
            "success": True,
            "warehouse": "redshift",
            "table_name": result["table_name"],
            "records_exported": result["records_inserted"],
            "s3_staging_path": result["s3_staging_path"],
            "ddl_executed": result["ddl_executed"],
            "timestamp": result["timestamp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na exportação Redshift: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BI TOOLS ENDPOINTS
# ============================================================================

@router.post("/bi/tableau/datasource")
async def create_tableau_datasource(
    server_url: str = Query(..., description="Tableau Server URL"),
    connection_name: str = Query(..., description="Nome da conexão"),
    db_server: str = Query(..., description="Database server"),
    db_name: str = Query(..., description="Database name"),
    db_username: str = Query(..., description="Database username"),
    tables: List[str] = Query(..., description="Tabelas a incluir"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Cria uma data source no Tableau Server
    
    **Gera:**
    - Arquivo TDS (Tableau Data Source)
    - Conexão configurada no servidor
    - Metadata para tabelas selecionadas
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/bi/tableau/datasource
    ?server_url=https://tableau.company.com
    &connection_name=AgroADB Analytics
    &db_server=localhost
    &db_name=agroadb
    &db_username=tableau_user
    &tables=investigations&tables=users&tables=documents
    ```
    """
    try:
        connector = TableauConnector(server_url)
        
        config = TableauDataSource(
            connection_name=connection_name,
            server=db_server,
            database=db_name,
            username=db_username,
            tables=tables
        )
        
        result = connector.create_data_source(config)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"Tableau datasource created by {current_user.username}: {connection_name}")
        
        return {
            "success": True,
            "bi_tool": "tableau",
            "data_source_id": result["data_source_id"],
            "connection_name": result["connection_name"],
            "tables": result["tables"],
            "tds_xml": result["tds_xml"],
            "server_url": result["server_url"],
            "created_at": result["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar datasource Tableau: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bi/tableau/schedule")
async def schedule_tableau_refresh(
    server_url: str = Query(..., description="Tableau Server URL"),
    data_source_id: str = Query(..., description="ID da data source"),
    cron_schedule: str = Query("0 8 * * *", description="Cron schedule (padrão: diariamente às 8h)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """
    Agenda atualização automática de data source no Tableau
    
    **Exemplos de cron:**
    - `0 8 * * *` - Diariamente às 8h
    - `0 */6 * * *` - A cada 6 horas
    - `0 0 * * 0` - Semanalmente aos domingos
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/bi/tableau/schedule
    ?data_source_id=ds_1234
    &cron_schedule=0 8 * * *
    ```
    """
    try:
        connector = TableauConnector(server_url)
        result = connector.schedule_refresh(data_source_id, cron_schedule)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"Tableau refresh scheduled by {current_user.username}: {data_source_id}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao agendar refresh Tableau: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bi/powerbi/dataset")
async def create_powerbi_dataset(
    workspace_id: str = Query(..., description="Power BI Workspace ID"),
    dataset_name: str = Query(..., description="Nome do dataset"),
    tables: List[Dict[str, Any]] = Query(..., description="Tabelas e schemas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Cria um dataset no Power BI Service
    
    **Estrutura de tabelas:**
    ```json
    [
        {
            "name": "investigations",
            "columns": [
                {"name": "id", "dataType": "Int64"},
                {"name": "title", "dataType": "String"},
                {"name": "status", "dataType": "String"},
                {"name": "created_at", "dataType": "DateTime"}
            ]
        }
    ]
    ```
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/bi/powerbi/dataset
    ```
    """
    try:
        connector = PowerBIConnector(workspace_id)
        
        config = PowerBIDataset(
            dataset_name=dataset_name,
            tables=tables
        )
        
        result = connector.create_dataset(config)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"Power BI dataset created by {current_user.username}: {dataset_name}")
        
        return {
            "success": True,
            "bi_tool": "powerbi",
            "dataset_id": result["dataset_id"],
            "dataset_name": result["dataset_name"],
            "workspace_id": result["workspace_id"],
            "tables_count": result["tables_count"],
            "web_url": result["web_url"],
            "created_at": result["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar dataset Power BI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bi/powerbi/push")
async def push_to_powerbi(
    dataset_id: str = Query(..., description="ID do dataset"),
    table_name: str = Query(..., description="Nome da tabela"),
    data_source: str = Query("investigations", description="Fonte de dados"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Push de dados para Power BI (Streaming/Push datasets)
    
    **Ideal para:**
    - Real-time dashboards
    - Atualizações incrementais
    - Datasets pequenos (< 10k linhas)
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/bi/powerbi/push
    ?dataset_id=ds_5678
    &table_name=investigations
    &data_source=investigations
    ```
    """
    try:
        # Obter dados
        query_builder = DatasetQueryBuilder(db)
        
        if data_source == "investigations":
            data = query_builder.get_investigations_dataset(start_date, end_date)
        elif data_source == "users_activity":
            data = query_builder.get_users_activity_dataset()
        elif data_source == "performance_metrics":
            data = query_builder.get_performance_metrics_dataset()
        else:
            raise HTTPException(status_code=400, detail=f"Fonte de dados inválida: {data_source}")
        
        # Push
        connector = PowerBIConnector("default_workspace")
        result = connector.push_data(dataset_id, table_name, data)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"Power BI push by {current_user.username}: {table_name} ({len(data)} records)")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no push Power BI: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bi/powerbi/embed-token/{report_id}")
async def get_powerbi_embed_token(
    report_id: str,
    expiration_minutes: int = Query(60, ge=5, le=1440),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """
    Gera token de embed para relatório Power BI
    
    **Uso:**
    - Embedding de relatórios em aplicações web
    - Token temporário com expiração configurável
    
    **Exemplo:**
    ```
    GET /api/v1/analytics/export/bi/powerbi/embed-token/report_123?expiration_minutes=120
    ```
    """
    try:
        connector = PowerBIConnector("default_workspace")
        result = connector.generate_embed_token(report_id, expiration_minutes)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        logger.info(f"Power BI embed token generated for {current_user.username}: {report_id}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar embed token: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FILE EXPORT ENDPOINTS
# ============================================================================

@router.post("/file/create")
async def create_file_export_job(
    data_source: str = Query(..., description="Fonte de dados"),
    export_format: ExportFormat = Query(ExportFormat.JSON, description="Formato de exportação"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Cria job de exportação de arquivo
    
    **Formatos suportados:**
    - csv: Comma-Separated Values
    - json: JSON formatado
    - ndjson: Newline Delimited JSON (para streaming)
    - parquet: Apache Parquet (colunar)
    
    **Fontes de dados:**
    - investigations
    - users_activity
    - performance_metrics
    
    **Exemplo:**
    ```
    POST /api/v1/analytics/export/file/create
    ?data_source=investigations
    &export_format=csv
    &start_date=2024-01-01
    ```
    """
    try:
        # Criar job
        manager = DataExportManager(db)
        job = manager.create_export_job(data_source, export_format)
        
        # Obter dados
        query_builder = DatasetQueryBuilder(db)
        
        if data_source == "investigations":
            data = query_builder.get_investigations_dataset(start_date, end_date)
        elif data_source == "users_activity":
            data = query_builder.get_users_activity_dataset()
        elif data_source == "performance_metrics":
            data = query_builder.get_performance_metrics_dataset()
        else:
            raise HTTPException(status_code=400, detail=f"Fonte de dados inválida: {data_source}")
        
        # Executar exportação
        job = manager.execute_export(job.job_id, data)
        
        logger.info(f"File export created by {current_user.username}: {job.job_id}")
        
        return {
            "success": True,
            "job_id": job.job_id,
            "dataset_name": job.dataset_name,
            "export_format": job.export_format,
            "status": job.status,
            "total_records": job.total_records,
            "file_size_bytes": job.file_size_bytes,
            "download_url": job.download_url,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar export job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/status/{job_id}")
async def get_export_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Retorna status de job de exportação
    
    **Exemplo:**
    ```
    GET /api/v1/analytics/export/file/status/export_20240115120000_123
    ```
    """
    try:
        manager = DataExportManager(db)
        job = manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
        
        return {
            "job_id": job.job_id,
            "dataset_name": job.dataset_name,
            "export_format": job.export_format,
            "status": job.status,
            "total_records": job.total_records,
            "exported_records": job.exported_records,
            "file_size_bytes": job.file_size_bytes,
            "download_url": job.download_url,
            "started_at": job.started_at.isoformat(),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "error_message": job.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/list")
async def list_export_jobs(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Lista jobs de exportação
    
    **Exemplo:**
    ```
    GET /api/v1/analytics/export/file/list?limit=20
    ```
    """
    try:
        manager = DataExportManager(db)
        jobs = manager.list_jobs(limit)
        
        return {
            "total": len(jobs),
            "jobs": [
                {
                    "job_id": job.job_id,
                    "dataset_name": job.dataset_name,
                    "export_format": job.export_format,
                    "status": job.status,
                    "total_records": job.total_records,
                    "file_size_bytes": job.file_size_bytes,
                    "started_at": job.started_at.isoformat(),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/download/{job_id}")
async def download_export_file(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst"]))
):
    """
    Download do arquivo exportado
    
    **Exemplo:**
    ```
    GET /api/v1/analytics/export/file/download/export_20240115120000_123
    ```
    """
    try:
        manager = DataExportManager(db)
        job = manager.get_job_status(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} não encontrado")
        
        if job.status != "completed":
            raise HTTPException(status_code=400, detail=f"Job não completado. Status: {job.status}")
        
        # Em produção, retornar arquivo real
        # Por ora, retornar metadata
        
        logger.info(f"File downloaded by {current_user.username}: {job_id}")
        
        return {
            "job_id": job.job_id,
            "dataset_name": job.dataset_name,
            "export_format": job.export_format,
            "file_size_bytes": job.file_size_bytes,
            "download_url": job.download_url,
            "note": "Em produção, retornaria o arquivo binário"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API DE ANALYTICS (QUERY)
# ============================================================================

@router.get("/query/datasets")
async def list_available_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """
    Lista datasets disponíveis para exportação
    
    **Exemplo:**
    ```
    GET /api/v1/analytics/export/query/datasets
    ```
    """
    return {
        "datasets": [
            {
                "name": "investigations",
                "description": "Dados completos de investigações",
                "columns": ["id", "title", "status", "priority", "created_at", "updated_at", 
                           "created_by", "documents_count", "events_count"],
                "estimated_rows": 1000,
                "supports_date_filter": True
            },
            {
                "name": "users_activity",
                "description": "Atividade e estatísticas de usuários",
                "columns": ["user_id", "username", "role", "total_investigations", 
                           "total_documents", "last_login", "active_days", "created_at"],
                "estimated_rows": 50,
                "supports_date_filter": False
            },
            {
                "name": "performance_metrics",
                "description": "Métricas de performance do sistema (90 dias)",
                "columns": ["date", "total_investigations", "completed_investigations", 
                           "avg_completion_time_days", "total_users", "active_users", 
                           "documents_processed", "api_calls"],
                "estimated_rows": 90,
                "supports_date_filter": True
            }
        ]
    }


@router.get("/query/preview")
async def preview_dataset(
    dataset_name: str = Query(..., description="Nome do dataset"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "viewer"]))
):
    """
    Preview de dataset (primeiras linhas)
    
    **Exemplo:**
    ```
    GET /api/v1/analytics/export/query/preview?dataset_name=investigations&limit=5
    ```
    """
    try:
        query_builder = DatasetQueryBuilder(db)
        
        if dataset_name == "investigations":
            data = query_builder.get_investigations_dataset()[:limit]
        elif dataset_name == "users_activity":
            data = query_builder.get_users_activity_dataset()[:limit]
        elif dataset_name == "performance_metrics":
            data = query_builder.get_performance_metrics_dataset()[:limit]
        else:
            raise HTTPException(status_code=400, detail=f"Dataset inválido: {dataset_name}")
        
        return {
            "dataset_name": dataset_name,
            "rows_returned": len(data),
            "preview": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no preview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check do módulo de exportação"""
    return {
        "status": "healthy",
        "module": "data_export",
        "features": {
            "data_warehouses": ["bigquery", "redshift"],
            "bi_tools": ["tableau", "powerbi"],
            "export_formats": ["csv", "json", "ndjson", "parquet"],
            "datasets": ["investigations", "users_activity", "performance_metrics"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }
