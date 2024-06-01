from sqlalchemy import select, func, case, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.AbstractModel import query_fetchall, query_fetchone
from src.exceptions import SuccessResponse
from src.users.models import User, Score


async def users_me(db: AsyncSession, user_id: int):
    """
    Получает текущего пользователя
    :param db:
    :param user_id:
    :return:
    """
    user = await query_fetchone(db, select(User).where(User.id == user_id))
    return await user.to_dict()


async def users_all(db: AsyncSession):
    """
    Получить всех пользователей, не используется. Для теста
    :param db:
    :return:
    """
    users = await query_fetchall(db, select(User))
    return SuccessResponse({"users": [await user[0].to_dict() for user in users]})


async def get_scores_history(db: AsyncSession, user_id: int):
    """
    Получить историю зачислений баллов
    :param db:
    :param user_id:
    :return:
    """
    scores = await query_fetchall(db, select(Score).where(Score.user_id == user_id).order_by(Score.id.desc()), False)
    if scores is False:
        return SuccessResponse({"history": []})
    return SuccessResponse({"history": [await score[0].to_dict() for score in scores]})


async def get_count_scores(db: AsyncSession, user_id: int):
    """
    Получает количество баллов пользователя
    :param db:
    :param user_id:
    :return:
    """
    scores = await query_fetchall(db, select(Score).where(Score.user_id == user_id).order_by(Score.id.desc()), False)
    if scores is False:
        return SuccessResponse({"score": 0})

    result = 0
    for score in scores:
        if score[0].operation == 1:
            result += score[0].count
        else: result -= score[0].count

    return SuccessResponse({"score": result})


async def change_score(db: AsyncSession, user_id: int, operation: int, count: int, admin_id: int):
    """
    Меняет количество баллов пользователю
    :param db:
    :param user_id:
    :param operation:
    :param count:
    :param admin_id:
    :return:
    """
    score = Score(user_id=user_id, operation=operation, count=count, admin_id=admin_id)
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return SuccessResponse({"score": await score.to_dict()})


async def edit_name(db: AsyncSession, user_id: int, new_name: str):
    """
    Изменить имя пользователя
    :param db:
    :param user_id:
    :param new_name:
    :return:
    """
    upd = await db.execute(update(User).where(User.id == user_id).values(name=new_name))
    await db.commit()
    return SuccessResponse({"count": upd.rowcount})


async def edit_surname(db: AsyncSession, user_id: int, new_surname: str):
    """
    Изменить фамилию пользователя
    :param db:
    :param user_id:
    :param new_surname:
    :return:
    """
    upd = await db.execute(update(User).where(User.id == user_id).values(surname=new_surname))
    await db.commit()
    return SuccessResponse({"count": upd.rowcount})


async def edit_patronymic(db: AsyncSession, user_id: int, new_patronymic: str):
    """
    Изменить отчество пользователя
    :param db:
    :param user_id:
    :param new_patronymic:
    :return:
    """
    upd = await db.execute(update(User).where(User.id == user_id).values(patronymic=new_patronymic))
    await db.commit()
    return SuccessResponse({"count": upd.rowcount})