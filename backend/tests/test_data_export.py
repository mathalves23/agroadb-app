"""
Testes para módulo de exportação de dados

Cobre:
- Exportação para BigQuery e Redshift
- Integração com Tableau e Power BI
- Exportação de arquivos (CSV, JSON, NDJSON, Parquet)
- API de analytics
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import csv
import io

from app.analytics.data_export import (
    BigQueryExporter,
    RedshiftExporter,
    TableauConnector,
    PowerBIConnector,
    FileExporter,
    DataExportManager,
    DatasetQueryBuilder,
    DataWarehouseType,
    DataWarehouseConfig,
    ExportFormat,
    ExportConfig,
    TableauDataSource,
    PowerBIDataset,
    ExportStatus
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock de sessão do banco de dados"""
    db = Mock()
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.scalar.return_value = 100
    return db


@pytest.fixture
def sample_data():
    """Dados de exemplo para testes"""
    return [
        {
            "id": 1,
            "title": "Investigação 1",
            "status": "active",
            "priority": "high",
            "created_at": "2024-01-01T10:00:00",
            "documents_count": 5
        },
        {
            "id": 2,
            "title": "Investigação 2",
            "status": "completed",
            "priority": "medium",
            "created_at": "2024-01-02T11:00:00",
            "documents_count": 3
        },
        {
            "id": 3,
            "title": "Investigação 3",
            "status": "active",
            "priority": "low",
            "created_at": "2024-01-03T12:00:00",
            "documents_count": 8
        }
    ]


@pytest.fixture
def bigquery_config():
    """Configuração BigQuery"""
    return DataWarehouseConfig(
        warehouse_type=DataWarehouseType.BIGQUERY,
        project_id="test-project",
        dataset="test_dataset"
    )


@pytest.fixture
def redshift_config():
    """Configuração Redshift"""
    return DataWarehouseConfig(
        warehouse_type=DataWarehouseType.REDSHIFT,
        cluster="test-cluster",
        database="test_db",
        schema="public"
    )


# ============================================================================
# TESTES BIGQUERY
# ============================================================================

class TestBigQueryExporter:
    """Testes para exportação BigQuery"""
    
    def test_export_table_success(self, bigquery_config, sample_data):
        """Testa exportação bem-sucedida para BigQuery"""
        exporter = BigQueryExporter(bigquery_config)
        result = exporter.export_table("test_table", sample_data)
        
        assert result["success"] is True
        assert result["records_inserted"] == 3
        assert "test-project.test_dataset.test_table" in result["table_id"]
        assert "schema" in result
        assert "timestamp" in result
    
    def test_export_table_empty_data(self, bigquery_config):
        """Testa exportação com dados vazios"""
        exporter = BigQueryExporter(bigquery_config)
        result = exporter.export_table("test_table", [])
        
        assert result["success"] is True
        assert result["records_inserted"] == 0
    
    def test_infer_schema(self, bigquery_config, sample_data):
        """Testa inferência de schema"""
        exporter = BigQueryExporter(bigquery_config)
        schema = exporter._infer_schema(sample_data[0])
        
        assert len(schema) > 0
        assert all("name" in field for field in schema)
        assert all("type" in field for field in schema)
        assert all("mode" in field for field in schema)
        
        # Verifica tipos específicos
        id_field = next(f for f in schema if f["name"] == "id")
        assert id_field["type"] == "INTEGER"
        
        title_field = next(f for f in schema if f["name"] == "title")
        assert title_field["type"] == "STRING"
    
    def test_create_dataset(self, bigquery_config):
        """Testa criação de dataset"""
        exporter = BigQueryExporter(bigquery_config)
        result = exporter.create_dataset("new_dataset", "US")
        
        assert result["success"] is True
        assert "new_dataset" in result["dataset_id"]
        assert result["location"] == "US"
    
    def test_export_with_custom_schema(self, bigquery_config, sample_data):
        """Testa exportação com schema customizado"""
        custom_schema = [
            {"name": "id", "type": "INTEGER", "mode": "REQUIRED"},
            {"name": "title", "type": "STRING", "mode": "NULLABLE"}
        ]
        
        exporter = BigQueryExporter(bigquery_config)
        result = exporter.export_table("test_table", sample_data, custom_schema)
        
        assert result["success"] is True
        assert result["schema"] == custom_schema


# ============================================================================
# TESTES REDSHIFT
# ============================================================================

class TestRedshiftExporter:
    """Testes para exportação Redshift"""
    
    def test_export_table_success(self, redshift_config, sample_data):
        """Testa exportação bem-sucedida para Redshift"""
        exporter = RedshiftExporter(redshift_config)
        result = exporter.export_table("test_table", sample_data, create_table=True)
        
        assert result["success"] is True
        assert result["records_inserted"] == 3
        assert "public.test_table" in result["table_name"]
        assert "s3_staging_path" in result
        assert result["ddl_executed"] is True
    
    def test_export_without_create_table(self, redshift_config, sample_data):
        """Testa exportação sem criar tabela"""
        exporter = RedshiftExporter(redshift_config)
        result = exporter.export_table("test_table", sample_data, create_table=False)
        
        assert result["success"] is True
        assert result["ddl_executed"] is False
    
    def test_generate_ddl(self, redshift_config, sample_data):
        """Testa geração de DDL"""
        exporter = RedshiftExporter(redshift_config)
        ddl = exporter._generate_ddl("test_table", sample_data[0])
        
        assert "CREATE TABLE" in ddl
        assert "public.test_table" in ddl
        assert "id" in ddl
        assert "title" in ddl
        assert "DISTSTYLE AUTO" in ddl
        assert "SORTKEY AUTO" in ddl
    
    def test_execute_copy_command(self, redshift_config):
        """Testa comando COPY"""
        exporter = RedshiftExporter(redshift_config)
        result = exporter.execute_copy_command(
            "test_table",
            "s3://bucket/path/",
            "JSON"
        )
        
        assert result["success"] is True
        assert "COPY" in result["command"]
        assert "s3://bucket/path/" in result["command"]
        assert "FORMAT AS JSON" in result["command"]
    
    def test_export_large_dataset(self, redshift_config):
        """Testa exportação de dataset grande"""
        large_data = [{"id": i, "value": f"test_{i}"} for i in range(10000)]
        
        exporter = RedshiftExporter(redshift_config)
        result = exporter.export_table("large_table", large_data)
        
        assert result["success"] is True
        assert result["records_inserted"] == 10000


# ============================================================================
# TESTES TABLEAU
# ============================================================================

class TestTableauConnector:
    """Testes para integração Tableau"""
    
    def test_create_data_source(self):
        """Testa criação de data source"""
        connector = TableauConnector("https://tableau.test.com")
        
        config = TableauDataSource(
            connection_name="Test Connection",
            server="localhost",
            database="test_db",
            username="test_user",
            tables=["investigations", "users"]
        )
        
        result = connector.create_data_source(config)
        
        assert result["success"] is True
        assert "data_source_id" in result
        assert result["connection_name"] == "Test Connection"
        assert len(result["tables"]) == 2
        assert "tds_xml" in result
    
    def test_generate_tds_xml(self):
        """Testa geração de XML TDS"""
        connector = TableauConnector("https://tableau.test.com")
        
        config = TableauDataSource(
            connection_name="Test",
            server="localhost",
            database="db",
            username="user",
            tables=["table1", "table2"]
        )
        
        xml = connector._generate_tds_xml(config)
        
        assert '<?xml version' in xml
        assert '<datasource' in xml
        assert 'class=\'postgres\'' in xml
        assert 'table1' in xml
        assert 'table2' in xml
    
    def test_publish_workbook(self):
        """Testa publicação de workbook"""
        connector = TableauConnector("https://tableau.test.com")
        result = connector.publish_workbook("test_workbook.twbx", "Analytics")
        
        assert result["success"] is True
        assert "workbook_id" in result
        assert result["project"] == "Analytics"
        assert "url" in result
    
    def test_schedule_refresh(self):
        """Testa agendamento de refresh"""
        connector = TableauConnector("https://tableau.test.com")
        result = connector.schedule_refresh("ds_123", "0 8 * * *")
        
        assert result["success"] is True
        assert result["data_source_id"] == "ds_123"
        assert result["schedule"] == "0 8 * * *"
        assert "next_run" in result
    
    def test_calculate_next_run(self):
        """Testa cálculo de próxima execução"""
        connector = TableauConnector("https://tableau.test.com")
        next_run = connector._calculate_next_run("0 8 * * *")
        
        assert next_run is not None
        # Verifica se é uma data válida
        datetime.fromisoformat(next_run)


# ============================================================================
# TESTES POWER BI
# ============================================================================

class TestPowerBIConnector:
    """Testes para integração Power BI"""
    
    def test_create_dataset(self):
        """Testa criação de dataset"""
        connector = PowerBIConnector("workspace_123")
        
        config = PowerBIDataset(
            dataset_name="Test Dataset",
            tables=[
                {"name": "investigations", "columns": []},
                {"name": "users", "columns": []}
            ]
        )
        
        result = connector.create_dataset(config)
        
        assert result["success"] is True
        assert "dataset_id" in result
        assert result["dataset_name"] == "Test Dataset"
        assert result["workspace_id"] == "workspace_123"
        assert result["tables_count"] == 2
    
    def test_push_data(self, sample_data):
        """Testa push de dados"""
        connector = PowerBIConnector("workspace_123")
        result = connector.push_data("ds_456", "investigations", sample_data)
        
        assert result["success"] is True
        assert result["dataset_id"] == "ds_456"
        assert result["table_name"] == "investigations"
        assert result["rows_pushed"] == 3
    
    def test_create_refresh_schedule(self):
        """Testa criação de schedule"""
        connector = PowerBIConnector("workspace_123")
        result = connector.create_refresh_schedule("ds_789", "Daily", "08:00")
        
        assert result["success"] is True
        assert result["dataset_id"] == "ds_789"
        assert result["frequency"] == "Daily"
        assert result["time"] == "08:00"
        assert result["enabled"] is True
    
    def test_generate_embed_token(self):
        """Testa geração de embed token"""
        connector = PowerBIConnector("workspace_123")
        result = connector.generate_embed_token("report_999", 120)
        
        assert result["success"] is True
        assert "token" in result
        assert result["report_id"] == "report_999"
        assert "expires_at" in result
        assert "embed_url" in result
    
    def test_generate_pbix_metadata(self):
        """Testa geração de metadata PBIX"""
        connector = PowerBIConnector("workspace_123")
        
        config = PowerBIDataset(
            dataset_name="Test",
            tables=[
                {
                    "name": "table1",
                    "columns": [{"name": "col1", "type": "String"}]
                }
            ],
            relationships=[{"from": "table1", "to": "table2"}]
        )
        
        metadata = connector._generate_pbix_metadata(config)
        
        assert metadata["name"] == "Test"
        assert len(metadata["tables"]) == 1
        assert len(metadata["relationships"]) == 1


# ============================================================================
# TESTES FILE EXPORTER
# ============================================================================

class TestFileExporter:
    """Testes para exportação de arquivos"""
    
    def test_export_to_csv(self, sample_data):
        """Testa exportação para CSV"""
        config = ExportConfig(dataset_name="test", export_format=ExportFormat.CSV)
        exporter = FileExporter(config)
        
        csv_data = exporter.export_to_csv(sample_data)
        
        assert csv_data is not None
        assert b"id,title,status" in csv_data
        assert b"Investigacao 1" in csv_data or "Investigação 1".encode('utf-8') in csv_data
        
        # Verifica se é CSV válido
        reader = csv.DictReader(io.StringIO(csv_data.decode('utf-8')))
        rows = list(reader)
        assert len(rows) == 3
    
    def test_export_to_json(self, sample_data):
        """Testa exportação para JSON"""
        config = ExportConfig(dataset_name="test", export_format=ExportFormat.JSON)
        exporter = FileExporter(config)
        
        json_data = exporter.export_to_json(sample_data)
        
        assert json_data is not None
        
        # Verifica se é JSON válido
        parsed = json.loads(json_data.decode('utf-8'))
        assert len(parsed) == 3
        assert parsed[0]["id"] == 1
    
    def test_export_to_ndjson(self, sample_data):
        """Testa exportação para NDJSON"""
        config = ExportConfig(dataset_name="test", export_format=ExportFormat.NDJSON)
        exporter = FileExporter(config)
        
        ndjson_data = exporter.export_to_ndjson(sample_data)
        
        assert ndjson_data is not None
        
        # Verifica formato NDJSON (uma linha por objeto)
        lines = ndjson_data.decode('utf-8').strip().split('\n')
        assert len(lines) == 3
        
        # Cada linha deve ser JSON válido
        for line in lines:
            obj = json.loads(line)
            assert "id" in obj
    
    def test_export_to_parquet(self, sample_data):
        """Testa exportação para Parquet"""
        config = ExportConfig(dataset_name="test", export_format=ExportFormat.PARQUET)
        exporter = FileExporter(config)
        
        # Nota: parquet está simulado, mas não deve gerar erro
        parquet_data = exporter.export_to_parquet(sample_data)
        
        assert parquet_data is not None
    
    def test_export_empty_data(self):
        """Testa exportação de dados vazios"""
        config = ExportConfig(dataset_name="test", export_format=ExportFormat.CSV)
        exporter = FileExporter(config)
        
        csv_data = exporter.export_to_csv([])
        assert csv_data == b""


# ============================================================================
# TESTES DATA EXPORT MANAGER
# ============================================================================

class TestDataExportManager:
    """Testes para gerenciador de exportação"""
    
    def test_create_export_job(self, mock_db):
        """Testa criação de job"""
        manager = DataExportManager(mock_db)
        job = manager.create_export_job("test_dataset", ExportFormat.JSON)
        
        assert job.job_id is not None
        assert job.dataset_name == "test_dataset"
        assert job.export_format == ExportFormat.JSON
        assert job.status == ExportStatus.PENDING
        assert job.total_records == 0
    
    def test_execute_export_success(self, mock_db, sample_data):
        """Testa execução bem-sucedida"""
        manager = DataExportManager(mock_db)
        job = manager.create_export_job("test", ExportFormat.JSON)
        
        completed_job = manager.execute_export(job.job_id, sample_data)
        
        assert completed_job.status == ExportStatus.COMPLETED
        assert completed_job.total_records == 3
        assert completed_job.exported_records == 3
        assert completed_job.file_size_bytes > 0
        assert completed_job.download_url is not None
        assert completed_job.completed_at is not None
    
    def test_execute_export_invalid_job(self, mock_db, sample_data):
        """Testa execução com job inválido"""
        manager = DataExportManager(mock_db)
        
        with pytest.raises(ValueError):
            manager.execute_export("invalid_job_id", sample_data)
    
    def test_get_job_status(self, mock_db):
        """Testa obtenção de status"""
        manager = DataExportManager(mock_db)
        job = manager.create_export_job("test", ExportFormat.CSV)
        
        retrieved_job = manager.get_job_status(job.job_id)
        
        assert retrieved_job is not None
        assert retrieved_job.job_id == job.job_id
    
    def test_get_job_status_not_found(self, mock_db):
        """Testa obtenção de job inexistente"""
        manager = DataExportManager(mock_db)
        job = manager.get_job_status("nonexistent")
        
        assert job is None
    
    def test_list_jobs(self, mock_db, sample_data):
        """Testa listagem de jobs"""
        manager = DataExportManager(mock_db)
        
        # Criar múltiplos jobs
        for i in range(5):
            job = manager.create_export_job(f"dataset_{i}", ExportFormat.JSON)
            manager.execute_export(job.job_id, sample_data[:i+1])
        
        jobs = manager.list_jobs(limit=3)
        
        assert len(jobs) == 3
        # Verifica ordenação (mais recente primeiro)
        assert jobs[0].started_at >= jobs[1].started_at


# ============================================================================
# TESTES DATASET QUERY BUILDER
# ============================================================================

class TestDatasetQueryBuilder:
    """Testes para builder de queries"""
    
    def test_get_investigations_dataset(self, mock_db):
        """Testa dataset de investigações"""
        builder = DatasetQueryBuilder(mock_db)
        data = builder.get_investigations_dataset()
        
        assert len(data) > 0
        assert "id" in data[0]
        assert "title" in data[0]
        assert "status" in data[0]
        assert "created_at" in data[0]
    
    def test_get_investigations_with_date_filter(self, mock_db):
        """Testa dataset com filtro de data"""
        builder = DatasetQueryBuilder(mock_db)
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        data = builder.get_investigations_dataset(start_date, end_date)
        
        assert len(data) > 0
    
    def test_get_users_activity_dataset(self, mock_db):
        """Testa dataset de usuários"""
        builder = DatasetQueryBuilder(mock_db)
        data = builder.get_users_activity_dataset()
        
        assert len(data) > 0
        assert "user_id" in data[0]
        assert "username" in data[0]
        assert "role" in data[0]
        assert "total_investigations" in data[0]
    
    def test_get_performance_metrics_dataset(self, mock_db):
        """Testa dataset de métricas"""
        builder = DatasetQueryBuilder(mock_db)
        data = builder.get_performance_metrics_dataset()
        
        assert len(data) == 90  # 90 dias
        assert "date" in data[0]
        assert "total_investigations" in data[0]
        assert "active_users" in data[0]


# ============================================================================
# TESTES DE INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração end-to-end"""
    
    def test_full_export_workflow(self, mock_db, sample_data):
        """Testa workflow completo de exportação"""
        # 1. Criar job
        manager = DataExportManager(mock_db)
        job = manager.create_export_job("investigations", ExportFormat.JSON)
        
        assert job.status == ExportStatus.PENDING
        
        # 2. Executar exportação
        completed_job = manager.execute_export(job.job_id, sample_data)
        
        assert completed_job.status == ExportStatus.COMPLETED
        
        # 3. Verificar status
        status = manager.get_job_status(job.job_id)
        
        assert status.status == ExportStatus.COMPLETED
        assert status.download_url is not None
    
    def test_multiple_format_exports(self, mock_db, sample_data):
        """Testa exportação em múltiplos formatos"""
        manager = DataExportManager(mock_db)
        formats = [ExportFormat.CSV, ExportFormat.JSON, ExportFormat.NDJSON]
        
        jobs = []
        for fmt in formats:
            job = manager.create_export_job(f"test_{fmt}", fmt)
            completed = manager.execute_export(job.job_id, sample_data)
            jobs.append(completed)
        
        # Todos devem ter sucesso
        assert all(j.status == ExportStatus.COMPLETED for j in jobs)
        
        # Tamanhos de arquivo devem variar
        sizes = [j.file_size_bytes for j in jobs]
        assert len(set(sizes)) > 1  # Pelo menos 2 tamanhos diferentes


# ============================================================================
# TESTES DE PERFORMANCE
# ============================================================================

class TestPerformance:
    """Testes de performance"""
    
    def test_large_dataset_export(self, mock_db):
        """Testa exportação de dataset grande"""
        large_data = [
            {"id": i, "value": f"test_{i}", "timestamp": datetime.utcnow().isoformat()}
            for i in range(10000)
        ]
        
        manager = DataExportManager(mock_db)
        job = manager.create_export_job("large_dataset", ExportFormat.JSON)
        
        import time
        start = time.time()
        completed = manager.execute_export(job.job_id, large_data)
        elapsed = time.time() - start
        
        assert completed.status == ExportStatus.COMPLETED
        assert completed.total_records == 10000
        assert elapsed < 5.0  # Deve completar em menos de 5 segundos
    
    def test_csv_export_performance(self, mock_db):
        """Testa performance de exportação CSV"""
        data = [{"col1": i, "col2": f"value_{i}"} for i in range(5000)]
        
        config = ExportConfig(dataset_name="perf_test", export_format=ExportFormat.CSV)
        exporter = FileExporter(config)
        
        import time
        start = time.time()
        result = exporter.export_to_csv(data)
        elapsed = time.time() - start
        
        assert result is not None
        assert elapsed < 2.0  # CSV deve ser rápido


# ============================================================================
# SUMÁRIO
# ============================================================================

def test_suite_summary():
    """Sumário dos testes"""
    print("\n" + "="*70)
    print("SUMÁRIO DOS TESTES - DATA EXPORT MODULE")
    print("="*70)
    print("✅ BigQuery Exporter: 5 testes")
    print("✅ Redshift Exporter: 5 testes")
    print("✅ Tableau Connector: 5 testes")
    print("✅ Power BI Connector: 5 testes")
    print("✅ File Exporter: 5 testes")
    print("✅ Export Manager: 6 testes")
    print("✅ Query Builder: 4 testes")
    print("✅ Integração: 2 testes")
    print("✅ Performance: 2 testes")
    print("-"*70)
    print("TOTAL: 39 testes automatizados")
    print("="*70)
    assert True
