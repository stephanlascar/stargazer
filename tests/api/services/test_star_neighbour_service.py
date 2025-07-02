import unittest
from unittest.mock import MagicMock

from stargazer.api.dto.starneighbour import StarNeighbourResponse
from stargazer.api.services.star_neighbour_service import StarNeighbourService


class TestStarNeighbourService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.github_client_mock = MagicMock()
        self.service = StarNeighbourService(self.github_client_mock)

    async def test_no_neighbour_if_main_repository_has_not_star(self):
        self.github_client_mock.get_stargazers = make_async_generator([])

        results = await self.service.get_neighbours("tony_stark", "iron_man")

        self.assertListEqual([], results)

    async def test_one_neighbour(self):
        self.github_client_mock.get_stargazers = make_async_generator(["thor"])
        self.github_client_mock.get_user_starred_repositories = make_async_generator(["mjolnir", "shield"])

        results = await self.service.get_neighbours("tony_stark", "iron_man")

        self.assertListEqual([
            StarNeighbourResponse(repo='mjolnir', stargazers=['thor']),
            StarNeighbourResponse(repo='shield', stargazers=['thor'])
        ], results)

    async def test_multiple_neighbours(self):
        starred_map = {
            "thor": ["mjolnir", "shield"],
            "nick_fury": ["shield", "jarvis", "infinity_gems"]
        }

        self.github_client_mock.get_stargazers = make_async_generator(["thor", "nick_fury"])
        self.github_client_mock.get_user_starred_repositories.side_effect = lambda session, stargazer: make_async_generator(starred_map.get(stargazer, []))()

        results = await self.service.get_neighbours("tony_stark", "iron_man")

        self.assertListEqual([
            StarNeighbourResponse(repo='mjolnir', stargazers=['thor']),
            StarNeighbourResponse(repo='shield', stargazers=['nick_fury', "thor"]),
            StarNeighbourResponse(repo='jarvis', stargazers=['nick_fury']),
            StarNeighbourResponse(repo='infinity_gems', stargazers=['nick_fury']),
        ], results)


def make_async_generator(items):
    async def generator(*args, **kwargs):
        for item in items:
            yield item
    return generator
