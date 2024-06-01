import datetime
import hashlib
import os
import shutil

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse

from exceptions import SuccessResponse
from files.models import File
from files.utils import sizes


def file_size_is_true(file_size: int, file_type: str):
    """
    Проверяет размер файла на валидность
    :param file_size:
    :param file_type:
    :return:
    """
    if file_size <= sizes[file_type]:
        return True
    return False


def hash_filename(filename: str):
    """
    Хешируем файл
    :param filename:
    :return:
    """
    hash_object = hashlib.sha256()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    filename = filename + current_time
    byte_string = filename.encode('utf-8')
    hash_object.update(byte_string)
    hashed_string = hash_object.hexdigest()
    return hashed_string


async def save_file(hash: str, obj: UploadFile, where: str):
    """
    Сохраняем файл в директорию
    :param hash:
    :param obj:
    :param where:
    :return:
    """
    file_path = os.path.join(f"data/{where}", hash)
    with open(file_path, "wb") as file:
        shutil.copyfileobj(obj.file, file)
    return hash


async def save_file_db(db: AsyncSession, obj: UploadFile, hash: str, user_id: int, file_type: str):
    """
    Сохраняет данные в БД
    :param db:
    :param obj:
    :param hash:
    :param user_id:
    :param file_type:
    :return: File
    """
    file = File(filename=obj.filename, hash_name=hash, user_id=user_id, file_type=file_type)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


async def upload_photo(db: AsyncSession, photo: UploadFile, user_id: int, host: str):
    """
    Загрузка фотографии
    :param db:
    :param photo:
    :param user_id:
    :return:
    """
    if not file_size_is_true(photo.size, "photos"):
        raise HTTPException(403, "Размер файла превышен")
    extension = photo.filename.split(".")[-1]
    hash = hash_filename(photo.filename + str(user_id) + "photo") + "." + extension
    await save_file(hash, photo, "photos")
    file = await save_file_db(db, photo, hash, user_id, "photo")
    return SuccessResponse({
        "file": "http://" + host + "/photos/" + file.hash_name
    })


async def get_photo(db: AsyncSession, hash: str):
    """
    Получает фотографию по хешу
    :param db:
    :param hash:
    :return:
    """
    photo_path = os.path.join("data", "photos", hash)
    if os.path.exists(photo_path):
        return FileResponse(photo_path)
    raise HTTPException(404, "Фотографии нет")


async def upload_video(db: AsyncSession, video: UploadFile, user_id: int, host: str):
    """
    Загрузка видео
    :param db:
    :param video:
    :param user_id:
    :return:
    """
    if not file_size_is_true(video.size, "videos"):
        raise HTTPException(403, "Размер файла превышен")
    extension = video.filename.split(".")[-1]
    hash = hash_filename(video.filename + str(user_id) + "video") + "." + extension
    await save_file(hash, video, "videos")
    file = await save_file_db(db, video, hash, user_id, "video")
    return SuccessResponse({
        "file": "http://" + host + "/videos/" + file.hash_name
    })


async def get_video(db: AsyncSession, hash: str):
    """
    Получает видео по хешу
    :param db:
    :param hash:
    :return:
    """
    video_path = os.path.join("data", "videos", hash)
    if os.path.exists(video_path):
        return FileResponse(video_path)
    raise HTTPException(404, "Видео нет")


async def upload_file(db: AsyncSession, file: UploadFile, user_id: int, host: str):
    """
    Загрузка file
    :param db:
    :param video:
    :param user_id:
    :return:
    """
    if not file_size_is_true(file.size, "files"):
        raise HTTPException(403, "Размер файла превышен")
    extension = file.filename.split(".")[-1]
    hash = hash_filename(file.filename + str(user_id) + "video") + "." + extension
    await save_file(hash, file, "files")
    file = await save_file_db(db, file, hash, user_id, "file")
    return SuccessResponse({
        "file": "http://" + host + "/files/" + file.hash_name
    })


async def get_file(db: AsyncSession, hash: str):
    """
    Получает видео по хешу
    :param db:
    :param hash:
    :return:
    """
    file_path = os.path.join("data", "files", hash)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(404, "Файла нет")