from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockHistoryListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    stock_id: int
    price: int
    created_at: datetime
