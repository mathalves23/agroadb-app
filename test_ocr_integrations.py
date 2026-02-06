"""
Script de Testes para OCR e Integrações Ambientais
Execute com: python test_ocr_integrations.py
"""
import asyncio
import sys
from pathlib import Path

# Adicionar path do backend ao PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / "backend"))


async def test_ocr():
    """Testa funcionalidades de OCR"""
    print("\n" + "="*60)
    print("🔍 TESTE 1: OCR - Extração de Texto")
    print("="*60)
    
    from app.services.ocr_service import OCRService
    
    # Teste 1: Extração de CPF/CNPJ de texto
    print("\n📝 Teste 1.1: Extração de CPF/CNPJ de texto")
    texto_teste = """
    Documento de identificação:
    CPF: 123.456.789-00
    CNPJ: 12.345.678/0001-90
    CAR: SP-1234567-A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6
    Email: contato@fazenda.com.br
    Telefone: (11) 98765-4321
    Área: 150,5 ha
    """
    
    resultado = OCRService.extract_cpf_cnpj(texto_teste)
    print(f"  ✅ CPFs encontrados: {resultado['cpf']}")
    print(f"  ✅ CNPJs encontrados: {resultado['cnpj']}")
    
    # Teste 2: Extração de todas entidades
    print("\n📝 Teste 1.2: Extração de todas entidades")
    entidades = OCRService._extract_all_entities(texto_teste)
    for tipo, valores in entidades.items():
        print(f"  ✅ {tipo}: {valores}")
    
    print("\n✅ Testes de OCR concluídos!")


async def test_ibama():
    """Testa integração com IBAMA"""
    print("\n" + "="*60)
    print("🌳 TESTE 2: IBAMA - Embargos Ambientais")
    print("="*60)
    
    from app.services.integrations.ibama_service import IBAMAService
    
    # Teste com CPF/CNPJ fictício
    cpf_cnpj_teste = "12.345.678/0001-90"
    
    print(f"\n📝 Consultando embargos para: {cpf_cnpj_teste}")
    
    async with IBAMAService() as service:
        embargos = await service.consultar_embargo(cpf_cnpj_teste)
        
        if embargos:
            print(f"  ⚠️  {len(embargos)} embargo(s) encontrado(s):")
            for embargo in embargos[:3]:  # Mostrar primeiros 3
                print(f"    - {embargo.tipo_infracao}")
                print(f"      Multa: R$ {embargo.valor_multa:,.2f}")
                print(f"      Local: {embargo.municipio}/{embargo.uf}")
        else:
            print("  ✅ Nenhum embargo encontrado")
    
    print("\n✅ Teste IBAMA concluído!")


async def test_funai():
    """Testa integração com FUNAI"""
    print("\n" + "="*60)
    print("🏞️  TESTE 3: FUNAI - Terras Indígenas")
    print("="*60)
    
    from app.services.integrations.funai_service import FUNAIService
    
    # Teste 1: Buscar terras no Pará
    print("\n📝 Teste 3.1: Buscar terras indígenas no PA")
    
    async with FUNAIService() as service:
        terras = await service.consultar_terras_indigenas(uf="PA")
        
        if terras:
            print(f"  ✅ {len(terras)} terra(s) indígena(s) encontrada(s)")
            # Mostrar primeiras 3
            for terra in terras[:3]:
                print(f"    - {terra.nome} ({terra.etnia})")
                print(f"      Área: {terra.area_hectares:,.0f} ha")
                print(f"      Fase: {terra.fase}")
        else:
            print("  ℹ️  Nenhuma terra encontrada (API pode estar indisponível)")
    
    # Teste 2: Verificar sobreposição (coordenadas de Brasília)
    print("\n📝 Teste 3.2: Verificar sobreposição em Brasília")
    
    async with FUNAIService() as service:
        resultado = await service.verificar_sobreposicao_por_coordenadas(
            latitude=-15.7942,
            longitude=-47.8822,
            raio_km=50.0
        )
        
        if resultado.tem_sobreposicao:
            print(f"  ⚠️  SOBREPOSIÇÃO DETECTADA!")
            print(f"  {len(resultado.terras_sobrepostas)} terra(s) no raio de 50km")
        else:
            print("  ✅ Nenhuma sobreposição detectada")
    
    print("\n✅ Teste FUNAI concluído!")


async def test_icmbio():
    """Testa integração com ICMBio"""
    print("\n" + "="*60)
    print("🦜 TESTE 4: ICMBio - Unidades de Conservação")
    print("="*60)
    
    from app.services.integrations.icmbio_service import ICMBioService
    
    # Teste 1: Buscar UCs no Mato Grosso
    print("\n📝 Teste 4.1: Buscar UCs no MT")
    
    async with ICMBioService() as service:
        unidades = await service.consultar_unidades_conservacao(uf="MT")
        
        if unidades:
            print(f"  ✅ {len(unidades)} unidade(s) de conservação encontrada(s)")
            # Mostrar primeiras 3
            for uc in unidades[:3]:
                print(f"    - {uc.nome}")
                print(f"      Categoria: {uc.categoria}")
                print(f"      Área: {uc.area_hectares:,.0f} ha")
        else:
            print("  ℹ️  Nenhuma UC encontrada (API pode estar indisponível)")
    
    # Teste 2: Verificar sobreposição (Chapada dos Guimarães)
    print("\n📝 Teste 4.2: Verificar sobreposição na Chapada dos Guimarães")
    
    async with ICMBioService() as service:
        resultado = await service.verificar_sobreposicao_por_coordenadas(
            latitude=-15.4603,
            longitude=-55.7472,
            raio_km=20.0
        )
        
        if resultado.tem_sobreposicao:
            print(f"  ⚠️  SOBREPOSIÇÃO COM UC DETECTADA!")
            print(f"  {len(resultado.unidades_sobrepostas)} UC(s) no raio de 20km")
            for uc in resultado.unidades_sobrepostas[:2]:
                print(f"    - {uc.nome} ({uc.categoria})")
        else:
            print("  ✅ Nenhuma sobreposição detectada")
    
    print("\n✅ Teste ICMBio concluído!")


async def main():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("🧪 TESTES - OCR e Integrações Ambientais - AgroADB")
    print("="*60)
    
    try:
        # Teste OCR (local, sempre funciona)
        await test_ocr()
        
        # Testes de integrações (dependem de APIs externas)
        print("\n" + "="*60)
        print("⚠️  ATENÇÃO: Próximos testes dependem de APIs externas")
        print("   Podem falhar se as APIs estiverem indisponíveis")
        print("="*60)
        
        await test_ibama()
        await test_funai()
        await test_icmbio()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        return
    except Exception as e:
        print(f"\n\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("="*60)
    print("\nNotas:")
    print("- Testes de APIs externas podem falhar se serviços estiverem indisponíveis")
    print("- Use dados reais para testes mais completos")
    print("- Consulte OCR_INTEGRACOES_AMBIENTAIS.md para documentação completa")
    print()


if __name__ == "__main__":
    # Verificar dependências
    try:
        import aiohttp
        import beautifulsoup4
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("   Instale: pip install -r backend/requirements.txt")
        sys.exit(1)
    
    # Executar testes
    asyncio.run(main())
