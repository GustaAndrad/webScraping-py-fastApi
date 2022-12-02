from fastapi import APIRouter
import controller.controle_health_check as controle_health_check


router = APIRouter()


@router.get("/ready")
async def health_check():
    return await controle_health_check.consulta_health_check()
