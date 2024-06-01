from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from src.jwt_handler import verify_token_and_check_role_user
from src.subscribtions.schemas import AddSubscription

subscriptions_router = APIRouter()


@subscriptions_router.post("/addSubscription", summary="Добавляет подписку пользователю")
async def addSubscription(data: AddSubscription,
                          db: AsyncSession = Depends(get_session),
                          token=Depends(verify_token_and_check_role_user)):
    return await add_subscription(db, )
