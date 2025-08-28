import fastapi
import src.catalogs.router
import src.products.router

app = fastapi.FastAPI(title="Flip Catalog Parser")
api = fastapi.APIRouter(prefix="/api")
api.include_router(src.catalogs.router.instance)
api.include_router(src.products.router.instance)
app.include_router(api)
