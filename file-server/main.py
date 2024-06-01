import aioredis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from database.database import init_models
from files.router import router

#from redis_creator.redis_creator import redis


app = FastAPI(title="APIServer", description="Swagger for API")

app.include_router(router)

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
    redis = await aioredis.create_redis_pool('redis://localhost')
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
