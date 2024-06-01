from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from src.jwt_handler import verify_token_and_check_role_hiring_manager_and_recruiter, \
    verify_token_and_check_role_hiring_manager_and_resource_manager
from src.templates.schemas import AddTemplate, BindTemplateParameters
from src.templates.service import getMyTemplates, getById, addTemplate, allSkills, bindInTemplates

templates_router = APIRouter(prefix="/templates")


@templates_router.get("/getMyTemplates", summary="Получить мои шаблоны", tags=["Templates"])
async def get_my_templates(token=Depends(verify_token_and_check_role_hiring_manager_and_resource_manager),
                           db: AsyncSession = Depends(get_session)):
    return await getMyTemplates(db, token['id'])


@templates_router.get("/getById", summary="Получает шаблон по id", tags=['Templates'])
async def get_by_id(template_id: int,
                    token=Depends(verify_token_and_check_role_hiring_manager_and_resource_manager),
                    db: AsyncSession = Depends(get_session)):
    return await getById(db, template_id, token['id'])


@templates_router.post("/create", summary="Создает шаблон", tags=['Templates'])
async def add_template(data: AddTemplate, token=Depends(verify_token_and_check_role_hiring_manager_and_resource_manager),
                    db: AsyncSession = Depends(get_session)):
    return await addTemplate(db, token['id'], data)


@templates_router.post("/bindParameters", summary="Привязать параметры к шаблону", tags=['Templates'])
async def bind_parameters(data: BindTemplateParameters, token=Depends(verify_token_and_check_role_hiring_manager_and_resource_manager),
                    db: AsyncSession = Depends(get_session)):
    return await bindInTemplates(db, data.data, data.template_id)


@templates_router.get("/getAllSkills", tags=['Templates'])
async def get_all_skills():
    return await allSkills()



