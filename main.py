from fastapi import FastAPI
import routes.rotas_consultas as consultas
import routes.rotas_health_check as healthcheck
import uvicorn

app = FastAPI()

app.include_router(consultas.router, prefix="/consultar")
app.include_router(healthcheck.router, prefix="/health")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
