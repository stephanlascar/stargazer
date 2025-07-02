from fastapi import FastAPI, Depends

from stargazer.api.deps import verify_bearer_token
from stargazer.api.routes.main import api_router

app = FastAPI(dependencies=[Depends(verify_bearer_token)])

app.include_router(api_router)
