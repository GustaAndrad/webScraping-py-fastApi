import schemas.schemas as schemas


async def consulta_health_check():

    resposta = schemas.RespostaHealthCheck(status=200, descricao="API funcional")
    return resposta
