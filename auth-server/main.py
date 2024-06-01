import aioredis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_oauth2_redirect_html, get_swagger_ui_html
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth.router import auth_router, registration_router
from database.database import init_models

#from redis_creator.redis_creator import redis


app = FastAPI(title="APIServer", description="Swagger for API", docs_url=None, redoc_url=None)

app.include_router(auth_router)
app.include_router(registration_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(HTTPException)
async def unicorn_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "error": exc.detail},
    )


@app.on_event("startup")
async def startup():
    await init_models()
    redis = await aioredis.create_redis_pool('redis://79.174.80.94')
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
