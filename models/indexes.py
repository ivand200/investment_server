from typing import Optional

from pydantic import BaseModel, StrictStr


class Indexes(BaseModel):
    name: StrictStr
    ticker: StrictStr

    class Config:
        orm_mode = True


class IndexesDB(Indexes):
    id: str


class IndexUpdate(BaseModel):
    name: Optional[str]
    ticker: Optional[str]