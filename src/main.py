from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

import src.catalogs.router
import src.exceptions
import src.products.router

app = FastAPI(title="Flip Catalog Parser")


@app.exception_handler(src.exceptions.AppBaseException)
async def app_exception_handler(request: Request, exception: src.exceptions.AppBaseException):
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.detail},
    )

api = APIRouter(prefix="/api")
api.include_router(src.catalogs.router.instance)
api.include_router(src.products.router.instance)
app.include_router(api)
