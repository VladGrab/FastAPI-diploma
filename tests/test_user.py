import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_info(client: AsyncClient):
    response = await client.get("/api/users/me", headers={"api-key": "test_1"})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data == {"result": True,
                             "user": {"id": 1,
                                      "name": "Test User 1",
                                      "followers": [],
                                      "following": []
                                      }
                             }


async def test_following(client: AsyncClient):
    request = await client.post("/api/users/2/follow",
                                headers={"api-key": "test_1"})
    assert request.status_code == 200
    response = await client.get("/api/users/me", headers={"api-key": "test_1"})
    response_data = response.json()
    assert response_data == {"result": True,
                             "user": {"id": 1,
                                      "name": "Test User 1",
                                      "followers": [],
                                      "following": [
                                          {"id": 2, "name": "Test User 2"}
                                      ]
                                      }
                             }


async def test_unfollowing(client: AsyncClient):
    request = await client.delete("/api/users/2/follow",
                                  headers={"api-key": "test_1"})
    assert request.status_code == 200
    response = await client.get("/api/users/me", headers={"api-key": "test_1"})
    response_data = response.json()
    assert response_data == {"result": True,
                             "user": {"id": 1,
                                      "name": "Test User 1",
                                      "followers": [],
                                      "following": []
                                      }
                             }
