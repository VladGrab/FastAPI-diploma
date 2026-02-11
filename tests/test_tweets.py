import json

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_tweets_route(client: AsyncClient):
    response = await client.get("/api/tweets", headers={"api-key": "test_1"})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data == {'result': True, 'tweets': [
        {'id': 1, 'content': 'First test text',
         'author': {'id': 1, 'name': 'Test User 1'},
         'likes': None,
         'attachments': []
         }
    ]
                             }


async def test_add_like(client: AsyncClient):
    request = await client.post("/api/tweets/1/likes",
                                headers={"api-key": "test_2"})
    assert request.status_code == 200
    response = await client.get("/api/tweets", headers={"api-key": "test_1"})
    response_data = response.json()
    assert response_data == {'result': True, 'tweets': [
        {'id': 1, 'content': 'First test text',
         'author': {'id': 1, 'name': 'Test User 1'},
         'likes': [{"user_id": 2, "name": "Test User 2"}],
         'attachments': []
         }
    ]
                             }


async def test_remove_like(client: AsyncClient):
    request = await client.delete("/api/tweets/1/likes",
                                  headers={"api-key": "test_2"})
    assert request.status_code == 200
    response = await client.get("/api/tweets", headers={"api-key": "test_1"})
    response_data = response.json()
    assert response_data == {'result': True, 'tweets': [
        {'id': 1, 'content': 'First test text',
         'author': {'id': 1, 'name': 'Test User 1'},
         'likes': [],
         'attachments': []
         }
    ]
                             }


async def test_add_tweet(client: AsyncClient):
    request = await client.post("/api/tweets", content=json.dumps(
        {"tweet_data": "Tweet for test 2", "tweet_media_ids": []}),
                                headers={"api-key": "test_2"})
    assert request.status_code == 200


async def test_delete_tweet(client: AsyncClient):
    request = await client.delete("/api/tweets/2",
                                  headers={"api-key": "test_2"})
    assert request.status_code == 200
