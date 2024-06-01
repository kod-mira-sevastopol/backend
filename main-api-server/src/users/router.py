from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from src.jwt_handler import verify_token_and_check_role_user, verify_token_and_check_role_admin, \
    verify_token_and_check_role_all
from src.users.schemas import EditScore, EditSelfScore, EditUserName, EditUserSurname, EditUserPatronymic
from src.users.service import *

users_router = APIRouter(prefix="/users")
scores_router = APIRouter(prefix="/score")


@users_router.get("/me", summary="Получить текущего пользователя", description="", tags=["Users", "Admin"])
async def usersMe(db: AsyncSession = Depends(get_session),
                  token=Depends(verify_token_and_check_role_all)):
    return await users_me(db, token['id'])


@users_router.get("/all", summary="Получить всех пользователей", description="", tags=["Admin"])
async def getAll(db: AsyncSession = Depends(get_session),
                 token=Depends(verify_token_and_check_role_admin)):
    return await users_all(db)


@scores_router.get("/history/me", summary="Получить свою историю зачисления баллов", tags=["Users", "Scores"])
async def getMyScoresHistory(db: AsyncSession = Depends(get_session),
                             token=Depends(verify_token_and_check_role_user)):
    return await get_scores_history(db, token['id'])


@scores_router.get("/history/{user_id}", summary="Получить историю зачисления баллов пользователя", tags=["Admin"])
async def getUserHistory(user_id: int,
                         db: AsyncSession = Depends(get_session),
                         token=Depends(verify_token_and_check_role_admin)):
    return await get_scores_history(db, user_id)


@scores_router.get("/me", summary="Получить свое количество очков", tags=["Users", "Scores"])
async def getMyScoreCount(db: AsyncSession = Depends(get_session),
                          token=Depends(verify_token_and_check_role_user)):
    return await get_count_scores(db, token['id'])


@scores_router.get("/{user_id}", summary="Получить количество очков пользователя", tags=["Admin"])
async def getMyScoreCount(user_id: int,
                          db: AsyncSession = Depends(get_session),
                          token=Depends(verify_token_and_check_role_admin)):
    return await get_count_scores(db, user_id)


@scores_router.post("/add", summary="Добавить баллов пользователю", tags=["Admin"])
async def addScores(data: EditScore,
                    db: AsyncSession = Depends(get_session),
                    token=Depends(verify_token_and_check_role_admin)):
    return await change_score(db, data.user_id, 1, data.count, admin_id=token['id'])


@scores_router.post("/subtract", summary="Вычесть баллы пользователя", tags=["Admin"])
async def addScores(data: EditScore,
                    db: AsyncSession = Depends(get_session),
                    token=Depends(verify_token_and_check_role_admin)):
    return await change_score(db, data.user_id, 0, data.count, admin_id=token['id'])


@scores_router.post("/add", summary="Добавить баллов себе", tags=["Users"])
async def addScores(data: EditSelfScore,
                    db: AsyncSession = Depends(get_session),
                    token=Depends(verify_token_and_check_role_user)):
    return await change_score(db, token['id'], 1, data.count, admin_id=token['id'])


@scores_router.post("/subtract", summary="Вычесть баллы пользователя", tags=["Users"])
async def addScores(data: EditSelfScore,
                    db: AsyncSession = Depends(get_session),
                    token=Depends(verify_token_and_check_role_user)):
    return await change_score(db, token['id'], 0, data.count, admin_id=token['id'])


@users_router.patch("/edit/name", summary="Изменить имя юзера", tags=["Users", "Изменение данных пользователя"])
async def editName(data: EditUserName,
                   db: AsyncSession = Depends(get_session),
                   token=Depends(verify_token_and_check_role_user)):
    return await edit_name(db, token['id'], data.name)


@users_router.patch("/edit/surname", summary="Изменить фамилию пользователя", tags=["Users", "Изменение данных пользователя"])
async def editName(data: EditUserSurname,
                   db: AsyncSession = Depends(get_session),
                   token=Depends(verify_token_and_check_role_user)):
    return await edit_surname(db, token['id'], data.surname)


@users_router.patch("/edit/patronymic", summary="Изменить отчество пользователя", tags=["Users", "Изменение данных пользователя"])
async def editName(data: EditUserPatronymic,
                   db: AsyncSession = Depends(get_session),
                   token=Depends(verify_token_and_check_role_user)):
    return await edit_patronymic(db, token['id'], data.patronymic)



