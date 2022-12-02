from fastapi import APIRouter
import scapring.detranMG
import schemas.schemas

router = APIRouter()


@router.get("/detranmg", response_model=dict)
async def consulta_detran(entrada_detran: schemas.schemas.EntradaDetranMG):
    return await scapring.detranMG.detran_mg(entrada_detran)
