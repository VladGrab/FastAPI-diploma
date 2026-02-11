import json
import os

from fastapi.exceptions import ResponseValidationError
from sqlalchemy.orm import Session
from starlette.responses import FileResponse, PlainTextResponse
import uvicorn

from .crud import get_curr_user, get_tweets_crud, get_curr_tweet, get_img_obj, delete_tweet_crud, get_user_by_id, \
    following_user, delete_following_user, create_tweet_crud, add_image, add_like_crud, delete_like_crud
from .models import User, Tweet, Media  #
from .schemas import (BaseTweets, UserMeInfo,
                      TweetListSchema, CreateTweet,
                      TrueResponse)  #
from .database import get_async_session  #
from .utils import (write_file_image_to_disk,
                    delete_file_from_disk,
                    send_error_message)
from fastapi import (FastAPI, File, UploadFile,
                     Header, Depends,
                     HTTPException)

# import logging

BASE_URL = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
path_from_images = f"{BASE_URL}/static/media/"

# templates = Jinja2Templates(directory=f"{BASE_URL}/static/")

# logger = logging.getLogger(__name__)
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.INFO
# )

app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request, exc):
    error_dict = exc.errors()[0]
    raw_response = {"result": False,
                    "error_type": error_dict["type"],
                    "error_message": error_dict["msg"]}
    return PlainTextResponse(str(raw_response), status_code=400)


@app.get("/api/users/me", response_model=UserMeInfo)
async def me_user(session: Session = Depends(get_async_session),
                  api_key: str = Header(None, alias="api-key")):
    user = await get_curr_user(api_key=api_key, session=session)
    if user is None:
        raise HTTPException(status_code=404,
                            detail=send_error_message(
                                error_type='404 Not Found',
                                error_message=f"User with api-key"
                                              f" '{api_key}' not found")
                            )
    return {"result": "true",
            "user": user}


@app.get("/api/tweets", response_model=TweetListSchema)
async def get_tweets(session: Session = Depends(get_async_session),
                     api_key: str = Header(None, alias="api-key")):
    curr_user = await get_curr_user(api_key=api_key, session=session)
    list_following_user = [user["id"] for user in curr_user.following]
    list_following_user.append(curr_user.id)
    tweets = await get_tweets_crud(list_following_user=list_following_user,
                                   session=session)
    response_dict = {"result": "true",
                     "tweets": tweets}
    return response_dict


@app.delete("/api/tweets/{id}", response_model=TrueResponse)
async def delete_tweet(id: int, session: Session = Depends(get_async_session),
                       api_key: str = Header(None, alias="api-key")):
    current_user = await get_curr_user(api_key=api_key, session=session)
    tweet_for_delete = await get_curr_tweet(id, session)
    if tweet_for_delete.author_id != current_user.id:
        raise HTTPException(status_code=403,
                            detail=send_error_message(
                                error_type='403 Forbidden',
                                error_message=f"User {current_user.name} does not have "
                                              f"the right to delete someone else's tweet."))
    image_obj = await get_img_obj(session, id=tweet_for_delete.id)
    if image_obj is not None:
        delete_file_from_disk(image_obj.path)
    await delete_tweet_crud(session, tweet_for_delete)
    return {"result": "true"}


@app.get("/app/static/media/{name}")
async def get_image(name):
    file_path = f"{path_from_images}/{name}"
    return FileResponse(file_path)


@app.get("/api/users/{id}", response_model=UserMeInfo)
async def add_user(id: int, session: Session = Depends(get_async_session)):
    user = await get_user_by_id(id, session)
    if user is None:
        raise HTTPException(status_code=404,
                            detail=send_error_message(
                                error_type='404 Not Found',
                                error_message=f"User {id} not found")
                            )
    return {"result": "true",
            "user": user}


@app.post("/api/users/{id}/follow", response_model=TrueResponse)
async def add_user_fl(id: int, session: Session = Depends(get_async_session),
                      api_key: str = Header(None, alias="api-key")) -> dict:
    current_user = await get_curr_user(api_key=api_key, session=session)
    second_user = await get_user_by_id(id, session)
    r_dict = {'id': id, 'name': second_user.name}
    f_dict = {'id': current_user.id, 'name': current_user.name}
    await following_user(session, api_key, r_dict, id, f_dict)
    return {"result": True}


@app.delete("/api/users/{id}/follow", response_model=TrueResponse)
async def delete_user_fl(id: int, session: Session = Depends(get_async_session),
                         api_key: str = Header(None, alias="api-key")) -> dict:
    current_user = await get_curr_user(api_key=api_key, session=session)
    second_user = await get_user_by_id(id, session)
    following_dict = {'id': id, 'name': second_user.name}
    followers_dict = {'id': current_user.id, 'name': current_user.name}
    await delete_following_user(session, api_key, following_dict, id, followers_dict)
    return {"result": True}


@app.post("/api/tweets", response_model=CreateTweet)
async def create_tweet(tweet: BaseTweets,
                       session: Session = Depends(get_async_session),
                       api_key: str = Header(None, alias="api-key")) -> dict:
    current_user = await get_curr_user(api_key=api_key, session=session)
    author_json = User.get_json_for_tweet(current_user)
    tweet_id = await create_tweet_crud(session, tweet, author_json, current_user)
    return {
        "result": True,
        "tweet_id": tweet_id
    }


@app.post("/api/medias")
async def load_image(file: UploadFile = File(...),
                     session: Session = Depends(get_async_session)):
    file_path = os.path.join(path_from_images, file.filename)
    path = await write_file_image_to_disk(file_path, file)
    media_id = await add_image(session, path)
    return {
        "result": True,
        "media_id": media_id
    }


@app.post("/api/tweets/{id}/likes", response_model=TrueResponse)
async def add_like(id: int, session: Session = Depends(get_async_session),
                   api_key: str = Header(None, alias="api-key")):
    user = await get_curr_user(api_key=api_key, session=session)
    text_record = {"user_id": user.id, "name": user.name}
    await add_like_crud(session, id, text_record)
    return {"result": "true"}


@app.delete("/api/tweets/{id}/likes", response_model=TrueResponse)
async def delete_like(id: int, session: Session = Depends(get_async_session),
                      api_key: str = Header(None, alias="api-key")):
    user = await get_curr_user(api_key=api_key, session=session)
    text_record = {"user_id": user.id, "name": user.name}
    await delete_like_crud(session, id, text_record)
    return {"result": "true"}


# app.mount("/",
#           StaticFiles(directory=f"{BASE_URL}/static", html=True),
#           name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
