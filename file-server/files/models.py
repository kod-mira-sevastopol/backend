from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary

from AbstractModel import AbstractModel


class User(AbstractModel):
    __tablename__ = "users"


class File(AbstractModel):
    __tablename__ = "files"

    filename = Column(String)
    hash_name = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    #file_data = Column(LargeBinary)
    file_type = Column(String, index=True)