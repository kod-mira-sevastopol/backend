from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from src.exceptions import SuccessResponse
from src.jwt_handler import verify_token_and_check_role_hiring_manager_and_recruiter
from src.resumes.schemas import UploadResume, AddFavorite, DeleteFavorite
from src.resumes.service import upload_file, getResumeById, getMyResumes, deleteById, get_all_resumes_count, \
    addToFavorite, getMyFavorites, deleteFromFavorites

resumes_router = APIRouter(prefix="/resume", tags=["Resume"])


@resumes_router.post("/upload/{sender}", summary="Отправить файл резюме")
async def upload(sender: str,
                 file: UploadFile = File(...),
                 db: AsyncSession = Depends(get_session),
                 token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter)):
    #return SuccessResponse({"token": token})
    #raise HTTPException(403, "Ошибонька кайфовая")
    return await upload_file(db, token['id'], sender, file)


@resumes_router.get("/getById", summary="Вернуть резюме по id")
async def get_resume_by_id(resume_id: int, db: AsyncSession = Depends(get_session),
                           token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter)):

    return await getResumeById(db, resume_id, token['id'])


@resumes_router.get("/getMyResumes", summary="Вернуть мои резюме")
async def get_my_resumes(limit: int = 10, offset: int = 0,
                         token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter),
                         db: AsyncSession = Depends(get_session)):
    return await getMyResumes(db, token['id'], limit, offset)


@resumes_router.delete("/deleteById", summary="Удалить моё резюме")
async def delete_by_id(resume_id: int,
               token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter),
               db: AsyncSession = Depends(get_session)):
    return await deleteById(db, token['id'], resume_id)


@resumes_router.get("/getAllCount", summary="Получить общее количество резюме")
async def get_all_count(token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter),
               db: AsyncSession = Depends(get_session)):
    return await get_all_resumes_count(db)


@resumes_router.post("/addToFavorite", summary="Добавить в избранное")
async def add_to_favorite(data: AddFavorite, token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter),
                          db: AsyncSession = Depends(get_session)):
    return await addToFavorite(db, token['id'], data.resume_id)


@resumes_router.get("/favorites", summary="Получить мои избранные")
async def get_my_favorites(token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter),
                          db: AsyncSession = Depends(get_session)):
    return await getMyFavorites(db, token['id'])


@resumes_router.delete("/delete_favorite", summary="Удалить избранное")
async def delete_favorite(data: DeleteFavorite, db: AsyncSession = Depends(get_session),
                          token=Depends(verify_token_and_check_role_hiring_manager_and_recruiter)):
    return await deleteFromFavorites(db, token['id'], data.resume_id)

