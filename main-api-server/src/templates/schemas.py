from pydantic import BaseModel


class AddTemplate(BaseModel):
    name: str
    experience_month: int


class BindTemplateParameters(BaseModel):
    data: dict
    template_id: int
