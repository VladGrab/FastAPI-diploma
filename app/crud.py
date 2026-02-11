from sqlalchemy import select, func, cast, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import joinedload

from .models import User, Tweet, Media


async def get_curr_user(api_key: str, session):
    """
    Получение текущего пользователя
    """
    res = await session.execute(
        select(User).where(User.api_key == api_key))
    user = res.scalars().first()
    return user


async def get_user_by_id(id, session):
    """
    Получение пользователя по id
    """
    res = await session.execute(
        select(User).where(User.id == id))
    user = res.scalars().first()
    return user


async def get_tweets_crud(list_following_user, session):
    """
    Получение списка твитов
    """
    tweet_ex = select(Tweet).filter(
        Tweet.author_id.in_(list_following_user)).options(
        joinedload(Tweet.attachments)).order_by(
        func.cardinality(Tweet.likes).desc())
    tweet_data = await session.execute(tweet_ex)
    tweets = tweet_data.unique().scalars().all()
    return tweets


async def get_curr_tweet(id: int, session):
    """
    Получение твита по id
    """
    curr_tweet = await session.get(Tweet, id)
    return curr_tweet


async def delete_tweet_crud(session, tweet):
    """
    Удаление твита
    """
    await session.delete(tweet)
    await session.commit()


async def get_img_obj(session, id):
    """
    Получение пути до изображения
    """
    get_path_image = await (session
                            .execute(select(Media)
                                     .where(Media.tweet_id == id)))
    image_obj = get_path_image.scalars().first()
    return image_obj


async def following_user(session, api_key, r_dict, id, f_dict):
    """
    Подписка на пользователя
    """
    query = update(User).where(User.api_key == api_key).values(
        following=func.array_append(
            User.following, cast(r_dict, JSONB)
        ))
    await session.execute(query)
    query_second = update(User).where(User.id == id).values(
        followers=func.array_append(
            User.followers, cast(f_dict, JSONB)
        ))
    await session.execute(query_second)
    await session.commit()


async def delete_following_user(session, api_key, following_dict, id, followers_dict):
    """
    Отписка от пользователя
    """
    query = update(User).where(User.api_key == api_key).values(
        following=func.array_remove(
            User.following, cast(following_dict, JSONB)
        ))
    await session.execute(query)
    query_second = update(User).where(User.id == id).values(
        followers=func.array_remove(
            User.followers, cast(followers_dict, JSONB)
        ))
    await session.execute(query_second)
    await session.commit()


async def create_tweet_crud(session, tweet, author_json, current_user):
    """
    Создание нового твита
    """
    new_tweet = Tweet(content=tweet.tweet_data,
                      author_id=current_user.id,
                      author=author_json)
    session.add(new_tweet)
    await session.flush()
    tweet_id = Tweet.get_id(new_tweet)
    tweet_media_ids = tweet.tweet_media_ids
    if tweet_media_ids:
        update_tweet_execute = update(Tweet).where(Tweet.id == tweet_id).values(
            tweet_media_ids=func.array_append(
                Tweet.tweet_media_ids, tweet_media_ids[0])
        )
        await session.execute(update_tweet_execute)
        update_image_execute = (update(Media)
                                .where(Media.id == tweet.tweet_media_ids[0])
                                .values(tweet_id=tweet_id))
        await session.execute(update_image_execute)
    await session.commit()
    return tweet_id


async def add_image(session, path):
    """
    Добавление изображения к твиту
    """
    image_row = Media(path=path)
    session.add(image_row)
    await session.commit()
    media_id = Media.get_id(image_row)
    return media_id


async def add_like_crud(session, id, text_record):
    """
    Добавление лайка на твит
    """
    query = update(Tweet).where(Tweet.id == id).values(
        likes=func.array_append(
            Tweet.likes, cast(text_record, JSONB)
        ))
    await session.execute(query)
    await session.commit()


async def delete_like_crud(session, id, text_record):
    """
    Удаление лайка у твита
    """
    query = update(Tweet).where(Tweet.id == id).values(
        likes=func.array_remove(
            Tweet.likes, cast(text_record, JSONB)
        ))
    await session.execute(query)
    await session.commit()
