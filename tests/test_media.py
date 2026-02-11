import os

from httpx import AsyncClient

TEST_DIR = os.path.dirname(__file__)
image_path = f"{TEST_DIR}/img_for_tests/test.png"
image = open(image_path, "rb")


async def test_download_media(client: AsyncClient):
    request = await client.post("/api/medias",
                                files={"file": image},
                                headers={"api-key": "test_1"}
                                )
    assert request.status_code == 200
    response = request.json()
    assert response == {"result": True, "media_id": 1}
