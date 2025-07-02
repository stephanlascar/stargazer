import unittest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from stargazer.api.deps import get_star_neighbour_service, verify_bearer_token
from stargazer.api.dto.starneighbour import StarNeighbourResponse
from stargazer.api.services.star_neighbour_service import StarNeighbourService
from stargazer.main import app


class TestBaseStarNeighbourRoutes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_service = AsyncMock(spec=StarNeighbourService)
        self.client = TestClient(app)
        app.dependency_overrides = {get_star_neighbour_service: lambda: self.mock_service}


class TestSecurityStarNeighbourRoutes(TestBaseStarNeighbourRoutes):

    def setUp(self):
        super().setUp()

    async def test_protected_route(self):
        response = self.client.get("/repos/someuser/repo/somerepo/starneighbours")

        self.assertEqual(403, response.status_code)


class TestRouteStarNeighbourRoutes(TestBaseStarNeighbourRoutes):

    def setUp(self):
        super().setUp()
        app.dependency_overrides[verify_bearer_token] = lambda: None

    async def test_no_neighbours(self):
        self.mock_service.get_neighbours.return_value = []

        response = self.client.get("/repos/user/repo/repo1/starneighbours")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])


    async def test_multiple_neighbours(self):
        self.mock_service.get_neighbours.return_value = [
            StarNeighbourResponse(
                repo="mjolnir",
                stargazers=["thor"]
            ),
            StarNeighbourResponse(
                repo="shield",
                stargazers=["thor", "nick_fury"]
            )
        ]

        response = self.client.get("/repos/tony_start/repo/jarvis/starneighbours")
        data = response.json()

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["repo"], "mjolnir")
        self.assertEqual(data[0]["stargazers"], ["thor"])
        self.assertEqual(data[1]["repo"], "shield")
        self.assertEqual(data[1]["stargazers"], ["thor", "nick_fury"])


class TestCachePolicyStarNeighbourRoutes(TestBaseStarNeighbourRoutes):

    def setUp(self):
        super().setUp()
        app.dependency_overrides[verify_bearer_token] = lambda: None

    async def test_do_not_call_multiple_time_service_with_same_url(self):
        self.mock_service.get_neighbours.return_value = [
            StarNeighbourResponse(
                repo="mjolnir",
                stargazers=["thor"]
            )
        ]

        response = self.client.get("/repos/someuser/repo/somerepo/starneighbours")
        data = response.json()

        self.assertEqual(data[0]["stargazers"], ["thor"])
        self.mock_service.get_neighbours.assert_called_once()
        self.mock_service.get_neighbours.reset_mock()

        response = self.client.get("/repos/someuser/repo/somerepo/starneighbours")
        data = response.json()

        self.assertEqual(data[0]["stargazers"], ["thor"])
        self.mock_service.get_neighbours.assert_not_called()
        self.mock_service.get_neighbours.reset_mock()

        response = self.client.get("/repos/otherone/repo/somerepo/starneighbours")
        data = response.json()

        self.assertEqual(data[0]["stargazers"], ["thor"])
        self.mock_service.get_neighbours.assert_called_once()
        self.mock_service.get_neighbours.reset_mock()

