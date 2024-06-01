import aioredis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from database.database import init_models
from src.resumes.router import resumes_router
from src.templates.router import templates_router
from src.users.router import users_router, scores_router

#from redis_creator.redis_creator import redis


app = FastAPI(title="APIServer", description="Swagger for MainAPI"
                                             "<br/>"
                                             "<h5>токен <div>user_id=5, role=recruiter:</div><span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwicm9sZSI6InJlY3J1aXRlciIsImV4cCI6MTc0ODU5NzE1MX0.r1N4BSrH3lR_HyYksMgbRUb4ebs_layfPG0IkTDMx8A</span></h5>"
                                             "<br><br>"
                                             "<h5>токен <div>user_id=5, role=hiring_manager:</div><span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwicm9sZSI6ImhpcmluZ19tYW5hZ2VyIiwiZXhwIjoxNzQ4NTk3MTUxfQ.YFxqd6KQ8-LRs_zqGytTjLFUKw5HXwzjaXxi3GnmFA0</span></h5>"
                                             "<br><br>"
                                             "<h5>токен <div>user_id=5, role=resource_manager:</div><span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwicm9sZSI6InJlc291cmNlX21hbmFnZXIiLCJleHAiOjE3NDg1OTcxNTF9.xLWEHSQXwhuV6GDjQLCHcxr_i8rtgLIBOQYCYOLUh0M</span></h5>"
                                             "<br><br>"
                                             "<h5>токен <div>user_id=5, role=recruiter:</div><span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwicm9sZSI6InJlY3J1aXRlciIsImV4cCI6MTc0ODc2NDAzNn0.57Lee7n4j-ylxQRCdWbLt2Z15TLyonroQ_a0LVP8dWg</span></h5>"
                                             "<br><br>"
                                             "<h5>токен <div>user_id=5, role=resource_manager:</div><span>eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwicm9sZSI6ImhpcmluZ19tYW5hZ2VyIiwiZXhwIjoxNzQ4NzY0MTUzfQ.oh_D9Dqh96WOqpQgN7IccQdSQ-Cv_-SEJJV9IWZzfBw</span></h5>"
                                             "", docs_url=None, redoc_url=None)

app.include_router(users_router)
app.include_router(scores_router)
app.include_router(resumes_router)
app.include_router(templates_router)


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
    uvicorn.run(app, host="0.0.0.0", port=8001)
