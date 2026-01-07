from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .history import StockHistoryListSchema


class StockListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    company_name: str
    price: int
    last_updated: str


class StockCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    company_name: str
    price: int
    last_updated: Optional[datetime] = None


class StockUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: Optional[str] = None
    company_name: Optional[str] = None
    price: Optional[int] = None
    last_updated: Optional[str] = None


class StockRetrieveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    company_name: str
    price: int
    last_updated: str


class StockHistoryRetrieveSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    company_name: str
    price: int
    last_updated: str
    history: List[StockHistoryListSchema] = []
