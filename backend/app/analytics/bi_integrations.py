"""
Integrações com ferramentas de Business Intelligence

Este módulo fornece conectores e adaptadores para ferramentas de BI externas.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from enum import Enum
import logging
import json

from app.analytics import MetricsCalculator, AnalyticsAggregator

logger = logging.getLogger(__name__)


class BITool(str, Enum):
    """Ferramentas de BI suportadas"""
    METABASE = "metabase"
    POWERBI = "powerbi"
    TABLEAU = "tableau"
    LOOKER = "looker"
    REDASH = "redash"


class DatasetSchema(BaseModel):
    """Schema de dataset para BI"""
    name: str
    description: str
    fields: List[Dict[str, str]]
    sample_data: Optional[List[Dict]] = None


class BIConnection(BaseModel):
    """Configuração de conexão com BI tool"""
    tool: BITool
    connection_string: Optional[str] = None
    api_key: Optional[str] = None
    database_name: Optional[str] = None
    schema: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None


class MetabaseConnector:
    """
    Conector para Metabase
    
    Metabase pode se conectar diretamente ao PostgreSQL ou consumir APIs REST
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
    
    def get_connection_config(self) -> Dict[str, Any]:
        """
        Retorna configuração para conectar Metabase ao PostgreSQL
        
        No Metabase, vá em Admin > Databases > Add Database
        """
        return {
            "engine": "postgres",
            "name": "AgroADB Analytics",
            "details": {
                "host": "localhost",  # Alterar para seu host
                "port": 5432,
                "dbname": "agroadb",
                "user": "seu_usuario",
                "password": "sua_senha",
                "ssl": True,
                "tunnel-enabled": False
            },
            "auto_run_queries": True,
            "is_full_sync": True,
            "schedules": {
                "metadata_sync": {
                    "schedule_day": None,
                    "schedule_frame": None,
                    "schedule_hour": 0,
                    "schedule_type": "daily"
                }
            }
        }
    
    def get_suggested_questions(self) -> List[Dict[str, str]]:
        """
        Retorna perguntas sugeridas para criar no Metabase
        
        Metabase permite criar queries SQL ou usar interface visual
        """
        return [
            {
                "name": "Total de Investigações por Status",
                "sql": """
                    SELECT 
                        status,
                        COUNT(*) as total
                    FROM investigations
                    GROUP BY status
                    ORDER BY total DESC
                """,
                "visualization": "pie"
            },
            {
                "name": "Investigações Criadas por Dia (Últimos 30 dias)",
                "sql": """
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as investigations
                    FROM investigations
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date
                """,
                "visualization": "line"
            },
            {
                "name": "Top 10 Usuários Mais Ativos",
                "sql": """
                    SELECT 
                        u.username,
                        u.email,
                        COUNT(i.id) as investigations
                    FROM users u
                    LEFT JOIN investigations i ON i.user_id = u.id
                    GROUP BY u.id, u.username, u.email
                    ORDER BY investigations DESC
                    LIMIT 10
                """,
                "visualization": "table"
            },
            {
                "name": "Taxa de Conclusão por Mês",
                "sql": """
                    SELECT 
                        DATE_TRUNC('month', created_at) as month,
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        ROUND(
                            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)::numeric / 
                            COUNT(*)::numeric * 100, 
                            2
                        ) as completion_rate
                    FROM investigations
                    GROUP BY DATE_TRUNC('month', created_at)
                    ORDER BY month DESC
                """,
                "visualization": "line"
            },
            {
                "name": "Distribuição de Propriedades por Estado",
                "sql": """
                    SELECT 
                        additional_data->>'state' as state,
                        COUNT(*) as properties,
                        SUM((additional_data->>'area_hectares')::numeric) as total_area
                    FROM properties
                    WHERE additional_data->>'state' IS NOT NULL
                    GROUP BY additional_data->>'state'
                    ORDER BY properties DESC
                """,
                "visualization": "bar"
            }
        ]
    
    def create_dashboard_template(self) -> Dict[str, Any]:
        """Template de dashboard para Metabase"""
        return {
            "name": "AgroADB - Dashboard Principal",
            "description": "Visão geral das métricas da plataforma",
            "cards": [
                {
                    "name": "Total de Usuários",
                    "type": "scalar",
                    "sql": "SELECT COUNT(*) FROM users WHERE is_active = true"
                },
                {
                    "name": "Investigações Ativas",
                    "type": "scalar",
                    "sql": "SELECT COUNT(*) FROM investigations WHERE status = 'in_progress'"
                },
                {
                    "name": "Taxa de Conclusão",
                    "type": "scalar",
                    "sql": """
                        SELECT ROUND(
                            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)::numeric / 
                            COUNT(*)::numeric * 100, 
                            2
                        ) 
                        FROM investigations
                    """
                },
                {
                    "name": "Atividade por Dia",
                    "type": "timeseries",
                    "sql": """
                        SELECT 
                            DATE(created_at) as date,
                            COUNT(*) as count
                        FROM investigations
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                        GROUP BY DATE(created_at)
                        ORDER BY date
                    """
                }
            ]
        }


class PowerBIConnector:
    """
    Conector para Microsoft Power BI
    
    Power BI pode consumir dados via:
    1. Direct Query ao PostgreSQL
    2. API REST (recomendado para dados agregados)
    3. Arquivos Excel/CSV
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
        self.aggregator = AnalyticsAggregator(db)
    
    def get_connection_config(self) -> Dict[str, Any]:
        """
        Configuração para conectar Power BI ao PostgreSQL
        
        No Power BI Desktop:
        Get Data > Database > PostgreSQL
        """
        return {
            "type": "PostgreSQL",
            "server": "localhost",  # Seu servidor
            "database": "agroadb",
            "authentication": "Database",
            "username": "seu_usuario",
            "password": "sua_senha",
            "connection_mode": "DirectQuery",  # ou "Import"
            "advanced_options": {
                "command_timeout": "30",
                "native_query": None,
                "relationship_columns": True
            }
        }
    
    def export_for_powerbi(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Exporta dados em formato otimizado para Power BI
        
        Retorna estrutura tabular flat (ideal para Power BI)
        """
        summary = self.aggregator.generate_executive_summary(start_date, end_date)
        
        # Tabela de fatos: Investigações
        investigations_table = {
            "name": "Investigations",
            "columns": [
                {"name": "InvestigationID", "type": "Integer"},
                {"name": "UserID", "type": "Integer"},
                {"name": "Status", "type": "String"},
                {"name": "CreatedAt", "type": "DateTime"},
                {"name": "CompletedAt", "type": "DateTime"},
                {"name": "DurationHours", "type": "Decimal"},
                {"name": "PropertiesCount", "type": "Integer"},
                {"name": "CompaniesCount", "type": "Integer"}
            ],
            "relationships": [
                {"to_table": "Users", "from_column": "UserID", "to_column": "UserID"}
            ]
        }
        
        # Tabela de dimensão: Usuários
        users_table = {
            "name": "Users",
            "columns": [
                {"name": "UserID", "type": "Integer"},
                {"name": "Username", "type": "String"},
                {"name": "Email", "type": "String"},
                {"name": "IsActive", "type": "Boolean"},
                {"name": "CreatedAt", "type": "DateTime"}
            ]
        }
        
        # Tabela de métricas agregadas
        metrics_table = {
            "name": "DailyMetrics",
            "columns": [
                {"name": "Date", "type": "Date"},
                {"name": "InvestigationsCreated", "type": "Integer"},
                {"name": "InvestigationsCompleted", "type": "Integer"},
                {"name": "ActiveUsers", "type": "Integer"},
                {"name": "NewUsers", "type": "Integer"}
            ]
        }
        
        return {
            "model": {
                "name": "AgroADB Analytics Model",
                "tables": [
                    investigations_table,
                    users_table,
                    metrics_table
                ]
            },
            "measures": self._get_powerbi_measures(),
            "sample_data": {
                "investigations": summary.get("overview", {}).get("investigations", {}),
                "users": summary.get("overview", {}).get("users", {})
            }
        }
    
    def _get_powerbi_measures(self) -> List[Dict[str, str]]:
        """Medidas DAX sugeridas para Power BI"""
        return [
            {
                "name": "Total Investigations",
                "dax": "COUNTROWS(Investigations)"
            },
            {
                "name": "Completion Rate",
                "dax": """
                    DIVIDE(
                        CALCULATE(COUNTROWS(Investigations), Investigations[Status] = "completed"),
                        COUNTROWS(Investigations),
                        0
                    ) * 100
                """
            },
            {
                "name": "Avg Completion Time",
                "dax": "AVERAGE(Investigations[DurationHours])"
            },
            {
                "name": "Active Users",
                "dax": "CALCULATE(COUNTROWS(Users), Users[IsActive] = TRUE())"
            },
            {
                "name": "MRR",
                "dax": "CALCULATE(COUNTROWS(Users), Users[IsActive] = TRUE()) * 299.90"
            },
            {
                "name": "ARR",
                "dax": "[MRR] * 12"
            }
        ]
    
    def get_dashboard_template(self) -> Dict[str, Any]:
        """Template de dashboard para Power BI"""
        return {
            "name": "AgroADB Executive Dashboard",
            "pages": [
                {
                    "name": "Overview",
                    "visuals": [
                        {
                            "type": "Card",
                            "measure": "Total Investigations",
                            "position": {"x": 0, "y": 0, "width": 3, "height": 2}
                        },
                        {
                            "type": "Card",
                            "measure": "Active Users",
                            "position": {"x": 3, "y": 0, "width": 3, "height": 2}
                        },
                        {
                            "type": "Card",
                            "measure": "Completion Rate",
                            "format": "0.00%",
                            "position": {"x": 6, "y": 0, "width": 3, "height": 2}
                        },
                        {
                            "type": "Line Chart",
                            "x_axis": "DailyMetrics[Date]",
                            "y_axis": "[Total Investigations]",
                            "position": {"x": 0, "y": 2, "width": 9, "height": 4}
                        },
                        {
                            "type": "Pie Chart",
                            "legend": "Investigations[Status]",
                            "values": "[Total Investigations]",
                            "position": {"x": 9, "y": 2, "width": 3, "height": 4}
                        }
                    ]
                },
                {
                    "name": "Financial",
                    "visuals": [
                        {
                            "type": "Card",
                            "measure": "MRR",
                            "format": "R$ #,##0.00"
                        },
                        {
                            "type": "Card",
                            "measure": "ARR",
                            "format": "R$ #,##0.00"
                        }
                    ]
                }
            ]
        }


class TableauConnector:
    """
    Conector para Tableau
    
    Tableau pode consumir dados via:
    1. Direct connection ao PostgreSQL
    2. Hyper extracts
    3. Web Data Connector (API REST)
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
        self.aggregator = AnalyticsAggregator(db)
    
    def get_connection_config(self) -> Dict[str, Any]:
        """
        Configuração para conectar Tableau ao PostgreSQL
        
        No Tableau Desktop:
        Connect > To a Server > PostgreSQL
        """
        return {
            "type": "postgres",
            "server": "localhost",  # Seu servidor
            "port": 5432,
            "database": "agroadb",
            "authentication": "username_password",
            "username": "seu_usuario",
            "password": "sua_senha",
            "ssl": {
                "mode": "require"
            },
            "initial_sql": None
        }
    
    def export_for_tableau(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Exporta dados em formato Tableau Data Extract (TDE/Hyper)
        
        Retorna especificação da estrutura
        """
        summary = self.aggregator.generate_executive_summary(start_date, end_date)
        
        return {
            "datasource": {
                "name": "AgroADB Analytics",
                "version": "10.5",
                "connection": {
                    "class": "postgres",
                    "dbname": "agroadb",
                    "schema": "public"
                },
                "tables": [
                    {
                        "name": "investigations",
                        "columns": [
                            {"name": "id", "datatype": "integer", "role": "dimension"},
                            {"name": "user_id", "datatype": "integer", "role": "dimension"},
                            {"name": "status", "datatype": "string", "role": "dimension"},
                            {"name": "created_at", "datatype": "datetime", "role": "dimension"},
                            {"name": "updated_at", "datatype": "datetime", "role": "dimension"}
                        ]
                    },
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "datatype": "integer", "role": "dimension"},
                            {"name": "username", "datatype": "string", "role": "dimension"},
                            {"name": "email", "datatype": "string", "role": "dimension"},
                            {"name": "is_active", "datatype": "boolean", "role": "dimension"},
                            {"name": "created_at", "datatype": "datetime", "role": "dimension"}
                        ]
                    }
                ],
                "relationships": [
                    {
                        "left_table": "investigations",
                        "right_table": "users",
                        "left_key": "user_id",
                        "right_key": "id",
                        "type": "many-to-one"
                    }
                ]
            },
            "calculated_fields": self._get_tableau_calculated_fields(),
            "sample_data": summary
        }
    
    def _get_tableau_calculated_fields(self) -> List[Dict[str, str]]:
        """Campos calculados sugeridos para Tableau"""
        return [
            {
                "name": "Is Completed",
                "formula": '[Status] = "completed"'
            },
            {
                "name": "Completion Rate",
                "formula": 'SUM([Is Completed]) / COUNT([ID])'
            },
            {
                "name": "Duration Days",
                "formula": 'DATEDIFF("day", [Created At], [Updated At])'
            },
            {
                "name": "Month Created",
                "formula": 'DATETRUNC("month", [Created At])'
            },
            {
                "name": "Year Created",
                "formula": 'YEAR([Created At])'
            }
        ]
    
    def get_workbook_template(self) -> Dict[str, Any]:
        """Template de workbook para Tableau"""
        return {
            "name": "AgroADB Analytics Workbook",
            "worksheets": [
                {
                    "name": "KPIs",
                    "type": "dashboard",
                    "components": [
                        {"type": "text", "content": "Total Investigations", "measure": "COUNT([ID])"},
                        {"type": "text", "content": "Active Users", "measure": "COUNTD([User ID])"},
                        {"type": "text", "content": "Completion Rate", "measure": "[Completion Rate]"}
                    ]
                },
                {
                    "name": "Trend Analysis",
                    "type": "line_chart",
                    "columns": "[Month Created]",
                    "rows": "COUNT([ID])",
                    "color": "[Status]"
                },
                {
                    "name": "User Activity",
                    "type": "bar_chart",
                    "columns": "COUNT([ID])",
                    "rows": "[Username]",
                    "sort": "descending",
                    "limit": 10
                },
                {
                    "name": "Geographic Distribution",
                    "type": "map",
                    "location": "[State]",
                    "size": "COUNT([Properties])"
                }
            ]
        }


class UniversalBIAdapter:
    """
    Adaptador universal para qualquer ferramenta de BI
    
    Fornece APIs RESTful padronizadas que podem ser consumidas por qualquer BI tool
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator(db)
        self.aggregator = AnalyticsAggregator(db)
    
    def get_dataset_catalog(self) -> List[DatasetSchema]:
        """
        Retorna catálogo de datasets disponíveis
        
        Qualquer BI tool pode consumir esta lista para descobrir dados disponíveis
        """
        return [
            DatasetSchema(
                name="investigations",
                description="Todas as investigações criadas no sistema",
                fields=[
                    {"name": "id", "type": "integer", "description": "ID único"},
                    {"name": "user_id", "type": "integer", "description": "ID do usuário"},
                    {"name": "status", "type": "string", "description": "Status da investigação"},
                    {"name": "created_at", "type": "datetime", "description": "Data de criação"},
                    {"name": "updated_at", "type": "datetime", "description": "Data de atualização"}
                ]
            ),
            DatasetSchema(
                name="users",
                description="Usuários da plataforma",
                fields=[
                    {"name": "id", "type": "integer", "description": "ID único"},
                    {"name": "username", "type": "string", "description": "Nome de usuário"},
                    {"name": "email", "type": "string", "description": "Email"},
                    {"name": "is_active", "type": "boolean", "description": "Está ativo?"},
                    {"name": "created_at", "type": "datetime", "description": "Data de criação"}
                ]
            ),
            DatasetSchema(
                name="metrics_overview",
                description="Métricas gerais agregadas",
                fields=[
                    {"name": "total_users", "type": "integer"},
                    {"name": "active_users", "type": "integer"},
                    {"name": "total_investigations", "type": "integer"},
                    {"name": "completion_rate", "type": "decimal"}
                ]
            ),
            DatasetSchema(
                name="daily_activity",
                description="Atividade diária (investigações criadas por dia)",
                fields=[
                    {"name": "date", "type": "date"},
                    {"name": "investigations_count", "type": "integer"}
                ]
            )
        ]
    
    def get_dataset_data(
        self,
        dataset_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retorna dados de um dataset específico
        
        Implementa paginação e filtros por data
        """
        if dataset_name == "metrics_overview":
            overview = self.calculator.get_overview_metrics(start_date, end_date)
            return {
                "dataset": dataset_name,
                "data": [overview],
                "metadata": {
                    "total_records": 1,
                    "returned_records": 1
                }
            }
        
        elif dataset_name == "daily_activity":
            usage = self.calculator.get_usage_metrics(start_date, end_date)
            return {
                "dataset": dataset_name,
                "data": usage.get("daily_activity", []),
                "metadata": {
                    "total_records": len(usage.get("daily_activity", [])),
                    "returned_records": len(usage.get("daily_activity", []))
                }
            }
        
        # Para outros datasets, retornar estrutura vazia
        return {
            "dataset": dataset_name,
            "data": [],
            "metadata": {
                "total_records": 0,
                "returned_records": 0,
                "note": "Direct database connection recommended for raw tables"
            }
        }
    
    def get_odata_metadata(self) -> Dict[str, Any]:
        """
        Retorna metadata no formato OData
        
        OData é um protocolo padrão suportado por muitas ferramentas de BI
        """
        return {
            "$schema": "http://docs.oasis-open.org/odata/odata-json-format/v4.01",
            "version": "4.0",
            "entities": [
                {
                    "name": "Investigations",
                    "key": "ID",
                    "properties": [
                        {"name": "ID", "type": "Edm.Int32"},
                        {"name": "UserID", "type": "Edm.Int32"},
                        {"name": "Status", "type": "Edm.String"},
                        {"name": "CreatedAt", "type": "Edm.DateTimeOffset"},
                        {"name": "UpdatedAt", "type": "Edm.DateTimeOffset"}
                    ]
                },
                {
                    "name": "Users",
                    "key": "ID",
                    "properties": [
                        {"name": "ID", "type": "Edm.Int32"},
                        {"name": "Username", "type": "Edm.String"},
                        {"name": "Email", "type": "Edm.String"},
                        {"name": "IsActive", "type": "Edm.Boolean"},
                        {"name": "CreatedAt", "type": "Edm.DateTimeOffset"}
                    ]
                }
            ]
        }
