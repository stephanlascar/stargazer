from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Optional, Dict, Union, List
from unittest import IsolatedAsyncioTestCase

from aiohttp import ClientSession
from aioresponses import aioresponses

from stargazer.api.clients.github import GitHubClient


@dataclass
class GitHubResponseContext:
    url: str
    status: int = 200
    payload: Optional[Union[Dict, List]] = None


class AbstractTestGitHubClient(IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = GitHubClient(token="dummy token")

    @asynccontextmanager
    async def github_test_context(self, contexts: List[GitHubResponseContext]):
        with aioresponses() as mock_request:
            for context in contexts:
                mock_request.get(url=context.url, status=context.status, payload=context.payload)
            async with ClientSession() as session:
                yield session


class TestGetStargazersGitHubClient(AbstractTestGitHubClient):
    async def test_return_empty_list_on_404(self):
        async with self.github_test_context([
            GitHubResponseContext(
                url="https://api.github.com/repos/tony_stark/jarvis/stargazers?page=1&per_page=100",
                status=404
            )
        ]) as session:
            result = [user async for user in self.client.get_stargazers(session, "tony_stark", "jarvis")]
            self.assertListEqual([], result)

    async def test_return_all_stargazers_on_small_dataset(self):
        async with self.github_test_context([
            GitHubResponseContext(
                url="https://api.github.com/repos/tony_stark/jarvis/stargazers?page=1&per_page=100",
                payload=[{"login": "iron_man"}, {"login": "hulk"}]
            )
        ]) as session:
            result = [user async for user in self.client.get_stargazers(session, "tony_stark", "jarvis")]
            self.assertListEqual(["iron_man", "hulk"], result)

    async def test_return_all_stargazers_from_multiple_pages(self):
        async with self.github_test_context([
            GitHubResponseContext(
                url="https://api.github.com/repos/tony_stark/jarvis/stargazers?page=1&per_page=3",
                payload=[{"login": "iron_man"}, {"login": "hulk"}, {"login": "captain_america"}]
            ),
            GitHubResponseContext(
                url="https://api.github.com/repos/tony_stark/jarvis/stargazers?page=2&per_page=3",
                payload=[{"login": "thor"}]
            )
        ]) as session:
            result = [user async for user in self.client.get_stargazers(session, "tony_stark", "jarvis", per_page=3)]
            self.assertListEqual(['iron_man', 'hulk', 'captain_america', 'thor'], result)


class TestGetUserStarredRepositoriesGitHubClient(AbstractTestGitHubClient):
    async def test_return_empty_list_on_404(self):
        async with self.github_test_context([
            GitHubResponseContext(
                url="https://api.github.com/users/tony_stark/starred?page=1&per_page=100",
                status=404
            )
        ]) as session:
            result = [user async for user in self.client.get_user_starred_repositories(session, "tony_stark")]
            self.assertListEqual([], result)

    async def test_return_all_user_starred_repositories_on_small_dataset(self):
        async with self.github_test_context([
            GitHubResponseContext(
                url="https://api.github.com/users/tony_stark/starred?page=1&per_page=100",
                payload=[{"owner": {"login": "thor"}, "name": "mjolnir"}, {"owner": {"login": "nick_fury"}, "name": "shield"}]
            )
        ]) as session:
            result = [user async for user in self.client.get_user_starred_repositories(session, "tony_stark")]
            self.assertListEqual(['thor/mjolnir', 'nick_fury/shield'], result)

    async def test_return_all_stargazers_from_multiple_pages(self):
        async with self.github_test_context([
            GitHubResponseContext(
                url="https://api.github.com/users/tony_stark/starred?page=1&per_page=1",
                payload=[{"owner": {"login": "thor"}, "name": "mjolnir"}]
            ),
            GitHubResponseContext(
                url="https://api.github.com/users/tony_stark/starred?page=2&per_page=1",
                payload=[{"owner": {"login": "nick_fury"}, "name": "shield"}]
            ),
            GitHubResponseContext(
                url="https://api.github.com/users/tony_stark/starred?page=3&per_page=1"
            )
        ]) as session:
            result = [user async for user in self.client.get_user_starred_repositories(session, "tony_stark", per_page=1)]
            self.assertListEqual(['thor/mjolnir', 'nick_fury/shield'], result)
