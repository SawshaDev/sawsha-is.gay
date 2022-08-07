from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import asyncpg
from views import upload_file, get_image


routes = [
    Route(
        "/upload",
        upload_file,
        methods=["POST"]
    ),
    Route(
        '/' + r"{name:str}",
        get_image,
    ),
]

app = Starlette(debug=True, routes=routes)


@app.on_event("startup")
async def on_startup():
    app.pool = await asyncpg.connect(dsn="postgres://skye:GRwe2h2ATA5qrmpa@db:5432/uploader")