from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.AbstractModel import AbstractModel


class Tariff(AbstractModel):
    __tablename__ = "tariffs"

    title = Column(String)
    description = Column(String)
    price = Column(Float)

    subscriptions = relationship("Subscription", backref="tariff", lazy="selectin")


class Subscription(AbstractModel):
    __tablename__ = "subscriptions"

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"), index=True)
    count_month = Column(Integer)

    tariff = relationship("Tariff", backref="subscriptions", lazy="selectin")

