from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from stargazer.api.clients.github import GitHubClient
from stargazer.api.services.star_neighbour_service import StarNeighbourService
from stargazer.core.settings import get_settings


def get_star_neighbour_service():
    github_client = GitHubClient(token=get_settings().GITHUB_TOKEN)
    return StarNeighbourService(github_client)


security = HTTPBearer()

def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != get_settings().TOKEN:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
