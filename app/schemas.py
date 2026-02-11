from typing import Optional, List

from pydantic import BaseModel, NaiveDatetime, Field, ConfigDict, model_validator, field_validator
from sqlalchemy.dialects.postgresql import JSON


class CreateTweet(BaseModel):
    result: bool
    tweet_id: int


class BaseTweets(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[list[int]]
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class OutTweets(BaseModel):
    result: bool
    tweets: list[BaseTweets]


class BaseUser(BaseModel):
    id: int
    name: str


class BaseLikes(BaseModel):
    user_id: int
    name: str

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AllInfoTweet(BaseTweets):
    # created_at: NaiveDatetime
    likes: list
    author_id: int
    tweet_media_id: int

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: int
    name: str
    followers: list
    following: list


class UserMeInfo(BaseModel):
    result: bool
    user: UserInfo


class LoadImageSchema(BaseModel):
    id: int


class OutImageSchema(BaseModel):
    path: str

    model_config = ConfigDict(from_attributes=True)


class TweetGetSchema(BaseModel):
    id: int
    content: str
    author: BaseUser
    likes: Optional[List[BaseLikes]]
    attachments: List[str]

    @field_validator("attachments", mode="before")
    def serialize_images(cls, img_values: List[OutImageSchema]):
        if isinstance(img_values, list):
            return [img_value.path for img_value in img_values]
        return img_values

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TweetListSchema(BaseModel):
    result: bool
    tweets: List[TweetGetSchema]

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TrueResponse(BaseModel):
    result: bool
