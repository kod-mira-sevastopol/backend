import time

from fastapi import APIRouter, UploadFile, File, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_cache import FastAPICache
from starlette.responses import FileResponse

from database.database import get_session
from files.service import upload_photo, get_photo, upload_video, get_video, upload_file, get_file
from jwt_handler import verify_jwt_token, verify_token_and_check_role_all
from fastapi_cache.decorator import cache

router = APIRouter()


@router.post("/photos/upload")
async def photos_upload(request: Request,
                        photo: UploadFile = File(...),
                        token: HTTPAuthorizationCredentials = Depends(verify_token_and_check_role_all),
                        db=Depends(get_session)):
    return await upload_photo(db, photo, token['id'], request.headers['host'])


@router.get("/photos/{hash}")
@cache(expire=31536000)
async def photos_get(hash: str, db=Depends(get_session)):
    return await get_photo(db, hash)


@router.post("/videos/upload")
async def videos_upload(request: Request,
                        video: UploadFile = File(...),
                        token: HTTPAuthorizationCredentials = Depends(verify_token_and_check_role_all),
                        db=Depends(get_session)):
    return await upload_video(db, video, token['id'], request.headers['host'])


@router.get("/videos/{hash}")
@cache(expire=31536000)
async def photos_get(hash: str, db=Depends(get_session)):
    return await get_video(db, hash)


@router.post("/files/upload")
async def videos_upload(request: Request,
                        file: UploadFile = File(...),
                        token: HTTPAuthorizationCredentials = Depends(verify_token_and_check_role_all),
                        db=Depends(get_session)):
    return await upload_file(db, file, token['id'], request.headers['host'])


@router.get("/files/{hash}")
@cache(expire=31536000)
async def files_get(hash: str, db=Depends(get_session)):
    return await get_file(db, hash)