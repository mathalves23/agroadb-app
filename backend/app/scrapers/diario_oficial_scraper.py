"""
Diários Oficiais Scraper

Integração com múltiplas fontes de Diários Oficiais:
- Jusbrasil API (DOU, DOE, DOM)
- Diário Oficial da União (DOU) - IMPRENSA NACIONAL
- DOEs Estaduais via APIs quando disponíveis
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
import logging
import re

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class DiarioOficialScraper(BaseScraper):
    """
    Scraper para Diários Oficiais
    
    Busca publicações em:
    - DOU (Diário Oficial da União)
    - DOEs (Diários Oficiais Estaduais)
    - DOMs (Diários Oficiais Municipais)
    
    Funcionalidades:
    - Busca por termos/palavras-chave
    - Busca por CPF/CNPJ
    - Busca por nome de pessoa/empresa
    - Filtro por tipo de diário
    - Filtro por data de publicação
    - Monitoramento de termos
    """
    
    def __init__(self):
        super().__init__()
        
        # APIs disponíveis
        self.jusbrasil_api = "https://api.jusbrasil.com.br/api/diarios"
        self.dou_api = "https://www.in.gov.br/servicos/diario-oficial-da-uniao/api"
        
        # Tipos de diários
        self.diary_types = {
            "DOU": "Diário Oficial da União",
            "DOE": "Diário Oficial Estadual",
            "DOM": "Diário Oficial Municipal",
            "DJE": "Diário de Justiça Eletrônico",
        }
        
        # Cache de resultados
        self.cache: Dict[str, tuple[datetime, List[Dict[str, Any]]]] = {}
        self.cache_ttl = timedelta(hours=24)
    
    def _get_from_cache(self, key: str) -> Optional[List[Dict[str, Any]]]:
        """Busca resultado do cache se ainda válido"""
        if key in self.cache:
            timestamp, data = self.cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _save_to_cache(self, key: str, data: List[Dict[str, Any]]) -> None:
        """Salva resultado no cache"""
        self.cache[key] = (datetime.now(), data)
    
    async def search(
        self,
        query: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        diary_type: Optional[str] = None,
        state: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca publicações em Diários Oficiais
        
        Args:
            query: Termo de busca (CPF, CNPJ, nome, palavra-chave)
            start_date: Data inicial de publicação
            end_date: Data final de publicação
            diary_type: Tipo de diário (DOU, DOE, DOM, DJE)
            state: Estado para DOE/DOM (ex: SP, RJ, MG)
        
        Returns:
            Lista de publicações encontradas
        """
        # Verificar cache
        cache_key = f"{query}_{start_date}_{end_date}_{diary_type}_{state}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        results = []
        
        try:
            # Buscar em Jusbrasil (cobertura ampla)
            jusbrasil_results = await self._search_jusbrasil(
                query, start_date, end_date, diary_type, state
            )
            results.extend(jusbrasil_results)
            
            # Buscar em DOU oficial (se aplicável)
            if not diary_type or diary_type == "DOU":
                dou_results = await self._search_dou(query, start_date, end_date)
                results.extend(dou_results)
            
            # Remover duplicatas
            results = self._remove_duplicates(results)
            
            # Salvar no cache
            if results:
                self._save_to_cache(cache_key, results)
        
        except Exception as e:
            logger.error(f"Error searching diários oficiais: {str(e)}")
        
        return results
    
    async def _search_jusbrasil(
        self,
        query: str,
        start_date: Optional[date],
        end_date: Optional[date],
        diary_type: Optional[str],
        state: Optional[str],
    ) -> List[Dict[str, Any]]:
        """
        Busca no Jusbrasil
        
        Nota: Requer autenticação (token Bearer)
        Em produção, configurar token nas variáveis de ambiente
        """
        results = []
        
        try:
            # Construir parâmetros de busca
            params = {
                "q": query,
                "page": 1,
                "per_page": 50,
            }
            
            if start_date:
                params["date_from"] = start_date.isoformat()
            if end_date:
                params["date_to"] = end_date.isoformat()
            if diary_type:
                params["diary_type"] = diary_type
            if state:
                params["state"] = state
            
            # TODO: Em produção, adicionar token de autenticação
            # headers = {"Authorization": f"Bearer {JUSBRASIL_TOKEN}"}
            
            # Simulação de estrutura de retorno
            # Em produção, fazer requisição real:
            # response = await self.fetch(
            #     f"{self.jusbrasil_api}/search",
            #     params=params,
            #     headers=headers
            # )
            
            # Estrutura esperada de retorno
            publication = {
                "id": f"jb_{query[:8]}",
                "source": "Jusbrasil",
                "diary_type": diary_type or "DOU",
                "diary_name": self.diary_types.get(diary_type or "DOU"),
                "publication_date": (start_date or date.today()).isoformat(),
                "title": f"Publicação relacionada a {query}",
                "content": f"Conteúdo da publicação mencionando {query}...",
                "snippet": f"...{query}...",
                "page": 1,
                "section": "Seção 3",
                "url": f"https://www.jusbrasil.com.br/diarios/busca?q={query}",
                "state": state,
                "city": None,
                "keywords": self._extract_keywords(query),
                "consulted_at": datetime.now().isoformat(),
            }
            
            results.append(publication)
        
        except Exception as e:
            logger.error(f"Error in Jusbrasil search: {str(e)}")
        
        return results
    
    async def _search_dou(
        self,
        query: str,
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> List[Dict[str, Any]]:
        """
        Busca no DOU (Imprensa Nacional)
        
        API oficial do Diário Oficial da União
        """
        results = []
        
        try:
            # Construir URL de busca
            params = {
                "q": query,
                "data_inicio": (start_date or date.today()).strftime("%d-%m-%Y"),
                "data_fim": (end_date or date.today()).strftime("%d-%m-%Y"),
            }
            
            # TODO: Em produção, fazer requisição real
            # response = await self.fetch(
            #     f"{self.dou_api}/pesquisa",
            #     params=params
            # )
            
            # Estrutura esperada de retorno
            publication = {
                "id": f"dou_{query[:8]}",
                "source": "DOU - Imprensa Nacional",
                "diary_type": "DOU",
                "diary_name": "Diário Oficial da União",
                "publication_date": (start_date or date.today()).isoformat(),
                "title": f"Publicação DOU - {query}",
                "content": f"Texto completo da publicação no DOU...",
                "snippet": f"...{query}...",
                "page": 1,
                "section": "Seção 3",
                "url": f"https://www.in.gov.br/consulta?q={query}",
                "state": None,
                "city": None,
                "keywords": self._extract_keywords(query),
                "consulted_at": datetime.now().isoformat(),
            }
            
            results.append(publication)
        
        except Exception as e:
            logger.error(f"Error in DOU search: {str(e)}")
        
        return results
    
    async def search_by_cpf_cnpj(
        self,
        cpf_cnpj: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca publicações relacionadas a um CPF/CNPJ
        
        Args:
            cpf_cnpj: CPF ou CNPJ (com ou sem formatação)
            start_date: Data inicial
            end_date: Data final
        
        Returns:
            Lista de publicações encontradas
        """
        # Limpar CPF/CNPJ
        doc_clean = re.sub(r'[^\d]', '', cpf_cnpj)
        
        # Buscar por diferentes formatos
        results = []
        
        # Formato limpo
        results.extend(await self.search(doc_clean, start_date, end_date))
        
        # Formato formatado (se for CNPJ)
        if len(doc_clean) == 14:
            formatted = f"{doc_clean[:2]}.{doc_clean[2:5]}.{doc_clean[5:8]}/{doc_clean[8:12]}-{doc_clean[12:]}"
            results.extend(await self.search(formatted, start_date, end_date))
        
        # Formato formatado (se for CPF)
        elif len(doc_clean) == 11:
            formatted = f"{doc_clean[:3]}.{doc_clean[3:6]}.{doc_clean[6:9]}-{doc_clean[9:]}"
            results.extend(await self.search(formatted, start_date, end_date))
        
        return self._remove_duplicates(results)
    
    async def search_by_name(
        self,
        name: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        diary_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca publicações relacionadas a um nome
        
        Args:
            name: Nome da pessoa ou empresa
            start_date: Data inicial
            end_date: Data final
            diary_type: Tipo de diário
        
        Returns:
            Lista de publicações encontradas
        """
        return await self.search(name, start_date, end_date, diary_type)
    
    async def monitor_term(
        self,
        term: str,
        diary_type: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Configura monitoramento de termo em diários oficiais
        
        Args:
            term: Termo a ser monitorado
            diary_type: Tipo de diário
            state: Estado (para DOE/DOM)
        
        Returns:
            Configuração do monitoramento
        """
        return {
            "monitor_id": f"mon_{term[:10]}_{datetime.now().timestamp()}",
            "term": term,
            "diary_type": diary_type,
            "state": state,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_check": None,
            "total_findings": 0,
        }
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave da query"""
        # Remover palavras comuns
        stop_words = ["de", "da", "do", "a", "o", "e", "em", "para", "com"]
        
        words = query.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return keywords[:10]  # Máximo 10 keywords
    
    def _remove_duplicates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove publicações duplicadas"""
        seen = set()
        unique = []
        
        for result in results:
            # Usar ID como chave única
            key = result.get("id")
            if key and key not in seen:
                seen.add(key)
                unique.append(result)
        
        return unique
    
    def get_diary_types(self) -> Dict[str, str]:
        """Retorna tipos de diários disponíveis"""
        return self.diary_types.copy()
    
    def clear_cache(self) -> None:
        """Limpa todo o cache de resultados"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_entries = len(self.cache)
        valid_entries = sum(
            1 for timestamp, _ in self.cache.values()
            if datetime.now() - timestamp < self.cache_ttl
        )
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "ttl_hours": self.cache_ttl.total_seconds() / 3600,
        }
