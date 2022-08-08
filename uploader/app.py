from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import asyncpg
from views import upload_file, get_image
from config import POSTGRES_DSN


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
    app.pool = await asyncpg.connect(POSTGRES_DSN)