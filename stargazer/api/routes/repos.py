from aiocache import cached
from fastapi import APIRouter, Depends

from stargazer.api.deps import get_star_neighbour_service
from stargazer.api.dto.starneighbour import StarNeighbourResponse
from stargazer.api.services.star_neighbour_service import StarNeighbourService


GITHUB_API_URL = "https://api.github.com"


def make_cache_key_builder(url: str):
    def url_key_builder(func, **kwargs: dict) -> str:
        return url.format(**kwargs)
    return url_key_builder


router = APIRouter(prefix="/repos", tags=["repos"])


@router.get(
    "/{user_name}/repo/{repository_name}/starneighbours",
    response_model=list[StarNeighbourResponse],
    summary="List neighboring repositories by common stargazers"
)
@cached(ttl=60, key_builder=make_cache_key_builder("/{user_name}/repo/{repository_name}/starneighbours"))
async def star_neighbours(
    user_name: str,
    repository_name: str,
    service: StarNeighbourService = Depends(get_star_neighbour_service)
):
    return await service.get_neighbours(user_name, repository_name)


