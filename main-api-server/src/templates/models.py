from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.AbstractModel import AbstractModel


class TemplateSkills(AbstractModel):
    __tablename__ = "templates_skills"
    hidden = ["id"]
    template_id = Column(Integer, ForeignKey("templates.id"), index=True)
    name = Column(String)
    template = relationship("Template", back_populates="skills", lazy="selectin")


class TemplateStacks(AbstractModel):
    __tablename__ = "template_stacks"
    hidden = ["id"]
    template_id = Column(Integer, ForeignKey("templates.id"), index=True)
    name = Column(String)
    type = Column(String)

    template = relationship("Template", back_populates="stacks", lazy="selectin")


class Template(AbstractModel):
    __tablename__ = "templates"

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String)
    experience_month = Column(Integer)

    skills = relationship("TemplateSkills", back_populates="template", lazy="selectin")
    stacks = relationship("TemplateStacks", back_populates="template", lazy="selectin")
