import logging
import random
import string
from typing import TYPE_CHECKING
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    Response,
    HTMLResponse
)
from config import AUTH

if TYPE_CHECKING:
    from starlette.datastructures import UploadFile, MultiDict

logger = logging.getLogger(__name__)


async def upload_file(request: Request) -> JSONResponse:
    form: MultiDict = await request.form()
    file: UploadFile = form.get("image")

    try:
        if request.headers['secret'] != AUTH :
            Invalid = {
                "message":"Invalid authorization!"
            }

            return JSONResponse(Invalid, status_code=401)
    except KeyError:
        Invalid = {
                "message":"Invalid authorization!"
        }

        return JSONResponse(Invalid, status_code=401)

    if file is None:
        print("\033[91mReceived an upload request that has not given us a 'file' to upload\033[0m")
        content = {
            "message": "No 'file' given.\nPlease make sure File Form Name is ``image`` not ``Image``x"
        }
        return JSONResponse(content, status_code=400)

    name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(9))

    await file.seek(0)
    image = await file.read()
    mime = file.content_type

    await request.app.pool.execute("INSERT INTO images (name, image, mime) VALUES ($1, $2, $3)",  name, image, mime)
    file_ext = "png"
    if mime:
        file_ext = mime.split("/")[1]

    content = {
        "status": 200,
        "file_id": name,
        "file_ext": file_ext,
    }
    return JSONResponse(content, status_code=200)


async def get_image(request: Request) -> Response:
    file_name: str = request.path_params.get("name")
    try: 
        file_ext = f"image/{file_name.split('.')[1]}"
    except IndexError:
        return JSONResponse({"error":"No extension found! please make sure there's an extension like ``.png``!"}, status_code=404)
    file_id = file_name.split(".")[0]


    query = (
        f"SELECT image, mime FROM images WHERE name = $1 AND mime = $2"
    )   

    row = await request.app.pool.fetchrow(query, file_id, file_ext)
    try:
        image = row["image"]
        mime = row["mime"]
    except TypeError:
        return JSONResponse({"error":"No Image Found!"}, status_code=404)

  
    

    return Response(
        image,
        status_code=200,
        media_type=mime
    )