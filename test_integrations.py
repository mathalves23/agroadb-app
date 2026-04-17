"""
Script de teste para as novas integrações de Tribunais Estaduais e Birôs de Crédito
Execute: python test_integrations.py
"""
import asyncio
import os
from datetime import datetime


async def test_esaj():
    """Testa integração com e-SAJ"""
    print("\n" + "="*60)
    print("🏛️  TESTANDO e-SAJ (Tribunais Estaduais)")
    print("="*60)
    
    from backend.app.services.integrations.esaj_service import ESAJService
    
    cpf_teste = "12345678900"  # Substituir por CPF real para teste
    tribunal = "tjsp"
    
    print(f"\nBuscando processos no {tribunal.upper()}...")
    
    try:
        async with ESAJService() as service:
            # Processos de 1º Grau
            print("\n📋 1º Grau:")
            processos_1g = await service.consultar_processos_1g(cpf_teste, tribunal)
            print(f"   Total: {len(processos_1g)} processos")
            
            for i, proc in enumerate(processos_1g[:3], 1):
                print(f"\n   {i}. Processo: {proc.numero_processo}")
                print(f"      Classe: {proc.classe}")
                print(f"      Assunto: {proc.assunto}")
                print(f"      Vara: {proc.vara}")
                print(f"      Status: {proc.status}")
            
            # Processos de 2º Grau
            print("\n📋 2º Grau:")
            processos_2g = await service.consultar_processos_2g(cpf_teste, tribunal)
            print(f"   Total: {len(processos_2g)} processos")
            
            for i, proc in enumerate(processos_2g[:3], 1):
                print(f"\n   {i}. Processo: {proc.numero_processo}")
                print(f"      Classe: {proc.classe}")
                print(f"      Assunto: {proc.assunto}")
        
        print("\n✅ Teste e-SAJ concluído com sucesso!")
    
    except Exception as e:
        print(f"\n❌ Erro no teste e-SAJ: {e}")


async def test_projudi():
    """Testa integração com Projudi"""
    print("\n" + "="*60)
    print("🏛️  TESTANDO Projudi (Tribunais Estaduais)")
    print("="*60)
    
    from backend.app.services.integrations.projudi_service import ProjudiService
    
    cpf_teste = "12345678900"
    tribunal = "tjmt"
    
    print(f"\nBuscando processos no {tribunal.upper()}...")
    
    try:
        async with ProjudiService() as service:
            processos = await service.consultar_processos(cpf_teste, tribunal)
            print(f"Total: {len(processos)} processos")
            
            for i, proc in enumerate(processos[:3], 1):
                print(f"\n{i}. Processo: {proc.numero_processo}")
                print(f"   Tribunal: {proc.tribunal}")
                print(f"   Classe: {proc.classe}")
                print(f"   Comarca: {proc.comarca}")
                print(f"   Status: {proc.status}")
        
        print("\n✅ Teste Projudi concluído com sucesso!")
    
    except Exception as e:
        print(f"\n❌ Erro no teste Projudi: {e}")


async def test_pje():
    """Testa integração com PJe melhorada"""
    print("\n" + "="*60)
    print("🏛️  TESTANDO PJe (Justiça Federal)")
    print("="*60)
    
    from backend.app.services.integrations.pje import PJeIntegration
    
    cpf_teste = "12345678900"
    
    print(f"\nBuscando processos em todos os TRFs...")
    
    try:
        async with PJeIntegration() as service:
            resultados = await service.consultar_todos_tribunais(cpf_teste)
            
            print(f"\nResultados:")
            for tribunal, processos in resultados.items():
                print(f"\n{tribunal}: {len(processos)} processos")
                
                for i, proc in enumerate(processos[:2], 1):
                    print(f"  {i}. {proc.numero_processo}")
                    print(f"     Classe: {proc.classe}")
                    print(f"     Órgão: {proc.orgao_julgador}")
        
        print("\n✅ Teste PJe concluído com sucesso!")
    
    except Exception as e:
        print(f"\n❌ Erro no teste PJe: {e}")


async def test_serasa():
    """Testa integração com Serasa"""
    print("\n" + "="*60)
    print("💳 TESTANDO Serasa Experian")
    print("="*60)
    
    from backend.app.services.integrations.serasa_service import SerasaService
    
    cpf_teste = "12345678900"
    
    # Verificar se credenciais estão configuradas
    if not os.getenv("SERASA_CLIENT_ID"):
        print("\n⚠️  AVISO: Credenciais Serasa não configuradas")
        print("   Configure SERASA_CLIENT_ID e SERASA_CLIENT_SECRET no .env")
        print("   Este é um teste de demonstração apenas.")
        return
    
    print(f"\nConsultando Serasa...")
    
    try:
        async with SerasaService() as service:
            # Score
            print("\n📊 Score:")
            score = await service.consultar_score(cpf_teste)
            
            if score:
                print(f"   Score: {score.score}/1000")
                print(f"   Faixa: {score.faixa}")
                print(f"   Probabilidade Inadimplência: {score.probabilidade_inadimplencia:.2%}")
            else:
                print("   Não disponível")
            
            # Restrições
            print("\n⚠️  Restrições:")
            restricoes = await service.consultar_restricoes(cpf_teste)
            print(f"   Total: {len(restricoes)} restrições")
            
            for i, rest in enumerate(restricoes[:3], 1):
                print(f"\n   {i}. Tipo: {rest.tipo}")
                print(f"      Credor: {rest.credor}")
                print(f"      Valor: R$ {rest.valor:,.2f}")
                print(f"      Data: {rest.data_ocorrencia.strftime('%d/%m/%Y')}")
            
            # Consultas recentes
            print("\n🔍 Consultas Recentes:")
            consultas = await service.consultar_consultas_recentes(cpf_teste)
            print(f"   Total: {len(consultas)} consultas nos últimos 90 dias")
            
            for i, cons in enumerate(consultas[:5], 1):
                print(f"   {i}. {cons.empresa} - {cons.data.strftime('%d/%m/%Y')}")
        
        print("\n✅ Teste Serasa concluído com sucesso!")
    
    except Exception as e:
        print(f"\n❌ Erro no teste Serasa: {e}")


async def test_boavista():
    """Testa integração com Boa Vista"""
    print("\n" + "="*60)
    print("💳 TESTANDO Boa Vista SCPC")
    print("="*60)
    
    from backend.app.services.integrations.boavista_service import BoaVistaService
    
    cpf_teste = "12345678900"
    
    # Verificar se credenciais estão configuradas
    if not os.getenv("BOAVISTA_CLIENT_ID"):
        print("\n⚠️  AVISO: Credenciais Boa Vista não configuradas")
        print("   Configure BOAVISTA_CLIENT_ID e BOAVISTA_CLIENT_SECRET no .env")
        print("   Este é um teste de demonstração apenas.")
        return
    
    print(f"\nConsultando Boa Vista...")
    
    try:
        async with BoaVistaService() as service:
            # Score
            print("\n📊 Score:")
            score = await service.consultar_score(cpf_teste)
            
            if score:
                print(f"   Score: {score.score}/1000")
                print(f"   Classificação: {score.classificacao}")
            else:
                print("   Não disponível")
            
            # Relatório completo
            print("\n📋 Relatório Completo:")
            report = await service.get_full_report(cpf_teste)
            
            if report:
                print(f"   Nome: {report.nome}")
                print(f"   Restrições: {len(report.restricoes_financeiras)}")
                print(f"   Protestos: {len(report.protestos)}")
                print(f"   Cheques sem Fundo: {len(report.cheques_sem_fundo)}")
                print(f"   Ações Judiciais: {len(report.acoes_judiciais)}")
                print(f"   Consultas Recentes: {report.consultas_recentes}")
                
                # Detalhar protestos
                if report.protestos:
                    print("\n   📜 Protestos:")
                    for i, prot in enumerate(report.protestos[:3], 1):
                        print(f"      {i}. Valor: R$ {prot.valor:,.2f}")
                        print(f"         Cartório: {prot.cartorio}")
                        print(f"         Data: {prot.data_protesto.strftime('%d/%m/%Y')}")
            else:
                print("   Não disponível")
        
        print("\n✅ Teste Boa Vista concluído com sucesso!")
    
    except Exception as e:
        print(f"\n❌ Erro no teste Boa Vista: {e}")


async def test_all():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🚀 INICIANDO TESTES DE INTEGRAÇÕES")
    print("="*60)
    print(f"\nData/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Testes de Tribunais Estaduais
    await test_esaj()
    await test_projudi()
    await test_pje()
    
    # Testes de Birôs de Crédito
    await test_serasa()
    await test_boavista()
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("="*60)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║  TESTE DE INTEGRAÇÕES - AgroADB                           ║
    ║  Tribunais Estaduais e Birôs de Crédito                   ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar testes
    asyncio.run(test_all())
