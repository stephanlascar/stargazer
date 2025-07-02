import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import List
from aiohttp import ClientSession

from stargazer.api.clients.github import GitHubClient
from stargazer.api.dto.starneighbour import StarNeighbourResponse

logger = logging.getLogger(__name__)


@dataclass
class UserStarredRepositories:
    """
    Data class representing a GitHub user and the list of repositories they have starred.
    """

    user_name: str
    repositories: List[str]


class StarNeighbourService:
    """
    Service layer responsible for finding 'neighbours' for a given GitHub repository.

    Neighbours are defined as repositories that share at least one stargazer with the target repository.
    """


    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    async def get_neighbours(self, user_name: str, repository_name: str):
        """
        Finds the repositories that have at least one stargazer in common with the given repository.

        :param user_name: Owner of the repository.
        :param repository_name: Name of the repository.
        :return: A list of StarNeighbourResponse objects representing neighbouring repositories and their common stargazers.
        """

        logger.debug('Get all neighbours "from %s/%s"', user_name, repository_name)

        async def collect_starred_repos(_session: ClientSession, stargazer: str):
            return UserStarredRepositories(
                user_name=stargazer,
                repositories=[repository async for repository in self.github_client.get_user_starred_repositories(session, stargazer)]
            )

        async with ClientSession() as session:
            stargazers = [stargazer async for stargazer in self.github_client.get_stargazers(session, user_name, repository_name)]
            workers = [collect_starred_repos(session, stargazer) for stargazer in stargazers]

            final_results: List[UserStarredRepositories] = await asyncio.gather(*workers)

            repos_to_stargazers = defaultdict(set)
            for user in final_results:
                for repo in user.repositories:
                    repos_to_stargazers[repo].add(user.user_name)

            return [
                StarNeighbourResponse(repo=repository, stargazers=sorted(list(user_names)))
                for repository, user_names in repos_to_stargazers.items() if repository != repository_name
            ]
