from pydantic import BaseModel
from typing import List


class StarNeighbourResponse(BaseModel):
    """
    Response model for a neighboring (related) repository based on shared stargazers.

    Attributes:
        repo (str): Full name of the neighboring repository (format: owner/repo).
        stargazers (List[str]): List of usernames who have starred both the target repository and this neighboring repository.
    """
    repo: str
    stargazers: List[str]
