from typing import Any, Optional, Dict, List
import logging

from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import APIKeyHeader
from bson import ObjectId  # type: ignore

from models.indexes import Indexes, IndexesDB, IndexUpdate  # type: ignore
from db import database  # type: ignore
from settings import Settings  # type: ignore

settings: Any = Settings()
logging.basicConfig(level=logging.INFO)

API_TOKEN: Any = settings.ADMIN_HEADER

indexes_router: Any = APIRouter()
api_admin_header: Any = APIKeyHeader(name="Authorization")


async def get_index_or_404(index_id: str) -> Dict:
    index_db = await database.indexes.find_one({"_id": ObjectId(index_id)})
    if index_db is None:
        raise HTTPException(status_code=404, detail="Index not found.")
    return index_db


async def check_admin(token: str) -> None:
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Not authenticated")


@indexes_router.post("/index")
async def create_index(index: Indexes, token: str = Depends(api_admin_header)) -> Dict:
    await check_admin(token)
    index_db = await database.indexes.find_one(
        {"$or": [{"ticker": index.ticker}, {"name": index.name}]},
    )
    if index_db:
        raise HTTPException(status_code=409, detail="Index already exists.")
    new_index = await database.indexes.insert_one(index.dict())
    refresh_index = await database.indexes.find_one({"_id": new_index.inserted_id})
    index_output = IndexesDB(**refresh_index, id=str(refresh_index["_id"]))
    return index_output.dict()


@indexes_router.put("/index/{id}")
async def update_index(
    id: str, index: IndexUpdate, token: str = Depends(api_admin_header)
) -> Dict:
    await check_admin(token)
    index_db = await get_index_or_404(id)
    await database.indexes.update_one(
        {"_id": index_db["_id"]}, {"$set": index.dict(exclude_unset=True)}
    )
    refresh_index = await database.indexes.find_one({"_id": index_db["_id"]})
    index_output = IndexesDB(**refresh_index, id=str(refresh_index["_id"]))
    return index_output.dict()


@indexes_router.get("/index/{id}")
async def get_index(id: str) -> Dict:
    index_db = await get_index_or_404(id)
    index_output = IndexesDB(**index_db, id=str(index_db["_id"]))
    return index_output.dict()


@indexes_router.get("/index/ticker/{index}")
async def get_index_info(index: str) -> Dict:
    index_db = await database.indexes.find_one({"ticker": index})
    index_output = IndexesDB(**index_db, id=str(index_db["_id"]))
    return index_output.dict()


@indexes_router.delete("/index/{id}")
async def delete_index(id: str, token: str = Depends(api_admin_header)) -> Dict:
    await check_admin(token)
    index_db = await get_index_or_404(id)
    await database.indexes.delete_one({"_id": index_db["_id"]})
    return {"deleted": id}


@indexes_router.get("/list")
async def get_indexes_list(
    start: int = Body(embed=True, default=0),
    limit: int = Body(embed=True, default=20),
) -> List:
    """
    start
    limit
    index
    sort
    desc
    search
    """
    indexes_list = await database.indexes.find({}).to_list(length=None)
    indexes_output = [IndexesDB(**i, id=str(i["_id"])) for i in indexes_list]
    return indexes_output
