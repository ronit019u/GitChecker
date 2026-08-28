from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import FRONTEND_URL 
from src.gitchecker.routes import auth_route, check

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_route.router)
app.include_router(check.router)
