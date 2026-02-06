"""
Investigation Service
"""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

from app.domain.investigation import Investigation, InvestigationStatus
from app.repositories.investigation import InvestigationRepository
from app.schemas.investigation import InvestigationCreate, InvestigationUpdate
from app.workers.tasks import start_investigation_task
from app.core.config import settings


class InvestigationService:
    """Service for investigation operations"""
    
    def __init__(self, investigation_repo: InvestigationRepository):
        self.investigation_repo = investigation_repo
    
    async def create_investigation(
        self, user_id: int, investigation_data: InvestigationCreate
    ) -> Investigation:
        """Create a new investigation and start processing"""
        # Create investigation
        investigation_dict = investigation_data.model_dump()
        investigation_dict["user_id"] = user_id
        investigation_dict["status"] = InvestigationStatus.PENDING

        # Encrypt CPF/CNPJ before storage if encryption key is configured
        if settings.ENCRYPTION_KEY and investigation_dict.get("target_cpf_cnpj"):
            from app.core.encryption import data_encryption
            investigation_dict["target_cpf_cnpj"] = data_encryption.encrypt(
                investigation_dict["target_cpf_cnpj"]
            )
        
        investigation = await self.investigation_repo.create(investigation_dict)
        
        # Start async investigation task (somente se habilitado)
        if settings.ENABLE_WORKERS:
            start_investigation_task.delay(investigation.id)
        else:
            # Fallback síncrono: executa scrapers diretamente sem Celery/Redis
            logger.info(
                f"Workers desabilitados — executando fallback síncrono para investigação {investigation.id}"
            )
            await self._run_sync_fallback(investigation)
        
        return investigation
    
    async def _run_sync_fallback(self, investigation: Investigation) -> None:
        """
        Fallback síncrono: executa scrapers diretamente quando Celery/Redis
        não estão disponíveis. Atualiza a investigação com os resultados.
        """
        from app.scrapers.car_scraper import CARScraper
        from app.scrapers.incra_scraper import INCRAScraper
        from app.scrapers.receita_scraper import ReceitaScraper

        # Marca como em andamento
        await self.investigation_repo.update(
            investigation.id, {"status": InvestigationStatus.IN_PROGRESS}
        )

        results = {"properties": [], "lease_contracts": [], "companies": []}

        try:
            # CAR
            try:
                logger.info(f"[sync-fallback] Executando CAR para investigação {investigation.id}")
                car = CARScraper()
                car_res = await car.search(investigation.target_name, investigation.target_cpf_cnpj)
                results["properties"].extend(car_res)
            except Exception as exc:
                logger.warning(f"[sync-fallback] CAR falhou para investigação {investigation.id}: {exc}")

            # INCRA
            try:
                logger.info(f"[sync-fallback] Executando INCRA para investigação {investigation.id}")
                incra = INCRAScraper()
                incra_res = await incra.search(investigation.target_name, investigation.target_cpf_cnpj)
                results["properties"].extend(incra_res)
            except Exception as exc:
                logger.warning(f"[sync-fallback] INCRA falhou para investigação {investigation.id}: {exc}")

            # Receita Federal
            if investigation.target_cpf_cnpj:
                try:
                    logger.info(f"[sync-fallback] Executando Receita para investigação {investigation.id}")
                    receita = ReceitaScraper()
                    company_res = await receita.search(investigation.target_cpf_cnpj)
                    results["companies"].extend(company_res)
                except Exception as exc:
                    logger.warning(f"[sync-fallback] Receita falhou para investigação {investigation.id}: {exc}")

            # Marca como concluída
            await self.investigation_repo.update(
                investigation.id,
                {
                    "status": InvestigationStatus.COMPLETED,
                    "completed_at": datetime.utcnow(),
                    "properties_found": len(results["properties"]),
                    "lease_contracts_found": len(results["lease_contracts"]),
                    "companies_found": len(results["companies"]),
                },
            )
            logger.info(
                f"[sync-fallback] Investigação {investigation.id} concluída: "
                f"{len(results['properties'])} propriedades, {len(results['companies'])} empresas"
            )
        except Exception as exc:
            logger.error(
                f"[sync-fallback] Erro crítico na investigação {investigation.id}: {exc}",
                exc_info=True,
            )
            await self.investigation_repo.update(
                investigation.id, {"status": InvestigationStatus.FAILED}
            )
    
    async def get_investigation(
        self, investigation_id: int, user_id: int, is_superuser: bool = False
    ) -> Investigation:
        """Get investigation by ID"""
        investigation = await self.investigation_repo.get_with_relations(investigation_id)
        
        if not investigation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found",
            )
        
        # Check ownership
        if not is_superuser and investigation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this investigation",
            )

        # Decrypt CPF/CNPJ if encryption key is configured
        if settings.ENCRYPTION_KEY and investigation.target_cpf_cnpj:
            try:
                from app.core.encryption import data_encryption
                investigation.target_cpf_cnpj = data_encryption.decrypt(
                    investigation.target_cpf_cnpj
                )
            except Exception:
                pass  # Already decrypted or not encrypted
        
        return investigation
    
    async def list_investigations(
        self, user_id: int, skip: int = 0, limit: int = 20, is_superuser: bool = False
    ) -> tuple[List[Investigation], int]:
        """List investigations for a user"""
        if is_superuser:
            investigations = await self.investigation_repo.get_multi(
                skip=skip, limit=limit, order_by=Investigation.created_at.desc()
            )
            total = await self.investigation_repo.count()
        else:
            investigations = await self.investigation_repo.get_by_user(
                user_id, skip=skip, limit=limit
            )
            total = await self.investigation_repo.count_by_user(user_id)
        
        return investigations, total
    
    async def update_investigation(
        self,
        investigation_id: int,
        user_id: int,
        investigation_data: InvestigationUpdate,
        is_superuser: bool = False,
    ) -> Investigation:
        """Update investigation"""
        investigation = await self.investigation_repo.get(investigation_id)
        
        if not investigation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found",
            )
        
        # Check ownership
        if not is_superuser and investigation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this investigation",
            )
        
        # Update investigation
        update_dict = investigation_data.model_dump(exclude_unset=True)
        updated_investigation = await self.investigation_repo.update(
            investigation_id, update_dict
        )
        
        return updated_investigation
    
    async def delete_investigation(
        self, investigation_id: int, user_id: int, is_superuser: bool = False
    ) -> bool:
        """Delete investigation"""
        investigation = await self.investigation_repo.get(investigation_id)
        
        if not investigation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Investigation not found",
            )
        
        # Check ownership
        if not is_superuser and investigation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this investigation",
            )
        
        return await self.investigation_repo.delete(investigation_id)
    
    async def update_investigation_status(
        self, investigation_id: int, status: InvestigationStatus
    ) -> Investigation:
        """Update investigation status (internal use)"""
        update_data = {"status": status}
        
        if status == InvestigationStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        
        updated = await self.investigation_repo.update(investigation_id, update_data)
        return updated
