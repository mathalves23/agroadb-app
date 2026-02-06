import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface Investigation {
  id: number;
  target_name: string;
  target_cpf_cnpj: string;
  target_description?: string;
  status: string;
  priority: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  properties_found: number;
  lease_contracts_found: number;
  companies_found: number;
}

interface Property {
  id: number;
  property_name: string;
  car_number?: string;
  ccir_number?: string;
  matricula?: string;
  area_hectares?: number;
  state: string;
  city: string;
  owner_name?: string;
  owner_cpf_cnpj?: string;
}

interface Company {
  id: number;
  cnpj: string;
  corporate_name: string;
  trade_name?: string;
  status: string;
  opening_date?: string;
  state: string;
  city: string;
  main_activity?: string;
}

interface LeaseContract {
  id: number;
  lessor_name: string;
  lessee_name: string;
  property_description: string;
  area_leased?: number;
  value?: number;
  start_date?: string;
  end_date?: string;
}

export class PDFExportService {
  private static readonly PRIMARY_COLOR = [99, 102, 241]; // Indigo-600
  private static readonly SECONDARY_COLOR = [16, 185, 129]; // Emerald-600
  private static readonly TEXT_COLOR = [17, 24, 39]; // Gray-900

  static async exportInvestigation(
    investigation: Investigation,
    properties: Property[],
    companies: Company[],
    leaseContracts: LeaseContract[]
  ): Promise<void> {
    const doc = new jsPDF();
    let currentY = 20;

    // Configurações
    doc.setFont('helvetica');

    // ==================== CAPA ====================
    this.addCover(doc, investigation);
    doc.addPage();
    currentY = 20;

    // ==================== ÍNDICE ====================
    this.addIndex(doc);
    doc.addPage();
    currentY = 20;

    // ==================== RESUMO DA INVESTIGAÇÃO ====================
    currentY = this.addSection(doc, currentY, 'RESUMO DA INVESTIGAÇÃO');
    currentY = this.addInvestigationSummary(doc, currentY, investigation);

    // ==================== PROPRIEDADES ====================
    if (properties.length > 0) {
      if (currentY > 200) {
        doc.addPage();
        currentY = 20;
      }
      currentY = this.addSection(doc, currentY, 'PROPRIEDADES ENCONTRADAS');
      currentY = this.addPropertiesTable(doc, currentY, properties);
    }

    // ==================== EMPRESAS ====================
    if (companies.length > 0) {
      if (currentY > 200) {
        doc.addPage();
        currentY = 20;
      }
      currentY = this.addSection(doc, currentY, 'EMPRESAS VINCULADAS');
      currentY = this.addCompaniesTable(doc, currentY, companies);
    }

    // ==================== CONTRATOS ====================
    if (leaseContracts.length > 0) {
      if (currentY > 200) {
        doc.addPage();
        currentY = 20;
      }
      currentY = this.addSection(doc, currentY, 'CONTRATOS DE ARRENDAMENTO');
      currentY = this.addLeaseContractsTable(doc, currentY, leaseContracts);
    }

    // ==================== RODAPÉ EM TODAS AS PÁGINAS ====================
    const pageCount = doc.internal.pages.length - 1;
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      this.addFooter(doc, i, pageCount);
    }

    // ==================== SALVAR ====================
    const filename = `Investigacao_${investigation.target_name.replace(/[^a-z0-9]/gi, '_')}_${format(new Date(), 'yyyyMMdd')}.pdf`;
    doc.save(filename);
  }

  private static addCover(doc: jsPDF, investigation: Investigation): void {
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    // Background gradient (simulado)
    doc.setFillColor(99, 102, 241);
    doc.rect(0, 0, pageWidth, 80, 'F');

    // Logo/Title
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(32);
    doc.setFont('helvetica', 'bold');
    doc.text('AgroADB', pageWidth / 2, 35, { align: 'center' });
    
    doc.setFontSize(14);
    doc.setFont('helvetica', 'normal');
    doc.text('Intelligence Platform', pageWidth / 2, 50, { align: 'center' });

    // Título do relatório
    doc.setTextColor(17, 24, 39);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('RELATÓRIO DE INVESTIGAÇÃO', pageWidth / 2, 110, { align: 'center' });

    // Nome do alvo
    doc.setFontSize(18);
    doc.setFont('helvetica', 'normal');
    doc.text(investigation.target_name, pageWidth / 2, 130, { align: 'center' });

    // CPF/CNPJ
    doc.setFontSize(12);
    doc.setTextColor(107, 114, 128);
    doc.text(`CPF/CNPJ: ${investigation.target_cpf_cnpj}`, pageWidth / 2, 145, { align: 'center' });

    // Status
    doc.setFontSize(14);
    const statusText = this.getStatusLabel(investigation.status);
    const statusColor = this.getStatusColor(investigation.status);
    doc.setTextColor(...statusColor);
    doc.text(`Status: ${statusText}`, pageWidth / 2, 165, { align: 'center' });

    // Data de geração
    doc.setFontSize(10);
    doc.setTextColor(107, 114, 128);
    doc.text(
      `Gerado em ${format(new Date(), "dd 'de' MMMM 'de' yyyy 'às' HH:mm", { locale: ptBR })}`,
      pageWidth / 2,
      pageHeight - 30,
      { align: 'center' }
    );

    // Marca d'água
    doc.setFontSize(8);
    doc.text('Documento Confidencial', pageWidth / 2, pageHeight - 20, { align: 'center' });
  }

  private static addIndex(doc: jsPDF): void {
    const pageWidth = doc.internal.pageSize.getWidth();
    
    doc.setTextColor(...this.TEXT_COLOR);
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('ÍNDICE', pageWidth / 2, 30, { align: 'center' });

    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    let y = 50;
    const sections = [
      '1. Resumo da Investigação',
      '2. Propriedades Encontradas',
      '3. Empresas Vinculadas',
      '4. Contratos de Arrendamento',
      '5. Análise e Conclusões'
    ];

    sections.forEach((section) => {
      doc.text(section, 30, y);
      y += 15;
    });
  }

  private static addSection(doc: jsPDF, y: number, title: string): number {
    doc.setFillColor(...this.PRIMARY_COLOR);
    doc.rect(15, y, doc.internal.pageSize.getWidth() - 30, 10, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text(title, 20, y + 7);
    
    return y + 20;
  }

  private static addInvestigationSummary(doc: jsPDF, y: number, investigation: Investigation): number {
    doc.setTextColor(...this.TEXT_COLOR);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');

    const data = [
      ['Alvo', investigation.target_name],
      ['CPF/CNPJ', investigation.target_cpf_cnpj],
      ['Status', this.getStatusLabel(investigation.status)],
      ['Prioridade', this.getPriorityLabel(investigation.priority)],
      ['Criado em', format(new Date(investigation.created_at), 'dd/MM/yyyy HH:mm', { locale: ptBR })],
      ['Atualizado em', format(new Date(investigation.updated_at), 'dd/MM/yyyy HH:mm', { locale: ptBR })],
      ['Propriedades', String(investigation.properties_found)],
      ['Empresas', String(investigation.companies_found)],
      ['Contratos', String(investigation.lease_contracts_found)]
    ];

    if (investigation.target_description) {
      data.push(['Descrição', investigation.target_description]);
    }

    autoTable(doc, {
      startY: y,
      head: [],
      body: data,
      theme: 'plain',
      styles: { fontSize: 10, cellPadding: 3 },
      columnStyles: {
        0: { fontStyle: 'bold', cellWidth: 40 },
        1: { cellWidth: 'auto' }
      }
    });

    return (doc as any).lastAutoTable.finalY + 10;
  }

  private static addPropertiesTable(doc: jsPDF, y: number, properties: Property[]): number {
    const tableData = properties.map((prop) => [
      prop.property_name || '-',
      prop.car_number || '-',
      prop.area_hectares ? `${prop.area_hectares} ha` : '-',
      `${prop.city}/${prop.state}`,
      prop.owner_name || '-'
    ]);

    autoTable(doc, {
      startY: y,
      head: [['Propriedade', 'CAR', 'Área', 'Localização', 'Proprietário']],
      body: tableData,
      theme: 'striped',
      headStyles: {
        fillColor: this.PRIMARY_COLOR,
        textColor: [255, 255, 255],
        fontSize: 10,
        fontStyle: 'bold'
      },
      styles: { fontSize: 9, cellPadding: 3 },
      columnStyles: {
        0: { cellWidth: 40 },
        1: { cellWidth: 35 },
        2: { cellWidth: 25 },
        3: { cellWidth: 40 },
        4: { cellWidth: 40 }
      }
    });

    return (doc as any).lastAutoTable.finalY + 10;
  }

  private static addCompaniesTable(doc: jsPDF, y: number, companies: Company[]): number {
    const tableData = companies.map((comp) => [
      comp.corporate_name,
      comp.cnpj,
      comp.status || '-',
      `${comp.city}/${comp.state}`,
      comp.main_activity || '-'
    ]);

    autoTable(doc, {
      startY: y,
      head: [['Razão Social', 'CNPJ', 'Status', 'Localização', 'Atividade']],
      body: tableData,
      theme: 'striped',
      headStyles: {
        fillColor: this.PRIMARY_COLOR,
        textColor: [255, 255, 255],
        fontSize: 10,
        fontStyle: 'bold'
      },
      styles: { fontSize: 9, cellPadding: 3 }
    });

    return (doc as any).lastAutoTable.finalY + 10;
  }

  private static addLeaseContractsTable(doc: jsPDF, y: number, contracts: LeaseContract[]): number {
    const tableData = contracts.map((contract) => [
      contract.lessor_name,
      contract.lessee_name,
      contract.property_description || '-',
      contract.area_leased ? `${contract.area_leased} ha` : '-',
      contract.value ? `R$ ${contract.value.toLocaleString('pt-BR')}` : '-',
      contract.start_date ? format(new Date(contract.start_date), 'MM/yyyy') : '-'
    ]);

    autoTable(doc, {
      startY: y,
      head: [['Locador', 'Locatário', 'Propriedade', 'Área', 'Valor', 'Início']],
      body: tableData,
      theme: 'striped',
      headStyles: {
        fillColor: this.PRIMARY_COLOR,
        textColor: [255, 255, 255],
        fontSize: 10,
        fontStyle: 'bold'
      },
      styles: { fontSize: 9, cellPadding: 3 }
    });

    return (doc as any).lastAutoTable.finalY + 10;
  }

  private static addFooter(doc: jsPDF, pageNumber: number, totalPages: number): void {
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    // Linha separadora
    doc.setDrawColor(229, 231, 235);
    doc.setLineWidth(0.5);
    doc.line(15, pageHeight - 20, pageWidth - 15, pageHeight - 20);

    // Texto do rodapé
    doc.setTextColor(107, 114, 128);
    doc.setFontSize(8);
    doc.text('AgroADB Intelligence Platform', 15, pageHeight - 12);
    doc.text(`Página ${pageNumber} de ${totalPages}`, pageWidth - 15, pageHeight - 12, { align: 'right' });
    doc.text('Documento Confidencial', pageWidth / 2, pageHeight - 12, { align: 'center' });
  }

  private static getStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      PENDING: 'Pendente',
      IN_PROGRESS: 'Em Andamento',
      COMPLETED: 'Concluída',
      CANCELLED: 'Cancelada'
    };
    return labels[status] || status;
  }

  private static getStatusColor(status: string): [number, number, number] {
    const colors: Record<string, [number, number, number]> = {
      PENDING: [251, 191, 36],      // Amber
      IN_PROGRESS: [59, 130, 246],  // Blue
      COMPLETED: [16, 185, 129],    // Green
      CANCELLED: [239, 68, 68]      // Red
    };
    return colors[status] || [107, 114, 128]; // Gray default
  }

  private static getPriorityLabel(priority: number): string {
    const labels: Record<number, string> = {
      1: 'Baixa',
      2: 'Normal',
      3: 'Alta',
      4: 'Urgente'
    };
    return labels[priority] || 'Normal';
  }
}
