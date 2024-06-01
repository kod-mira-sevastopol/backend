from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.AbstractModel import AbstractModel


class InputResume(AbstractModel):
    __tablename__ = "inputs"

    file_name = Column(String, nullable=False)
    sender = Column(String)
    link = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)


class Education(AbstractModel):
    __tablename__ = "educations"
    # может быть много кафедр
    resume_id = Column(Integer, ForeignKey("resumes_data.id"), index=True)
    start_year = Column(Integer)
    end_year = Column(Integer)
    name = Column(String)
    tier = Column(String)
    department_name = Column(String)

    resume = relationship("ResumeData", back_populates="educations")
    #departments = relationship("Department", back_populates="education", lazy="selectin")


class Company(AbstractModel):
    __tablename__ = "companies"

    name = Column(String)
    resume_id = Column(Integer, ForeignKey("resumes_data.id"), index=True)
    start_date = Column(String)
    end_date = Column(String)
    job_description = Column(String)
    job_location = Column(String)
    position = Column(String)

    resume_data = relationship("ResumeData", back_populates="companies")


class Stack(AbstractModel):
    __tablename__ = "stack"

    stack = Column(String)
    resume_id = Column(Integer, ForeignKey("resumes_data.id"), index=True)

    resume_data = relationship("ResumeData", back_populates="stacks")


class Achievement(AbstractModel):
    __tablename__ = "achievements"

    description = Column(String)
    resume_id = Column(Integer, ForeignKey("resumes_data.id"), index=True)

    resume_data = relationship("ResumeData", back_populates="achievements")


class Skill(AbstractModel):
    __tablename__ = "skills"

    resume_id = Column(Integer, ForeignKey("resumes_data.id"), index=True)
    name = Column(String)
    type = Column(String)

    resume_data = relationship("ResumeData", back_populates="skills")




class ResumeData(AbstractModel):
    __tablename__ = "resumes_data"

    resume_id = Column(Integer, ForeignKey("inputs.id"), index=True)

    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    age = Column(String)
    birth_date = Column(String)
    email = Column(String)
    phone_number = Column(String)
    telegram = Column(String)
    # education может быть много
    hh_url = Column(String)
    # stack может быть много
    degree = Column(String)
    experience = Column(String)
    position = Column(String)

    educations = relationship("Education", back_populates="resume", lazy="selectin")
    stacks = relationship("Stack", back_populates="resume_data", lazy="selectin")
    companies = relationship("Company", back_populates="resume_data", lazy="selectin")
    achievements = relationship("Achievement", back_populates="resume_data", lazy="selectin")
    skills = relationship("Skill", back_populates="resume_data", lazy="selectin")


class Favorite(AbstractModel):
    __tablename__ = "favorites"

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    resume_id = Column(Integer, ForeignKey("resumes_data.id"), index=True)

