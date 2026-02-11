import datetime

from sqlalchemy.dialects.postgresql import insert

from app.models import Tweet, User

USER_ID = "user_id"

user_test = [
    {"api_key": "test_1",
     "name": "Test User 1",
     "followers": [],
     "following": []
     },
    {"api_key": "test_2",
     "name": "Test User 2",
     "followers": [],
     "following": []
     }
]

tweet_data = {"content": "First test text",
              "author": {"id": 1, "name": "Test User 1"},
              "author_id": 1,
              "created_at": datetime.datetime.now()}


async def insert_data(conn):
    await conn.execute(insert(User), user_test)
    await conn.execute(insert(Tweet), tweet_data)
