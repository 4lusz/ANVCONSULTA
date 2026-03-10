from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path


from backend.api.admin_auth import router as admin_auth_router
from backend.api.admin import router as admin_router
from backend.api.health import router as health_router
from backend.api.auth import router as auth_router
from backend.api.client import router as client_router
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="AnvConsulta")




app.add_middleware(
    CORSMiddleware,
    allow_origins=["http//:72.62.106.107:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.core.database import criar_tabelas
criar_tabelas()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= API =================
app.include_router(health_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(client_router)
app.include_router(admin_auth_router)
# ================= TESTE =================
@app.get("/_test-client")
def test_client():
    return FileResponse(
        BASE_DIR / "frontend_cliente" / "index.html"
    )

# ================= FRONTENDS =================


# FRONTEND CLIENTE
app.mount(
    "/client",
    StaticFiles(directory=BASE_DIR / "frontend_cliente", html=True),
    name="client"
)

# FRONTEND ADMIN
app.mount(
    "/admin-ui",
    StaticFiles(directory=BASE_DIR / "frontend", html=True),
    name="admin-ui"
)


