from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.AbstractModel import query_fetchall, query_fetchone
from src.exceptions import SuccessResponse
from src.templates.models import Template, TemplateSkills, TemplateStacks
from src.templates.schemas import AddTemplate


async def getMyTemplates(db: AsyncSession, user_id: int):
    """
    Отдает все созданные шаблоны пользователя
    :param db:
    :param user_id:
    :return:
    """
    templates = await query_fetchall(db, select(Template)
                                     .where(Template.user_id == user_id).order_by(Template.id.desc()), False)

    return SuccessResponse({'templates': [await template[0].to_dict(skills=True, stacks=True) for template in templates]})


async def getById(db: AsyncSession, template_id: int, user_id: int):
    """
    Получить шаблон по id
    :param db:
    :param template_id:
    :param user_id:
    :return:
    """
    template = await query_fetchone(db, select(Template)
                                    .where(Template.user_id == user_id, Template.id == template_id)
                                    .limit(1), False)
    if template is False:
        raise HTTPException(404, "Не найден шаблон. Либо он создан не этим пользователем")

    return SuccessResponse({"template": await template.to_dict(skills=True)})


async def addTemplate(db: AsyncSession, user_id: int, data: AddTemplate):
    """
    Добавляет шаблон
    :param db:
    :param user_id:
    :param data:
    :return:
    """
    template = Template(user_id=user_id, name=data.name, experience_month=data.experience_month)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return SuccessResponse({"template": await template.to_dict(skills=True)})


async def addTemplateSkills(db: AsyncSession, template_id: int, skills: list):
    """
    Добавляет скилы к шаблону
    :param db:
    :param template_id:
    :param skills:
    :return:

    skills = [
        {
            "name": "test"
        },
        {
            "name": test
        }
    ]
    """
    result = []
    print(skills)
    for skill in skills:
        skill = TemplateSkills(template_id=template_id, name=skill['name'])
        db.add(skill)
        result.append(result)
    await db.commit()
    return result


async def addTemplateStacks(db: AsyncSession, template_id: int, stacks: list):
    result = []
    for stack in stacks:
        stack = TemplateStacks(template_id=template_id, name=stack['name'], type=stack['type'])
        db.add(stack)
        result.append(result)
    await db.commit()
    return result


async def bindInTemplates(db: AsyncSession, data: dict, template_id: int):
    """
    Привязывает всё к шаблону
    :param template_id:
    :param db:
    :param data:
    :return:
    """

    if 'skills' in data.keys():
        result = await addTemplateSkills(db, template_id, data['skills'])
    if 'stacks' in data.keys():
        result = await addTemplateSkills(db, template_id, data['stacks'])
    return SuccessResponse()


async def allSkills():
    """

    :return:
    """
    return SuccessResponse({"templates": [
        "ReactJS",
        "VueJS",
        "Angular",
        "Python",
        "FastAPI",
        "Java",
        "КОМПАС3D",
        "PHP",
        "C#"
    ]})
