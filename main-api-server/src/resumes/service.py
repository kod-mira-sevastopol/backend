import json
import os
import zipfile
from datetime import datetime

import requests
from fastapi import UploadFile, File, Depends, HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy import select, delete, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_session
from src.AbstractModel import query_fetchone, query_fetchall
from src.exceptions import SuccessResponse
from src.mail.send import send_to_resumer
from src.resumes.models import InputResume, Education, Company, Stack, Achievement, ResumeData, Favorite, Skill
from src.resumes.schemas import UploadResume


async def send_file(file_path: str, url: str):
    """Отправляет файл на указанный URL в теле запроса"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in (".pdf", ".docx", ".rtf", ".zip"):
            with open(file_path, "rb") as file:
                response = requests.post(url, files={"file": file})
            if response.status_code == 200:
                response_data = json.loads(response.text)
                return response_data
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
        else:
            print(f"Файл {file_path} с расширением {file_extension} игнорируется.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def save_files_in_db(db: AsyncSession, filename: str, sender: str, user_id: int) -> InputResume:
    """
    Сохраняет входной файл в базу данных
    :param db:
    :param filename:
    :param sender:
    :param user_id:
    :return:
    """
    file = InputResume(file_name=filename, sender=sender, user_id=user_id)
    db.add(file)
    await db.commit()
    await db.refresh(file)
    return file


async def addEducation(db: AsyncSession, start_year: int = None, end_year: int = None,
                       name: str = None, tier: str = None, resume_id: int = None, department_name: str = None):
    """
    Добавляет университет
    :param db:
    :param start_year:
    :param end_year:
    :param name:
    :param tier:
    :param resume_id:
    :param department_name:
    :return:
    """
    start_year = int(start_year)
    end_year = int(end_year)
    education = Education(start_year=start_year, end_year=end_year, name=name,
                          tier=tier, resume_id=resume_id, department_name=department_name)
    db.add(education)
    await db.commit()
    await db.refresh(education)
    return education


async def addCompany(db: AsyncSession, name: str, resume_id: int, start_date: str,
                     end_date: str, job_description: str,
                     job_location: str):
    """
    Добавляет компанию к резюме
    :param db:
    :param name:
    :param resume_id:
    :param start_date:
    :param end_date:
    :param job_description:
    :param job_location:
    :return:
    """
    # if start_date.count("-") == 1:
    #     start_date += "-01"
    # if end_date.count("-"):
    #     end_date += "-01"
    # if end_date == '':
    #     end_date = None
    # if start_date is not None:
    #     start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    # else: start_date_obj = None
    # if end_date is not None:
    #     end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    # else: end_date_obj = None
    company = Company(name=name, resume_id=resume_id, start_date=start_date,
                      end_date=end_date, job_description=job_description, job_location=job_location)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


async def addStack(db: AsyncSession, stack: str, resume_id: int):
    """
    Добавляет стек к резюме
    :param db:
    :param stack:
    :param resume_id:
    :return:
    """
    stack = Stack(stack=stack, resume_id=resume_id)
    db.add(stack)
    await db.commit()
    await db.refresh(stack)
    return stack


async def addAchievement(db: AsyncSession, description: str, resume_id: int):
    """
    Добавить ачивмент к резюме
    :param db:
    :param description:
    :param resume_id:
    :return:
    """
    achievement = Achievement(description=description, resume_id=resume_id)
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    return achievement


async def addSkill(db: AsyncSession,
                   resume_id: int, name: str, type: str):
    """
    Добавляет качества человечку
    :param db:
    :param resume_id:
    :param name:
    :param type:
    :return:
    """

    skill = Skill(resume_id=resume_id, name=name, type=type)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


async def addResume(db: AsyncSession,
                    input_id: int, first_name: str = None,
                    last_name: str = None, middle_name: str = None,
                    age: str = None, email: str = None,
                    phone_number: str = None, telegram: str = None,
                    hh_url: str = None, birth_date: str = None, degree: str = None,
                    experience: str = None, position: str = None):
    """

    :param position:
    :param experience:
    :param degree:
    :param db:
    :param input_id:
    :param first_name:
    :param last_name:
    :param middle_name:
    :param age:
    :param email:
    :param phone_number:
    :param telegram:
    :param hh_url:
    :param birth_date:
    :return:
    """
    #if birth_date:
    #birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

    age = str(age)
    degree = str(degree)
    experience = str(experience)
    position = str(position)

    resume_data = ResumeData(resume_id=input_id, first_name=first_name,
                             last_name=last_name, middle_name=middle_name,
                             age=age, email=email, phone_number=phone_number,
                             telegram=telegram, hh_url=hh_url, birth_date=birth_date, degree=degree,
                             experience=experience, position=position)
    db.add(resume_data)
    await db.commit()
    await db.refresh(resume_data)
    return resume_data


async def upload_file(db: AsyncSession,
                      user_id: int,
                      sender: str,
                      file: UploadFile = File(...)):
    file_location = f"files/{file.filename}"
    result = []
    if not file.filename.endswith((".pdf", ".docx", ".zip", ".rtf")):
        return SuccessResponse({"result": result})
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        url = "http://192.168.137.103:8080/resume/scrab"
        if file.filename.endswith(".zip"):
            if zipfile.is_zipfile(file_location):
                with zipfile.ZipFile(file_location) as zip_file:
                    for file_info in zip_file.infolist():
                        if not file_info.is_dir():
                            extract_path = os.path.join("files", file_info.filename)
                            zip_file.extract(file_info, "files/")
                            if not file_info.filename.endswith(".pdf") and not file_info.filename.endswith(
                                    ".docx") and not file_info.filename.endswith(".rtf"):
                                continue
                            try:
                                model_answer = await send_file(extract_path, f"{url}")
                                if model_answer is None:
                                    continue
                                if 'result' in model_answer.keys():
                                    continue
                                #result.append(model_answer)
                            except Exception as E:
                                continue
                            new_file = await save_files_in_db(db, file_info.filename, sender, user_id)
                            person = model_answer['person']
                            contact = model_answer['contact']
                            resume = await addResume(db, new_file.id, person['first_name'], person['last_name'],
                                                     person['middle_name'], person['age'], contact['email'],
                                                     contact['phone_number'], contact['telegram'],
                                                     model_answer['hh-url'],
                                                     person['birth_date'], model_answer['stats']['degree'],
                                                     model_answer['stats']['experience'],
                                                     model_answer['stats']['position'])
                            for ach in model_answer['achievements']:
                                await addAchievement(db, ach['description'], resume.id)

                            for job in model_answer['jobs']:
                                await addCompany(db, job['job_company'], resume.id,
                                                 job['start_date'], job['end_date'],
                                                 job['job_description'], job['job_location'])

                            # for education in model_answer['education']:
                            #     new_education = await addEducation(db, education['start_year'], education['end_year'],
                            #                                        education['name'], education['tier'],
                            #                                        resume.id, education['department_name'][0]) ##### КОСТЫЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
                            for stack in model_answer['stack']:
                                new_stack = await addStack(db, stack['stack'], resume.id)

                            for skill in model_answer['skills']:
                                await addSkill(db, resume.id, skill['name'], skill['type'])

                            await db.refresh(resume)
                            result.append([await resume.to_dict(educations=True, stacks=True,
                                                                companies=True, achievements=True,
                                                                skills=True)])
                    return SuccessResponse({"response": result})
                #return {"message": "Файлы из архива успешно отправлены"}
        else:
            print(file_location)
            message_dict = dict()
            if file_location.endswith(".pdf") or file_location.endswith(".docx") or file_location.endswith(".rtf"):
                model_answer = await send_file(file_location, f"{url}")
                if model_answer is None:
                    raise HTTPException(403, "Сервер недостаточно точно распознал резюме")
                if 'result' in model_answer.keys():
                    raise HTTPException(403, "Документ не может быть разобран")
                result.append(model_answer)
                print(model_answer)
                new_file = await save_files_in_db(db, file.filename, sender, user_id)
                person = model_answer['person']
                contact = model_answer['contact']
                resume = await addResume(db, new_file.id, person['first_name'], person['last_name'],
                                         person['middle_name'], person['age'], contact['email'],
                                         contact['phone_number'], contact['telegram'], model_answer['hh-url'],
                                         person['birth_date'], model_answer['stats']['degree'],
                                         model_answer['stats']['experience'], model_answer['stats']['position'])
                message_dict['experience'] = model_answer['stats']['experience']
                message_dict['position'] = model_answer['stats']['position']
                message_dict['degree'] = model_answer['stats']['degree']
                #await send_to_resumer(message_dict)
                for ach in model_answer['achievements']:
                    await addAchievement(db, ach['description'], resume.id)

                for job in model_answer['jobs']:
                    await addCompany(db, job['job_company'], resume.id,
                                     job['start_date'], job['end_date'],
                                     job['job_description'], job['job_location'])

                #for education in model_answer['education']:
                #new_education = await addEducation(db, education['start_year'], education['end_year'],
                #education['name'], education['tier'],
                #resume.id, education['department_name'][0])  ##### КОСТЫЛЬ!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
                for stack in model_answer['stack']:
                    new_stack = await addStack(db, stack['stack'], resume.id)

                for skill in model_answer['skills']:
                    await addSkill(db, resume.id, skill['name'], skill['type'])

                await db.refresh(resume)
                return SuccessResponse({"response": await resume.to_dict(educations=True, stacks=True,
                                                                         companies=True, achievements=True,
                                                                         skills=True)})
            else:
                raise HTTPException(403, "Файл не .pdf/.docx/.rtf")
            #return {"message": "Файл успешно отправлен"}
        return SuccessResponse({"result": result})
    except Exception as e:
        raise HTTPException(403, f"Не удалось сохранить или отправить файл: {str(e)}")


@cache(expire=60 * 100)
async def getResumeById(db: AsyncSession, resume_id: int, user_id: int):
    """
    Получает резюме пользователя
    :param db:
    :param resume_id:
    :param user_id:
    :return:
    """
    resume = await query_fetchone(db, select(ResumeData)
                                  .join(InputResume).filter(InputResume.id == ResumeData.resume_id)
                                  .where(InputResume.user_id == user_id, ResumeData.id == resume_id))
    return SuccessResponse({"resume": await resume.to_dict(educations=True, stacks=True, companies=True,
                                                           achievements=True, skills=True)})


async def getMyResumes(db: AsyncSession, user_id: int, limit: int, offset: int):
    """
    Получает все мои резюме
    :param db:
    :param user_id:
    :param limit:
    :param offset:
    :return:
    """
    resumes = await query_fetchall(db, select(ResumeData)
                                   .join(InputResume).filter(InputResume.id == ResumeData.resume_id)
                                   .where(InputResume.user_id == user_id)
                                   .limit(limit).offset(offset).order_by(ResumeData.id.desc()))
    print(resumes)
    return SuccessResponse({"resumes": [
        await resume[0].to_dict(educations=True, stacks=True, companies=True, achievements=True, skills=True) for resume
        in resumes]})


async def deleteById(db: AsyncSession, user_id: int, resume_id: int):
    """
    Удаляет из базы данных(в основном полезно если неправильно сгенерил)
    :param db:
    :param user_id:
    :param resume_id:
    :return:
    """
    resume = await query_fetchone(db, select(ResumeData)
                                  .join(InputResume).filter(InputResume.id == ResumeData.resume_id)
                                  .where(InputResume.user_id == user_id, ResumeData.id == resume_id), False)
    if resume is False:
        raise HTTPException(404, "Нет такого резюме. Либо оно не ваше")

    await db.execute(delete(ResumeData).where(ResumeData.id == resume_id))
    await db.commit()
    return SuccessResponse()


async def get_all_resumes_count(db: AsyncSession):
    """
    Получить общее количество резюме(для главной страницы)
    :param db:
    :return:
    """
    total_count = await db.scalar(
        select(func.count()).select_from(ResumeData)
    )
    return SuccessResponse({"count": str(total_count) + " "})


async def addToFavorite(db: AsyncSession, user_id: int, resume_id: int):
    """
    Добавить в избранное
    :param db:
    :param user_id:
    :param resume_id:
    :return:
    """
    old_favorite = await query_fetchone(db, select(Favorite)
                                        .where(Favorite.user_id == user_id, Favorite.resume_id == resume_id).limit(1),
                                        False)
    if old_favorite is not False:
        raise HTTPException(403, "Уже в избранном")
    favorite = Favorite(user_id=user_id, resume_id=resume_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return SuccessResponse({"favorite": await favorite.to_dict()})


async def getMyFavorites(db: AsyncSession, user_id: int):
    """
    Получает избранные пользователя
    :param db:
    :param user_id:
    :return:
    """
    favorites = await query_fetchall(db, select(ResumeData).join(Favorite)
                                     .where(Favorite.user_id == user_id)
                                     .order_by(Favorite.id.desc()), False)
    if favorites is False:
        return SuccessResponse({"favorites": []})

    return SuccessResponse({"favorites": [
        await favorite[0].to_dict(educations=True, stacks=True, companies=True, achievements=True) for favorite in
        favorites]})


async def deleteFromFavorites(db: AsyncSession, user_id: int, resume_id: int):
    """
    Удаляет из избранных
    :param db:
    :param user_id:
    :param resume_id:
    :return:
    """
    resume = await query_fetchone(db, select(ResumeData)
                                  .join(InputResume).filter(InputResume.id == ResumeData.resume_id)
                                  .where(InputResume.user_id == user_id, ResumeData.id == resume_id), False)
    if resume is False:
        raise HTTPException(404, "Нет такого резюме. Либо оно не ваше")

    delete_resume = await db.execute(delete(Favorite).where(Favorite.resume_id == resume_id,
                                                            Favorite.user_id == user_id))
    await db.commit()
    return SuccessResponse()
