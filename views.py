import random
import string
from typing import TYPE_CHECKING
from starlette.requests import Request
from starlette.responses import (
    JSONResponse,
    Response,
    HTMLResponse
)

if TYPE_CHECKING:
    from starlette.datastructures import UploadFile, MultiDict


async def upload_file(request: Request) -> JSONResponse:
    form: MultiDict = await request.form()
    file: UploadFile = form.get("image")

    if file is None:
        print("\033[91mReceived an upload request that has not given us a 'file' to upload\033[0m")
        content = {
            "message": "No 'file' given."
        }
        return JSONResponse(content, status_code=400)

    name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(9))

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
        "file_ext": file_ext
    }
    return JSONResponse(content, status_code=200)


async def get_image(request: Request) -> Response:
    file_id: str = request.path_params.get("name")
    file_id = file_id.split(".")[0]

    query = (
        f"SELECT image, mime FROM images WHERE name = $1"
    )   

    row = await request.app.pool.fetchrow(query, file_id)
    image = row["image"]
    mime = row["mime"]

    if image is None:
        return Response(None, status_code=404)

    return Response(
        image,
        status_code=200,
        media_type=mime
    ) 