from fastapi import APIRouter

from stargazer.api.routes import repos

api_router = APIRouter()
api_router.include_router(repos.router)
