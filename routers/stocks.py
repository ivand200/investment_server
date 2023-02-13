from typing import Any, Optional, Dict, List

from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import APIKeyHeader
from bson import ObjectId  # type: ignore

from db import database  # type: ignore
from models.stocks import Stocks, StocksDB, StocksUpdate  # type: ignore
from settings import Settings  # type: ignore

settings: Any = Settings()

API_TOKEN = settings.ADMIN_HEADER


stocks_router: Any = APIRouter()
api_admin_header: Any = APIKeyHeader(name="Authorization")


async def check_admin(token: str) -> None:
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Not authenticated")


async def get_stock_or_404(stock_id: str) -> Stocks:
    stock_db = await database.stocks.find_one({"_id": ObjectId(stock_id)})
    if stock_db is None:
        raise HTTPException(status_code=404, detail="Stock not found.")
    return stock_db


async def get_index_or_404(index_ticker: str) -> Dict:
    index_db = await database.indexes.find_one({"ticker": index_ticker})
    if index_db is None:
        raise HTTPException(status_code=404, detail="Index not found")
    return index_db


@stocks_router.post("/stock")
async def create_stock(stock: Stocks, token: str = Depends(api_admin_header)) -> Dict:
    """
    Create stock
    name: StrictStr
    ticker: StrictStr
    index_id: str
    momentum_12_2: Optional[float]
    momentum_avg: Optional[float]
    e_p: Optional[float]
    ma_10: Optional[int]
    div_p: Optional[float]
    """
    await check_admin(token)
    stock_db = await database.stocks.find_one(
        {"$or": [{"ticker": stock.ticker}, {"name": stock.name}]}
    )
    if stock_db:
        raise HTTPException(status_code=409, detail="Stock already exists.")
    index_db = await database.indexes.find_one({"_id": ObjectId(stock.index_id)})
    if index_db is None:
        raise HTTPException(status_code=409, detail="Cant find index.")

    new_stock = await database.stocks.insert_one(stock.dict(exclude_unset=True))
    refresh_stock = await database.stocks.find_one({"_id": new_stock.inserted_id})
    stock_output = StocksDB(**refresh_stock, id=str(refresh_stock["_id"]))

    return stock_output.dict(exclude_unset=True)


@stocks_router.put("/stock/{id}")
async def update_stock(
    id: str, stock: StocksUpdate, token: str = Depends(api_admin_header)
) -> StocksDB:
    """
    Update stock by id
    name: StrictStr
    ticker: StrictStr
    index_id: str
    momentum_12_2: Optional[float]
    momentum_avg: Optional[float]
    e_p: Optional[float]
    ma_10: Optional[int]
    div_p: Optional[float]
    """
    await check_admin(token)
    stock_db = await get_stock_or_404(id)
    await database.stocks.update_one(
        {"_id": stock_db["_id"]},
        {"$set": stock.dict(exclude_unset=True)},
    )
    stock_refresh = await database.stocks.find_one({"_id": stock_db["_id"]})
    stock_output = StocksDB(**stock_refresh, id=str(stock_refresh["_id"]))

    return stock_output.dict(exclude_unset=True)


@stocks_router.get("/stock/{id}")
async def get_stock(id: str) -> Dict:
    """
    Get stock by id
    """
    stock_db = await get_stock_or_404(id)
    stock_output = StocksDB(**stock_db, id=str(stock_db["_id"]))
    return stock_output.dict(exclude_unset=True)


@stocks_router.get("/stock/ticker/{ticker}")
async def get_stock_by_ticker(ticker: str) -> Dict:
    """
    Get stock data by ticker
    """
    stock_db = await database.stocks.find_one({"ticker": ticker})
    stock_output = StocksDB(**stock_db, id=str(stock_db["_id"]))
    return stock_output.dict(exclude_unset=True)


@stocks_router.delete("/stock/{id}")
async def delete_stock(id: str, token: str = Depends(api_admin_header)) -> Dict:
    """
    Delete stock by id
    """
    await check_admin(token)
    stock_db = await get_stock_or_404(id)
    await database.stocks.delete_one({"_id": stock_db["_id"]})
    return {"deleted": id}


@stocks_router.get("/{index}")
async def get_stocks_list(
    index: str,
    sort_by: str = Body(embed=True, default="momentum_12_2"),
    desc: bool = Body(emdeb=True, default=False),
    limit: int = Body(embed=True, default=20),
) -> List:
    """
    Stocks list by index by params
    """
    if desc:
        desc_or_asc = 1
    else:
        desc_or_asc = -1

    index_db = await database.indexes.find_one({"ticker": index})
    stocks_db = (
        await database.stocks.find({"index_id": str(index_db["_id"])})
        .sort(sort_by, desc_or_asc)
        .limit(limit)
        .to_list(None)
    )
    stocks_output = [
        StocksDB(**i, id=str(i["_id"])).dict(exclude_unset=True) for i in stocks_db
    ]

    return stocks_output
