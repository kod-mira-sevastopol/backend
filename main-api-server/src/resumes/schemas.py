from pydantic import BaseModel


class UploadResume(BaseModel):
    sender: str


class AddFavorite(BaseModel):
    resume_id: int


class DeleteFavorite(AddFavorite):
    pass