import * as XLSX from 'xlsx';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { saveAs } from 'file-saver';

interface Investigation {
  id: number;
  target_name: string;
  target_cpf_cnpj: string;
  target_description?: string;
  status: string;
  priority: number;
  created_at: string;
  properties_found: number;
  companies_found: number;
  lease_contracts_found: number;
}

interface Property {
  property_name: string;
  car_number?: string;
  ccir_number?: string;
  matricula?: string;
  area_hectares?: number;
  state: string;
  city: string;
  owner_name?: string;
  owner_cpf_cnpj?: string;
  data_source?: string;
}

interface Company {
  cnpj: string;
  corporate_name: string;
  trade_name?: string;
  status: string;
  opening_date?: string;
  state: string;
  city: string;
  main_activity?: string;
  legal_nature?: string;
}

interface LeaseContract {
  lessor_name: string;
  lessee_name: string;
  property_description: string;
  area_leased?: number;
  value?: number;
  start_date?: string;
  end_date?: string;
  payment_terms?: string;
}

export class ExcelExportService {
  static exportInvestigation(
    investigation: Investigation,
    properties: Property[],
    companies: Company[],
    leaseContracts: LeaseContract[]
  ): void {
    const workbook = XLSX.utils.book_new();

    // ==================== ABA 1: RESUMO ====================
    const summaryData = [
      ['RESUMO DA INVESTIGAÇÃO'],
      [],
      ['Campo', 'Valor'],
      ['ID', investigation.id],
      ['Alvo', investigation.target_name],
      ['CPF/CNPJ', investigation.target_cpf_cnpj],
      ['Descrição', investigation.target_description || '-'],
      ['Status', this.getStatusLabel(investigation.status)],
      ['Prioridade', this.getPriorityLabel(investigation.priority)],
      ['Data Criação', format(new Date(investigation.created_at), 'dd/MM/yyyy HH:mm')],
      [],
      ['ESTATÍSTICAS'],
      [],
      ['Total de Propriedades', investigation.properties_found],
      ['Total de Empresas', investigation.companies_found],
      ['Total de Contratos', investigation.lease_contracts_found],
      [],
      ['Relatório gerado em', format(new Date(), "dd/MM/yyyy 'às' HH:mm")]
    ];

    const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
    
    // Larguras das colunas
    summarySheet['!cols'] = [{ wch: 25 }, { wch: 50 }];
    
    // Estilos (se suportado)
    XLSX.utils.book_append_sheet(workbook, summarySheet, 'Resumo');

    // ==================== ABA 2: PROPRIEDADES ====================
    if (properties.length > 0) {
      const propHeaders = [
        'Nome da Propriedade',
        'CAR',
        'CCIR',
        'Matrícula',
        'Área (ha)',
        'Estado',
        'Cidade',
        'Proprietário',
        'CPF/CNPJ',
        'Fonte'
      ];

      const propData = properties.map(prop => [
        prop.property_name || '-',
        prop.car_number || '-',
        prop.ccir_number || '-',
        prop.matricula || '-',
        prop.area_hectares || '-',
        prop.state,
        prop.city,
        prop.owner_name || '-',
        prop.owner_cpf_cnpj || '-',
        prop.data_source || '-'
      ]);

      const propSheet = XLSX.utils.aoa_to_sheet([propHeaders, ...propData]);
      propSheet['!cols'] = [
        { wch: 30 }, { wch: 25 }, { wch: 15 }, { wch: 12 },
        { wch: 10 }, { wch: 8 }, { wch: 20 }, { wch: 30 },
        { wch: 18 }, { wch: 15 }
      ];
      
      // Auto-filtro
      propSheet['!autofilter'] = { ref: `A1:J${propData.length + 1}` };
      
      XLSX.utils.book_append_sheet(workbook, propSheet, 'Propriedades');
    }

    // ==================== ABA 3: EMPRESAS ====================
    if (companies.length > 0) {
      const compHeaders = [
        'Razão Social',
        'Nome Fantasia',
        'CNPJ',
        'Status',
        'Data Abertura',
        'Estado',
        'Cidade',
        'Atividade Principal',
        'Natureza Jurídica'
      ];

      const compData = companies.map(comp => [
        comp.corporate_name,
        comp.trade_name || '-',
        comp.cnpj,
        comp.status || '-',
        comp.opening_date ? format(new Date(comp.opening_date), 'dd/MM/yyyy') : '-',
        comp.state,
        comp.city,
        comp.main_activity || '-',
        comp.legal_nature || '-'
      ]);

      const compSheet = XLSX.utils.aoa_to_sheet([compHeaders, ...compData]);
      compSheet['!cols'] = [
        { wch: 40 }, { wch: 30 }, { wch: 18 }, { wch: 12 },
        { wch: 15 }, { wch: 8 }, { wch: 20 }, { wch: 40 },
        { wch: 25 }
      ];
      
      compSheet['!autofilter'] = { ref: `A1:I${compData.length + 1}` };
      
      XLSX.utils.book_append_sheet(workbook, compSheet, 'Empresas');
    }

    // ==================== ABA 4: CONTRATOS ====================
    if (leaseContracts.length > 0) {
      const contractHeaders = [
        'Locador',
        'Locatário',
        'Propriedade',
        'Área Arrendada (ha)',
        'Valor (R$)',
        'Data Início',
        'Data Fim',
        'Condições Pagamento'
      ];

      const contractData = leaseContracts.map(contract => [
        contract.lessor_name,
        contract.lessee_name,
        contract.property_description || '-',
        contract.area_leased || '-',
        contract.value || '-',
        contract.start_date ? format(new Date(contract.start_date), 'dd/MM/yyyy') : '-',
        contract.end_date ? format(new Date(contract.end_date), 'dd/MM/yyyy') : '-',
        contract.payment_terms || '-'
      ]);

      const contractSheet = XLSX.utils.aoa_to_sheet([contractHeaders, ...contractData]);
      contractSheet['!cols'] = [
        { wch: 30 }, { wch: 30 }, { wch: 35 }, { wch: 15 },
        { wch: 15 }, { wch: 12 }, { wch: 12 }, { wch: 30 }
      ];
      
      contractSheet['!autofilter'] = { ref: `A1:H${contractData.length + 1}` };
      
      XLSX.utils.book_append_sheet(workbook, contractSheet, 'Contratos');
    }

    // ==================== SALVAR ARQUIVO ====================
    const filename = `Investigacao_${investigation.target_name.replace(/[^a-z0-9]/gi, '_')}_${format(new Date(), 'yyyyMMdd')}.xlsx`;
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const data = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(data, filename);
  }

  static exportCSV(
    investigation: Investigation,
    properties: Property[],
    companies: Company[],
    leaseContracts: LeaseContract[]
  ): void {
    // Export simples em CSV (primeira aba apenas)
    const data = [
      ['INVESTIGAÇÃO'],
      ['Alvo', investigation.target_name],
      ['CPF/CNPJ', investigation.target_cpf_cnpj],
      ['Status', this.getStatusLabel(investigation.status)],
      [],
      ['PROPRIEDADES'],
      ['Nome', 'CAR', 'Área', 'Cidade', 'Estado'],
      ...properties.map(p => [
        p.property_name || '-',
        p.car_number || '-',
        p.area_hectares || '-',
        p.city,
        p.state
      ])
    ];

    const worksheet = XLSX.utils.aoa_to_sheet(data);
    const csv = XLSX.utils.sheet_to_csv(worksheet);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const filename = `Investigacao_${investigation.target_name.replace(/[^a-z0-9]/gi, '_')}_${format(new Date(), 'yyyyMMdd')}.csv`;
    saveAs(blob, filename);
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
