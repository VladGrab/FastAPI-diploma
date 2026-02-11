import asyncio
from typing import List

from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP, JSONB

from .database import engine  #
from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped


class Base(DeclarativeBase):
    pass


class Tweet(Base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id",
                                           ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(),
                        autoincrement=True)
    author = Column(JSONB)
    content = Column(String(1000), nullable=True)
    likes = Column(ARRAY(JSONB), nullable=True)
    tweet_media_ids = Column(ARRAY(Integer), nullable=True)
    attachments: Mapped[List["Media"]] = relationship("Media",
                                                      back_populates="tweet",
                                                      cascade="all, delete-orphan"
                                                      )

    def get_id(self):
        return self.id

    def __str__(self):
        return (self.id,
                self.author_id,
                self.created_at,
                self.author, self.content,
                self.likes,
                self.tweet_media_ids,
                self.attachments)

    def __repr__(self):
        return (
            f"Tweet(id={self.id}, tweet_text={self.content}, "
            f"created_at={self.created_at}, user_id={self.author_id}, "
            f"likes={self.likes}, attachments={self.attachments})"
        )


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String(255), nullable=False)
    tweet_id = Column(Integer, nullable=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=True)
    followers = Column(ARRAY(JSONB), nullable=True)
    following = Column(ARRAY(JSONB), nullable=True)

    def __repr__(self):
        return (f"id={self.id},"
                f"name={self.name},"
                f"followers={self.followers},"
                f"following={self.following}")

    def get_json_for_tweet(self):
        return {"id": self.id, "name": self.name}

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_followers(self):
        return self.followers

    def get_following(self):
        return self.following


class Media(Base):
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id",
                                          ondelete="CASCADE"))
    path = Column(String(255), nullable=False)
    tweet: Mapped["Tweet"] = relationship("Tweet",
                                          back_populates="attachments")

    def get_id(self):
        return self.id

    def __repr__(self):
        return self.path


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# asyncio.run(create_tables())
