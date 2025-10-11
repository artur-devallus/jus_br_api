from fastapi import FastAPI

from api.routers import auth as auth_router, users as users_router, queries as queries_router

app = FastAPI(title="Jus BR API")

app.include_router(auth_router.router, prefix='/v1')
app.include_router(users_router.router, prefix='/v1')
app.include_router(queries_router.router, prefix='/v1')


# health
@app.get("/v1/health")
def health():
    return dict(status='ok')
