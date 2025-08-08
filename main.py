from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging, logging.config, json, pathlib

from routers import auth, src, ml, optional

# Monitoring
from prometheus_fastapi_instrumentator import Instrumentator
from monitoring_addon.logging_middleware import RequestLogMiddleware


# --- Logging estruturado (antes de criar a app) ---
LOGGING_PATH = pathlib.Path(__file__).resolve().parent / "monitoring_addon" / "logging.json"
logging.config.dictConfig(json.loads(LOGGING_PATH.read_text()))

app = FastAPI(
    title="BookScraper API",
    version="1.0.0",
    description="API para servir dados do Snowflake",
)

# --- CORS (ajuste os domínios permitidos) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # coloque domínios específicos em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Middleware de logs ---
app.add_middleware(RequestLogMiddleware)

# --- Métricas Prometheus ---
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# --- Opcional: endpoint de saúde ---
@app.get("/health")
def health():
    return {"status": "ok"}

# --- Routers da aplicação ---
app.include_router(auth.router)
app.include_router(src.router)
app.include_router(optional.router)
app.include_router(ml.router)


@app.middleware("http")
async def add_trace_id_header(request, call_next):
    response = await call_next(request)
    trace_id = getattr(request.state, "trace_id", None)
    if trace_id:
        response.headers["X-Request-ID"] = trace_id
    return response
