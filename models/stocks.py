from typing import Optional

from pydantic import BaseModel, StrictStr


class Stocks(BaseModel):
    name: StrictStr
    ticker: StrictStr
    index_id: str
    momentum_12_2: Optional[float]
    momentum_avg: Optional[float]
    e_p: Optional[float]
    ma_10: Optional[int]
    div_p: Optional[float]

    class Config:
        orm_mode = True


class StocksDB(Stocks):
    id: str


class StocksUpdate(BaseModel):
    name: Optional[StrictStr]
    ticker: Optional[StrictStr]
    index_id: Optional[str]
    momentum_12_2: Optional[float]
    momentum_avg: Optional[float]
    e_p: Optional[float]
    ma_10: Optional[int]
    div_p: Optional[float]

    class Config:
        orm_mode = True
