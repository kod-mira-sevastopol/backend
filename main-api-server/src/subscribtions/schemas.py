from pydantic import BaseModel


class AddSubscription(BaseModel):
    tariff_id: int