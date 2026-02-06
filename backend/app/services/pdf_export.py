"""
PDF Export Service for Investigations
Generates professional PDF reports using ReportLab
"""
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

logger = logging.getLogger(__name__)


class NumberedCanvas(canvas.Canvas):
    """Canvas with page numbering and headers/footers"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Draw page number and footer"""
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        
        # Page number
        page_num = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[0] - 2 * cm, 1.5 * cm, page_num)
        
        # Footer
        footer_text = f"AgroADB - Relatório de Investigação - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        self.drawString(2 * cm, 1.5 * cm, footer_text)
        
        # Header line (except first page)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#10b981"))
            self.setLineWidth(1)
            self.line(2 * cm, A4[1] - 2.5 * cm, A4[0] - 2 * cm, A4[1] - 2.5 * cm)


class PDFExportService:
    """Service for generating professional investigation PDF reports"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                textColor=colors.HexColor("#1f2937"),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # Subtitle style
        self.styles.add(
            ParagraphStyle(
                name="CustomSubtitle",
                parent=self.styles["Heading2"],
                fontSize=16,
                textColor=colors.HexColor("#10b981"),
                spaceAfter=12,
                spaceBefore=12,
                fontName="Helvetica-Bold",
            )
        )

        # Section style
        self.styles.add(
            ParagraphStyle(
                name="Section",
                parent=self.styles["Heading3"],
                fontSize=14,
                textColor=colors.HexColor("#374151"),
                spaceAfter=10,
                spaceBefore=10,
                fontName="Helvetica-Bold",
            )
        )

        # Info style
        self.styles.add(
            ParagraphStyle(
                name="InfoLabel",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#6b7280"),
                fontName="Helvetica-Bold",
            )
        )

        # Value style
        self.styles.add(
            ParagraphStyle(
                name="InfoValue",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#1f2937"),
            )
        )

    def generate_investigation_pdf(
        self,
        investigation: Dict[str, Any],
        properties: List[Dict[str, Any]],
        companies: List[Dict[str, Any]],
        legal_queries: List[Dict[str, Any]],
    ) -> io.BytesIO:
        """
        Generate a comprehensive PDF report for an investigation
        
        Args:
            investigation: Investigation data
            properties: List of properties found
            companies: List of companies found
            legal_queries: List of legal queries performed
            
        Returns:
            BytesIO object containing the PDF
        """
        buffer = io.BytesIO()
        
        # Create document with margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=3 * cm,
            bottomMargin=2.5 * cm,
        )

        # Build content
        story = []

        # Cover page
        story.extend(self._create_cover_page(investigation))
        story.append(PageBreak())

        # Table of contents
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(name='TOCHeading1', fontSize=14, leftIndent=0, spaceBefore=10, spaceAfter=2),
            ParagraphStyle(name='TOCHeading2', fontSize=12, leftIndent=20, spaceBefore=5, spaceAfter=2),
        ]
        story.append(Paragraph("Índice", self.styles["CustomSubtitle"]))
        story.append(toc)
        story.append(PageBreak())

        # Executive summary
        story.extend(self._create_executive_summary(investigation, properties, companies, legal_queries))
        story.append(PageBreak())

        # Investigation details
        story.extend(self._create_investigation_details(investigation))
        story.append(Spacer(1, 0.5 * cm))

        # Properties section
        if properties:
            story.extend(self._create_properties_section(properties))
            story.append(Spacer(1, 0.5 * cm))

        # Companies section
        if companies:
            story.extend(self._create_companies_section(companies))
            story.append(Spacer(1, 0.5 * cm))

        # Legal queries section
        if legal_queries:
            story.extend(self._create_legal_queries_section(legal_queries))
            story.append(Spacer(1, 0.5 * cm))

        # Charts and analysis
        if legal_queries:
            story.append(PageBreak())
            story.extend(self._create_charts_section(legal_queries))

        # Build PDF
        doc.multiBuild(story, canvasmaker=NumberedCanvas)
        
        buffer.seek(0)
        return buffer

    def _create_cover_page(self, investigation: Dict[str, Any]) -> List:
        """Create professional cover page"""
        elements = []

        # Logo (if exists)
        logo_path = Path(__file__).parent.parent / "static" / "logo.png"
        if logo_path.exists():
            try:
                logo = Image(str(logo_path), width=4 * cm, height=4 * cm)
                logo.hAlign = "CENTER"
                elements.append(logo)
                elements.append(Spacer(1, 1 * cm))
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")

        # Title
        elements.append(Spacer(1, 3 * cm))
        elements.append(
            Paragraph("RELATÓRIO DE INVESTIGAÇÃO", self.styles["CustomTitle"])
        )
        elements.append(Spacer(1, 0.5 * cm))

        # Investigation name
        target_name = investigation.get("target_name", "Sem nome")
        elements.append(
            Paragraph(
                f"<b>{target_name}</b>",
                ParagraphStyle(
                    name="CoverSubtitle",
                    fontSize=18,
                    textColor=colors.HexColor("#10b981"),
                    alignment=TA_CENTER,
                    spaceAfter=30,
                ),
            )
        )

        elements.append(Spacer(1, 2 * cm))

        # Key information box
        data = [
            ["CPF/CNPJ:", investigation.get("target_cpf_cnpj", "N/A")],
            ["Status:", investigation.get("status", "N/A").upper()],
            ["Criado em:", self._format_date(investigation.get("created_at"))],
            [
                "Atualizado em:",
                self._format_date(investigation.get("updated_at")),
            ],
        ]

        table = Table(data, colWidths=[5 * cm, 10 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#374151")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(table)

        elements.append(Spacer(1, 3 * cm))

        # Footer
        elements.append(
            Paragraph(
                "Sistema AgroADB - Inteligência e Análise de Dados Fundiários",
                ParagraphStyle(
                    name="CoverFooter",
                    fontSize=10,
                    textColor=colors.HexColor("#6b7280"),
                    alignment=TA_CENTER,
                ),
            )
        )

        return elements

    def _create_executive_summary(
        self,
        investigation: Dict[str, Any],
        properties: List[Dict[str, Any]],
        companies: List[Dict[str, Any]],
        legal_queries: List[Dict[str, Any]],
    ) -> List:
        """Create executive summary section"""
        elements = []

        elements.append(Paragraph("Resumo Executivo", self.styles["CustomSubtitle"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Statistics
        total_properties = len(properties)
        total_companies = len(companies)
        total_queries = len(legal_queries)
        total_results = sum(q.get("result_count", 0) for q in legal_queries)

        # Create statistics table
        stats_data = [
            ["Métrica", "Quantidade"],
            ["Propriedades Encontradas", str(total_properties)],
            ["Empresas Encontradas", str(total_companies)],
            ["Consultas Realizadas", str(total_queries)],
            ["Resultados Totais", str(total_results)],
        ]

        stats_table = Table(stats_data, colWidths=[10 * cm, 5 * cm])
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 1), (1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdf4")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5 * cm))

        # Description
        if investigation.get("target_description"):
            elements.append(Paragraph("Descrição:", self.styles["Section"]))
            desc_text = investigation["target_description"].replace("\n", "<br/>")
            elements.append(
                Paragraph(desc_text, self.styles["InfoValue"])
            )

        return elements

    def _create_investigation_details(self, investigation: Dict[str, Any]) -> List:
        """Create investigation details section"""
        elements = []

        elements.append(Paragraph("Detalhes da Investigação", self.styles["CustomSubtitle"]))
        elements.append(Spacer(1, 0.3 * cm))

        # Basic information
        data = [
            ["Campo", "Valor"],
            ["Nome/Razão Social", investigation.get("target_name", "N/A")],
            ["CPF/CNPJ", investigation.get("target_cpf_cnpj", "N/A")],
            ["Status", investigation.get("status", "N/A").upper()],
            ["Data de Criação", self._format_date(investigation.get("created_at"))],
            ["Última Atualização", self._format_date(investigation.get("updated_at"))],
        ]

        table = Table(data, colWidths=[6 * cm, 11 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f3f4f6")),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        elements.append(table)

        return elements

    def _create_properties_section(self, properties: List[Dict[str, Any]]) -> List:
        """Create properties section"""
        elements = []

        elements.append(Paragraph(f"Propriedades Encontradas ({len(properties)})", self.styles["CustomSubtitle"]))
        elements.append(Spacer(1, 0.3 * cm))

        for idx, prop in enumerate(properties[:20], 1):  # Limit to first 20
            # Property header
            prop_title = f"{idx}. {prop.get('name', 'Propriedade sem nome')}"
            elements.append(Paragraph(prop_title, self.styles["Section"]))

            # Property details
            data = []
            if prop.get("area_ha"):
                data.append(["Área (ha)", f"{prop['area_ha']:,.2f}"])
            if prop.get("location"):
                data.append(["Localização", prop["location"]])
            if prop.get("source"):
                data.append(["Fonte", prop["source"]])
            if prop.get("registration_code"):
                data.append(["Código", prop["registration_code"]])

            if data:
                table = Table(data, colWidths=[5 * cm, 12 * cm])
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                elements.append(table)

            elements.append(Spacer(1, 0.3 * cm))

        if len(properties) > 20:
            elements.append(
                Paragraph(
                    f"<i>... e mais {len(properties) - 20} propriedades não exibidas neste relatório.</i>",
                    self.styles["InfoValue"],
                )
            )

        return elements

    def _create_companies_section(self, companies: List[Dict[str, Any]]) -> List:
        """Create companies section"""
        elements = []

        elements.append(Paragraph(f"Empresas Encontradas ({len(companies)})", self.styles["CustomSubtitle"]))
        elements.append(Spacer(1, 0.3 * cm))

        for idx, company in enumerate(companies[:20], 1):  # Limit to first 20
            # Company header
            company_title = f"{idx}. {company.get('name', 'Empresa sem nome')}"
            elements.append(Paragraph(company_title, self.styles["Section"]))

            # Company details
            data = []
            if company.get("cnpj"):
                data.append(["CNPJ", company["cnpj"]])
            if company.get("registration_status"):
                data.append(["Status", company["registration_status"]])
            if company.get("activity"):
                data.append(["Atividade", company["activity"]])
            if company.get("address"):
                data.append(["Endereço", company["address"]])

            if data:
                table = Table(data, colWidths=[5 * cm, 12 * cm])
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
                            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                elements.append(table)

            elements.append(Spacer(1, 0.3 * cm))

        if len(companies) > 20:
            elements.append(
                Paragraph(
                    f"<i>... e mais {len(companies) - 20} empresas não exibidas neste relatório.</i>",
                    self.styles["InfoValue"],
                )
            )

        return elements

    def _create_legal_queries_section(self, legal_queries: List[Dict[str, Any]]) -> List:
        """Create legal queries section"""
        elements = []

        elements.append(Paragraph(f"Consultas Legais Realizadas ({len(legal_queries)})", self.styles["CustomSubtitle"]))
        elements.append(Spacer(1, 0.3 * cm))

        # Group by provider
        providers: Dict[str, List[Dict[str, Any]]] = {}
        for query in legal_queries:
            provider = query.get("provider", "Desconhecido")
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(query)

        # Create table for each provider
        for provider, queries in providers.items():
            elements.append(Paragraph(provider, self.styles["Section"]))

            data = [["Tipo de Consulta", "Resultados", "Data"]]
            for query in queries[:10]:  # Limit to 10 per provider
                data.append(
                    [
                        query.get("query_type", "N/A"),
                        str(query.get("result_count", 0)),
                        self._format_datetime(query.get("created_at")),
                    ]
                )

            table = Table(data, colWidths=[8 * cm, 4 * cm, 5 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (1, 1), (1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 0.4 * cm))

        return elements

    def _create_charts_section(self, legal_queries: List[Dict[str, Any]]) -> List:
        """Create charts and visual analysis section"""
        elements = []

        elements.append(Paragraph("Análise Visual", self.styles["CustomSubtitle"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Chart 1: Distribution by provider (Pie Chart)
        elements.append(Paragraph("Distribuição por Fonte", self.styles["Section"]))
        elements.append(Spacer(1, 0.3 * cm))

        provider_counts: Dict[str, int] = {}
        for query in legal_queries:
            provider = query.get("provider", "Desconhecido")
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

        if provider_counts:
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = list(provider_counts.values())
            pie.labels = list(provider_counts.keys())
            pie.slices.strokeWidth = 0.5
            
            # Colors
            colors_list = [
                colors.HexColor("#10b981"),
                colors.HexColor("#3b82f6"),
                colors.HexColor("#f59e0b"),
                colors.HexColor("#ef4444"),
                colors.HexColor("#8b5cf6"),
                colors.HexColor("#ec4899"),
            ]
            for i, slice in enumerate(pie.slices):
                slice.fillColor = colors_list[i % len(colors_list)]

            drawing.add(pie)
            elements.append(drawing)
            elements.append(Spacer(1, 0.5 * cm))

        # Chart 2: Results by provider (Bar Chart)
        elements.append(Paragraph("Resultados por Fonte", self.styles["Section"]))
        elements.append(Spacer(1, 0.3 * cm))

        provider_results: Dict[str, int] = {}
        for query in legal_queries:
            provider = query.get("provider", "Desconhecido")
            provider_results[provider] = provider_results.get(provider, 0) + query.get("result_count", 0)

        if provider_results:
            drawing = Drawing(400, 200)
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 125
            bc.width = 300
            bc.data = [list(provider_results.values())]
            bc.categoryAxis.categoryNames = list(provider_results.keys())
            bc.categoryAxis.labels.boxAnchor = "ne"
            bc.categoryAxis.labels.dx = -8
            bc.categoryAxis.labels.dy = -2
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.fontSize = 8
            bc.valueAxis.valueMin = 0
            bc.bars[0].fillColor = colors.HexColor("#10b981")
            
            drawing.add(bc)
            elements.append(drawing)

        return elements

    def _format_date(self, date_str: Optional[str]) -> str:
        """Format date string to Brazilian format"""
        if not date_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return date_str

    def _format_datetime(self, date_str: Optional[str]) -> str:
        """Format datetime string to Brazilian format"""
        if not date_str:
            return "N/A"
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return date_str
