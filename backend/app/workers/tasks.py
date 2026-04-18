"""
Celery Tasks for Investigation
"""
import asyncio
import logging
from typing import List

logger = logging.getLogger(__name__)

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.repositories.investigation import InvestigationRepository
from app.repositories.user import UserRepository
from app.domain.investigation import InvestigationStatus
from app.scrapers.car_scraper import CARScraper
from app.scrapers.incra_scraper import INCRAScraper
from app.scrapers.receita_scraper import ReceitaScraper
from app.services.email_service import EmailService


@celery_app.task(name="start_investigation")
def start_investigation_task(investigation_id: int) -> dict:
    """Start investigation process"""
    return asyncio.run(_start_investigation(investigation_id))


@celery_app.task(name="heavy_investigation")
def heavy_investigation_task(investigation_id: int) -> dict:
    """
    Pipeline pós-investigação (agregações pesadas, refresh de MV no PostgreSQL, etc.).
    Executado em fila separada quando ENABLE_HEAVY_INVESTIGATION_QUEUE está activo.
    """
    return asyncio.run(_heavy_investigation_pipeline(investigation_id))


async def _heavy_investigation_pipeline(investigation_id: int) -> dict:
    from app.services.materialized_views import try_refresh_investigation_summary

    async with AsyncSessionLocal() as db:
        refreshed = await try_refresh_investigation_summary(db)
        await db.commit()
        logger.info(
            "heavy_investigation_task concluída id=%s mv_refresh=%s",
            investigation_id,
            refreshed,
        )
        return {"investigation_id": investigation_id, "mv_refreshed": refreshed}


async def _start_investigation(investigation_id: int) -> dict:
    """Async function to run investigation"""
    async with AsyncSessionLocal() as db:
        investigation_repo = InvestigationRepository(db)
        
        # Get investigation
        investigation = await investigation_repo.get(investigation_id)
        if not investigation:
            return {"status": "error", "message": "Investigation not found"}
        
        logger.info(f"Iniciando investigação {investigation_id}")
        
        # Update status to in progress
        await investigation_repo.update(
            investigation_id, {"status": InvestigationStatus.IN_PROGRESS}
        )
        await db.commit()
        
        logger.info(f"Investigação {investigation_id} em andamento")
        
        try:
            # Run scrapers
            results = {
                "properties": [],
                "lease_contracts": [],
                "companies": [],
            }
            
            # CAR Scraper
            logger.info(f"Executando scraper CAR para investigação {investigation_id}")
            car_scraper = CARScraper()
            car_results = await car_scraper.search(
                investigation.target_name,
                investigation.target_cpf_cnpj,
            )
            results["properties"].extend(car_results)
            
            # INCRA Scraper
            logger.info(f"Executando scraper INCRA para investigação {investigation_id}")
            incra_scraper = INCRAScraper()
            incra_results = await incra_scraper.search(
                investigation.target_name,
                investigation.target_cpf_cnpj,
            )
            results["properties"].extend(incra_results)
            
            # Receita Federal Scraper
            if investigation.target_cpf_cnpj:
                logger.info(f"Executando scraper Receita para investigação {investigation_id}")
                receita_scraper = ReceitaScraper()
                company_results = await receita_scraper.search(investigation.target_cpf_cnpj)
                results["companies"].extend(company_results)
            
            # Update investigation with results
            await investigation_repo.update(
                investigation_id,
                {
                    "status": InvestigationStatus.COMPLETED,
                    "properties_found": len(results["properties"]),
                    "lease_contracts_found": len(results["lease_contracts"]),
                    "companies_found": len(results["companies"]),
                },
            )
            await db.commit()
            
            logger.info(f"Investigação {investigation_id} concluída: {len(results['properties'])} propriedades, {len(results['companies'])} empresas")
            
            # Enviar email de notificação ao usuário
            try:
                user_repo = UserRepository(db)
                user = await user_repo.get(investigation.user_id)
                
                if user and user.email:
                    await EmailService.send_investigation_completed(
                        user_email=user.email,
                        user_name=user.full_name or user.username,
                        investigation={
                            'id': investigation.id,
                            'target_name': investigation.target_name,
                            'properties_found': len(results["properties"]),
                            'companies_found': len(results["companies"]),
                            'lease_contracts_found': len(results["lease_contracts"])
                        }
                    )
                    logger.info(f"📧 Email de conclusão enviado para {user.email}")
            except Exception as email_error:
                logger.warning(f"Falha ao enviar email de conclusão: {email_error}")
                # Não falhar a task se o email falhar
            
            return {
                "status": "success",
                "investigation_id": investigation_id,
                "results": results,
            }
        
        except Exception as e:
            logger.error(f"Erro na investigação {investigation_id}: {str(e)}", exc_info=True)
            
            # Update status to failed
            await investigation_repo.update(
                investigation_id, {"status": InvestigationStatus.FAILED}
            )
            await db.commit()
            
            return {
                "status": "error",
                "investigation_id": investigation_id,
                "message": str(e),
            }
