from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import (
    auth as auth_router,
    users as users_router,
    queries as queries_router,
    processes as processes_router
)

app = FastAPI(title="Jus BR API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://151.243.218.157:8081',
        'http://127.0.0.1:5173',
        'http://localhost:5173',
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix='/v1')
app.include_router(users_router.router, prefix='/v1')
app.include_router(queries_router.router, prefix='/v1')
app.include_router(processes_router.router, prefix='/v1')


# health
@app.get("/v1/health")
def health():
    return dict(status='ok')
