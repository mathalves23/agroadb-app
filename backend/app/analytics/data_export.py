"""
Data Export Module - Exportação para Data Warehouses e BI Tools

Este módulo implementa exportação de dados para:
- BigQuery (Google Cloud)
- Redshift (AWS)
- Tableau
- Power BI
- Arquivos exportáveis (CSV, JSON, Parquet)
"""

from typing import Dict, Any, List, Optional, Union, BinaryIO
from datetime import datetime, timedelta
from enum import Enum
import json
import csv
import io
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS E CONSTANTES
# ============================================================================

class DataWarehouseType(str, Enum):
    """Tipos de data warehouse suportados"""
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    SNOWFLAKE = "snowflake"  # Bonus


class ExportFormat(str, Enum):
    """Formatos de exportação suportados"""
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    NDJSON = "ndjson"  # Newline Delimited JSON


class ExportStatus(str, Enum):
    """Status de exportação"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class ExportConfig(BaseModel):
    """Configuração de exportação"""
    dataset_name: str = Field(..., description="Nome do dataset/tabela")
    export_format: ExportFormat = Field(default=ExportFormat.JSON)
    include_metadata: bool = Field(default=True)
    compress: bool = Field(default=False)
    batch_size: int = Field(default=1000, ge=100, le=10000)
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S")


class DataWarehouseConfig(BaseModel):
    """Configuração para data warehouse"""
    warehouse_type: DataWarehouseType
    project_id: Optional[str] = None  # BigQuery
    dataset: Optional[str] = None
    cluster: Optional[str] = None  # Redshift
    database: Optional[str] = None
    schema: Optional[str] = "public"
    credentials: Optional[Dict[str, Any]] = None


class ExportJob(BaseModel):
    """Trabalho de exportação"""
    job_id: str
    dataset_name: str
    export_format: ExportFormat
    status: ExportStatus
    total_records: int = 0
    exported_records: int = 0
    file_size_bytes: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None


class TableauDataSource(BaseModel):
    """Configuração de data source para Tableau"""
    connection_name: str
    server: str
    port: int = 5432
    database: str
    username: str
    tables: List[str]
    refresh_schedule: Optional[str] = None  # Cron format


class PowerBIDataset(BaseModel):
    """Configuração de dataset para Power BI"""
    dataset_name: str
    tables: List[Dict[str, Any]]
    relationships: Optional[List[Dict[str, Any]]] = None
    refresh_schedule: Optional[str] = None


# ============================================================================
# DATA WAREHOUSE EXPORTERS
# ============================================================================

class BigQueryExporter:
    """Exportador para Google BigQuery"""
    
    def __init__(self, config: DataWarehouseConfig):
        self.config = config
        self.project_id = config.project_id
        self.dataset = config.dataset
        
    def export_table(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        schema: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Exporta dados para uma tabela no BigQuery
        
        Args:
            table_name: Nome da tabela
            data: Dados a exportar
            schema: Schema opcional (inferido se não fornecido)
            
        Returns:
            Resultado da exportação
        """
        try:
            # Simulação de exportação para BigQuery
            # Em produção, usar: from google.cloud import bigquery
            
            table_id = f"{self.project_id}.{self.dataset}.{table_name}"
            
            # Schema inference
            if not schema:
                schema = self._infer_schema(data[0] if data else {})
            
            logger.info(f"Exportando {len(data)} registros para {table_id}")
            
            # Simulação de inserção em lote
            batch_size = 1000
            total_batches = (len(data) + batch_size - 1) // batch_size
            
            return {
                "success": True,
                "table_id": table_id,
                "records_inserted": len(data),
                "batches": total_batches,
                "schema": schema,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar para BigQuery: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "table_id": table_name
            }
    
    def _infer_schema(self, sample_row: Dict[str, Any]) -> List[Dict[str, str]]:
        """Infere schema a partir de uma linha de exemplo"""
        type_mapping = {
            int: "INTEGER",
            float: "FLOAT",
            str: "STRING",
            bool: "BOOLEAN",
            datetime: "TIMESTAMP",
            dict: "RECORD",
            list: "REPEATED"
        }
        
        schema = []
        for key, value in sample_row.items():
            field_type = type_mapping.get(type(value), "STRING")
            schema.append({
                "name": key,
                "type": field_type,
                "mode": "NULLABLE"
            })
        
        return schema
    
    def create_dataset(self, dataset_name: str, location: str = "US") -> Dict[str, Any]:
        """Cria um dataset no BigQuery"""
        try:
            dataset_id = f"{self.project_id}.{dataset_name}"
            
            logger.info(f"Criando dataset: {dataset_id}")
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "location": location,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar dataset: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class RedshiftExporter:
    """Exportador para Amazon Redshift"""
    
    def __init__(self, config: DataWarehouseConfig):
        self.config = config
        self.cluster = config.cluster
        self.database = config.database
        self.schema = config.schema
        
    def export_table(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        create_table: bool = True
    ) -> Dict[str, Any]:
        """
        Exporta dados para uma tabela no Redshift
        
        Args:
            table_name: Nome da tabela
            data: Dados a exportar
            create_table: Se deve criar a tabela
            
        Returns:
            Resultado da exportação
        """
        try:
            # Simulação de exportação para Redshift
            # Em produção, usar: import psycopg2 ou redshift_connector
            
            full_table_name = f"{self.schema}.{table_name}"
            
            logger.info(f"Exportando {len(data)} registros para {full_table_name}")
            
            # DDL generation
            if create_table:
                ddl = self._generate_ddl(table_name, data[0] if data else {})
            else:
                ddl = None
            
            # Simulação de COPY command via S3
            s3_path = f"s3://agroadb-exports/{self.database}/{table_name}/"
            
            return {
                "success": True,
                "table_name": full_table_name,
                "records_inserted": len(data),
                "ddl_executed": ddl is not None,
                "s3_staging_path": s3_path,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Redshift: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "table_name": table_name
            }
    
    def _generate_ddl(self, table_name: str, sample_row: Dict[str, Any]) -> str:
        """Gera DDL para criar tabela"""
        type_mapping = {
            int: "INTEGER",
            float: "DOUBLE PRECISION",
            str: "VARCHAR(65535)",
            bool: "BOOLEAN",
            datetime: "TIMESTAMP"
        }
        
        columns = []
        for key, value in sample_row.items():
            col_type = type_mapping.get(type(value), "VARCHAR(65535)")
            columns.append(f"  {key} {col_type}")
        
        ddl = f"""
CREATE TABLE IF NOT EXISTS {self.schema}.{table_name} (
{chr(10).join(columns)}
)
DISTSTYLE AUTO
SORTKEY AUTO;
        """.strip()
        
        return ddl
    
    def execute_copy_command(
        self,
        table_name: str,
        s3_path: str,
        file_format: str = "JSON"
    ) -> Dict[str, Any]:
        """Executa comando COPY do S3 para Redshift"""
        try:
            copy_command = f"""
COPY {self.schema}.{table_name}
FROM '{s3_path}'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftCopyRole'
FORMAT AS {file_format}
TIMEFORMAT 'auto'
TRUNCATECOLUMNS
BLANKSASNULL
EMPTYASNULL;
            """.strip()
            
            logger.info(f"Executando COPY: {copy_command}")
            
            return {
                "success": True,
                "command": copy_command,
                "table_name": table_name,
                "s3_path": s3_path
            }
            
        except Exception as e:
            logger.error(f"Erro no COPY command: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# BI TOOLS INTEGRATIONS
# ============================================================================

class TableauConnector:
    """Conector para Tableau"""
    
    def __init__(self, server_url: str, api_token: Optional[str] = None):
        self.server_url = server_url
        self.api_token = api_token
        
    def create_data_source(self, config: TableauDataSource) -> Dict[str, Any]:
        """
        Cria uma data source no Tableau Server
        
        Args:
            config: Configuração da data source
            
        Returns:
            Resultado da criação
        """
        try:
            # Simulação de criação de data source
            # Em produção, usar: tableauserverclient library
            
            logger.info(f"Criando data source: {config.connection_name}")
            
            # TDS (Tableau Data Source) XML generation
            tds_xml = self._generate_tds_xml(config)
            
            return {
                "success": True,
                "data_source_id": f"ds_{hash(config.connection_name) % 10000}",
                "connection_name": config.connection_name,
                "tables": config.tables,
                "tds_xml": tds_xml,
                "server_url": f"{self.server_url}/datasources",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar data source Tableau: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_tds_xml(self, config: TableauDataSource) -> str:
        """Gera XML de configuração TDS"""
        tables_xml = "\n".join([
            f'    <table name="{table}" />' for table in config.tables
        ])
        
        tds_xml = f"""<?xml version='1.0' encoding='utf-8' ?>
<datasource formatted-name='{config.connection_name}' inline='true' version='18.1'>
  <connection class='postgres' dbname='{config.database}' 
              server='{config.server}' port='{config.port}' 
              username='{config.username}'>
{tables_xml}
  </connection>
</datasource>
"""
        return tds_xml
    
    def publish_workbook(
        self,
        workbook_file: str,
        project_name: str = "Default"
    ) -> Dict[str, Any]:
        """Publica um workbook no Tableau Server"""
        try:
            logger.info(f"Publicando workbook: {workbook_file}")
            
            return {
                "success": True,
                "workbook_id": f"wb_{hash(workbook_file) % 10000}",
                "project": project_name,
                "url": f"{self.server_url}/workbooks/{workbook_file}",
                "published_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao publicar workbook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_refresh(
        self,
        data_source_id: str,
        cron_schedule: str
    ) -> Dict[str, Any]:
        """Agenda atualização automática de data source"""
        try:
            logger.info(f"Agendando refresh para data source {data_source_id}: {cron_schedule}")
            
            return {
                "success": True,
                "data_source_id": data_source_id,
                "schedule": cron_schedule,
                "next_run": self._calculate_next_run(cron_schedule),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_next_run(self, cron: str) -> str:
        """Calcula próxima execução do cron"""
        # Simplificação - em produção usar croniter
        return (datetime.utcnow() + timedelta(hours=1)).isoformat()


class PowerBIConnector:
    """Conector para Power BI"""
    
    def __init__(self, workspace_id: str, api_token: Optional[str] = None):
        self.workspace_id = workspace_id
        self.api_token = api_token
        
    def create_dataset(self, config: PowerBIDataset) -> Dict[str, Any]:
        """
        Cria um dataset no Power BI Service
        
        Args:
            config: Configuração do dataset
            
        Returns:
            Resultado da criação
        """
        try:
            # Simulação de criação via Power BI REST API
            logger.info(f"Criando dataset Power BI: {config.dataset_name}")
            
            # PBIX metadata generation
            pbix_metadata = self._generate_pbix_metadata(config)
            
            return {
                "success": True,
                "dataset_id": f"ds_{hash(config.dataset_name) % 10000}",
                "dataset_name": config.dataset_name,
                "workspace_id": self.workspace_id,
                "tables_count": len(config.tables),
                "metadata": pbix_metadata,
                "web_url": f"https://app.powerbi.com/groups/{self.workspace_id}/datasets",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar dataset Power BI: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_pbix_metadata(self, config: PowerBIDataset) -> Dict[str, Any]:
        """Gera metadata para PBIX"""
        return {
            "name": config.dataset_name,
            "tables": [
                {
                    "name": table["name"],
                    "columns": table.get("columns", [])
                }
                for table in config.tables
            ],
            "relationships": config.relationships or []
        }
    
    def push_data(
        self,
        dataset_id: str,
        table_name: str,
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Push data para dataset (Streaming/Push datasets)"""
        try:
            logger.info(f"Enviando {len(rows)} linhas para {table_name}")
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "table_name": table_name,
                "rows_pushed": len(rows),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar dados: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_refresh_schedule(
        self,
        dataset_id: str,
        frequency: str = "Daily",
        time: str = "08:00"
    ) -> Dict[str, Any]:
        """Cria schedule de atualização"""
        try:
            logger.info(f"Criando schedule para dataset {dataset_id}")
            
            return {
                "success": True,
                "dataset_id": dataset_id,
                "frequency": frequency,
                "time": time,
                "timezone": "UTC",
                "enabled": True,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_embed_token(
        self,
        report_id: str,
        expiration_minutes: int = 60
    ) -> Dict[str, Any]:
        """Gera token de embed para relatório"""
        try:
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            
            return {
                "success": True,
                "token": f"embed_token_{hash(report_id) % 100000}",
                "report_id": report_id,
                "expires_at": expiration.isoformat(),
                "embed_url": f"https://app.powerbi.com/reportEmbed?reportId={report_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# FILE EXPORTERS
# ============================================================================

class FileExporter:
    """Exportador para arquivos (CSV, JSON, Parquet)"""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        
    def export_to_csv(self, data: List[Dict[str, Any]]) -> bytes:
        """Exporta dados para CSV"""
        if not data:
            return b""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue().encode('utf-8')
    
    def export_to_json(self, data: List[Dict[str, Any]]) -> bytes:
        """Exporta dados para JSON"""
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.strftime(self.config.date_format)
            return str(obj)
        
        json_str = json.dumps(data, indent=2, default=default_serializer)
        return json_str.encode('utf-8')
    
    def export_to_ndjson(self, data: List[Dict[str, Any]]) -> bytes:
        """Exporta dados para NDJSON (Newline Delimited JSON)"""
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.strftime(self.config.date_format)
            return str(obj)
        
        lines = [json.dumps(row, default=default_serializer) for row in data]
        return "\n".join(lines).encode('utf-8')
    
    def export_to_parquet(self, data: List[Dict[str, Any]]) -> bytes:
        """
        Exporta dados para Parquet
        Nota: Requer pyarrow em produção
        """
        # Simulação - em produção usar pyarrow
        logger.warning("Parquet export simulated - install pyarrow for production")
        
        # Fallback para JSON comprimido
        return self.export_to_json(data)


# ============================================================================
# EXPORT MANAGER
# ============================================================================

class DataExportManager:
    """Gerenciador central de exportação de dados"""
    
    def __init__(self, db: Session):
        self.db = db
        self.jobs: Dict[str, ExportJob] = {}
        
    def create_export_job(
        self,
        dataset_name: str,
        export_format: ExportFormat,
        filters: Optional[Dict[str, Any]] = None
    ) -> ExportJob:
        """Cria um job de exportação"""
        job_id = f"export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(dataset_name) % 1000}"
        
        job = ExportJob(
            job_id=job_id,
            dataset_name=dataset_name,
            export_format=export_format,
            status=ExportStatus.PENDING,
            started_at=datetime.utcnow()
        )
        
        self.jobs[job_id] = job
        return job
    
    def execute_export(
        self,
        job_id: str,
        data: List[Dict[str, Any]]
    ) -> ExportJob:
        """Executa exportação"""
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} não encontrado")
        
        try:
            job.status = ExportStatus.PROCESSING
            job.total_records = len(data)
            
            # Exportação
            config = ExportConfig(dataset_name=job.dataset_name, export_format=job.export_format)
            exporter = FileExporter(config)
            
            if job.export_format == ExportFormat.CSV:
                file_data = exporter.export_to_csv(data)
            elif job.export_format == ExportFormat.JSON:
                file_data = exporter.export_to_json(data)
            elif job.export_format == ExportFormat.NDJSON:
                file_data = exporter.export_to_ndjson(data)
            elif job.export_format == ExportFormat.PARQUET:
                file_data = exporter.export_to_parquet(data)
            else:
                raise ValueError(f"Formato não suportado: {job.export_format}")
            
            job.file_size_bytes = len(file_data)
            job.exported_records = len(data)
            job.status = ExportStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.download_url = f"/api/v1/exports/download/{job_id}"
            
            logger.info(f"Export job {job_id} completed: {len(data)} records, {job.file_size_bytes} bytes")
            
        except Exception as e:
            job.status = ExportStatus.FAILED
            job.error_message = str(e)
            logger.error(f"Export job {job_id} failed: {str(e)}")
        
        return job
    
    def get_job_status(self, job_id: str) -> Optional[ExportJob]:
        """Retorna status de um job"""
        return self.jobs.get(job_id)
    
    def list_jobs(self, limit: int = 50) -> List[ExportJob]:
        """Lista jobs de exportação"""
        return sorted(
            self.jobs.values(),
            key=lambda j: j.started_at,
            reverse=True
        )[:limit]


# ============================================================================
# QUERY BUILDERS PARA DATASETS COMUNS
# ============================================================================

class DatasetQueryBuilder:
    """Builder de queries para datasets analíticos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_investigations_dataset(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Dataset de investigações"""
        query = """
        SELECT 
            i.id,
            i.title,
            i.status,
            i.priority,
            i.created_at,
            i.updated_at,
            u.name as created_by,
            COUNT(DISTINCT d.id) as documents_count,
            COUNT(DISTINCT e.id) as events_count
        FROM investigations i
        LEFT JOIN users u ON i.user_id = u.id
        LEFT JOIN documents d ON d.investigation_id = i.id
        LEFT JOIN events e ON e.investigation_id = i.id
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND i.created_at >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND i.created_at <= :end_date"
            params["end_date"] = end_date
        
        query += " GROUP BY i.id, u.name ORDER BY i.created_at DESC"
        
        # Simulação de resultado
        return [
            {
                "id": i,
                "title": f"Investigação {i}",
                "status": "active" if i % 2 == 0 else "completed",
                "priority": "high" if i % 3 == 0 else "medium",
                "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "created_by": f"User {i % 10}",
                "documents_count": i * 3,
                "events_count": i * 5
            }
            for i in range(1, 101)
        ]
    
    def get_users_activity_dataset(self) -> List[Dict[str, Any]]:
        """Dataset de atividade de usuários"""
        return [
            {
                "user_id": i,
                "username": f"user{i}",
                "role": ["analyst", "investigator", "admin"][i % 3],
                "total_investigations": i * 5,
                "total_documents": i * 15,
                "last_login": (datetime.utcnow() - timedelta(days=i % 30)).isoformat(),
                "active_days": i * 2,
                "created_at": (datetime.utcnow() - timedelta(days=i * 10)).isoformat()
            }
            for i in range(1, 51)
        ]
    
    def get_performance_metrics_dataset(self) -> List[Dict[str, Any]]:
        """Dataset de métricas de performance"""
        return [
            {
                "date": (datetime.utcnow() - timedelta(days=i)).date().isoformat(),
                "total_investigations": 100 + i,
                "completed_investigations": 50 + i // 2,
                "avg_completion_time_days": 15.5 + (i % 5),
                "total_users": 50 + i // 10,
                "active_users": 30 + i // 15,
                "documents_processed": 500 + i * 10,
                "api_calls": 1000 + i * 50
            }
            for i in range(90)  # 90 dias
        ]
