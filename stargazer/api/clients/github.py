import itertools
from abc import ABC

from typing import List, AsyncGenerator, Callable, Any

from aiohttp import ClientSession


class AbstractGitHubClient(ABC):
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.headers = {"Accept": "application/vnd.github.v3+json", "Authorization": f"Bearer {token}"}

    async def _get(
        self, session: ClientSession, endpoint: str, extract_func: Callable[[Any], List[Any]], per_page: int = 100, max_pages: int = 5
    ):
        """
        Generic async generator for fetching paginated GitHub API resources.

        :param session: An aiohttp ClientSession.
        :param endpoint: The GitHub API endpoint (relative to BASE_URL).
        :param extract_func: A function to extract the desired items from the response payload.
        :param per_page: Number of items per page (max 100 for GitHub).
        :param max_pages: Maximum number of pages to fetch.
        :yield: Each item as yielded by extract_func.
        """
        for page in itertools.count(1):
            async with session.get(
                    url=f"{self.BASE_URL}{endpoint}",
                    params=dict(per_page=per_page, page=page),
                    headers=self.headers
            ) as response:
                if page > max_pages:
                    break

                if response.status == 404:
                    break

                data = await response.json()
                if not data:
                    break

                items = extract_func(data)
                for item in items:
                    yield item

                if len(items) < per_page:
                    break


class GitHubClient(AbstractGitHubClient):

    async def get_stargazers(self, session: ClientSession, user_name: str, repository_name: str, per_page: int = 100, max_pages: int = 5 ) -> AsyncGenerator[str, None]:
        """
        Yields the usernames of stargazers for the given repository.

        :param session: An aiohttp ClientSession.
        :param user_name: Owner of the repository.
        :param repository_name: Name of the repository.
        :param per_page: Number of results per page.
        :param max_pages: Maximum number of pages to fetch.
        :yield: Usernames of stargazers.
        """
        async for user in self._get(
            session=session,
            endpoint=f"/repos/{user_name}/{repository_name}/stargazers",
            extract_func=lambda items: [item["login"] for item in items],
            per_page=per_page,
            max_pages=max_pages
        ):
            yield user

    async def get_user_starred_repositories(self, session: ClientSession, user_name: str, per_page: int = 100, max_pages: int = 5) -> AsyncGenerator[str, None]:
        """
        Yields the full names of repositories starred by the given user (format: owner/repo).

        :param session: An aiohttp ClientSession.
        :param user_name: Username whose starred repositories to fetch.
        :param per_page: Number of results per page.
        :param max_pages: Maximum number of pages to fetch.
        :yield: Full names of repositories (owner/repo).
        """
        async for user in self._get(
            session=session,
            endpoint=f"/users/{user_name}/starred",
            extract_func = lambda items: [f"{item['owner']['login']}/{item['name']}" for item in items],
            per_page=per_page,
            max_pages=max_pages
        ):
            yield user
