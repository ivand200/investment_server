import pytest
import pymongo

from settings import Settings


settings = Settings()


@pytest.fixture(scope="session")
def backend():
    return settings.BACKEND


@pytest.fixture(scope="session")
def database():
    client = pymongo.MongoClient(str(settings.DATABASE))
    mydb = client.investments
    return mydb


@pytest.fixture(scope="function")
def new_index(database):
    data = {"name": "MMVB","ticker": "MCIB"}
    yield data
    database.indexes.delete_many({"ticker": data["ticker"]})


@pytest.fixture(scope="function")
def index_db(database):
    data = {"name": "MMVB", "ticker": "MD"}
    database.indexes.insert_one(data)
    yield data
    database.indexes.delete_many({"ticker": data["ticker"]})


@pytest.fixture(scope="function")
def new_stock(database, index_db):
    data = {
        "name": "stock_test",
        "ticker": "STT",
        "index_id": str(index_db["_id"]),
    }
    yield data
    database.stocks.delete_many({"name": data["name"]})


@pytest.fixture(scope="function")
def stock_db(database, index_db):
    data = {
        "name": "Pytest",
        "ticker": "PTT",
        "index_id": str(index_db["_id"]),
    }
    database.stocks.insert_one(data)
    yield data
    database.stocks.delete_many({"name": data["name"]})


@pytest.fixture(scope="function")
def stocks_index(database, index_db):
    stocks_list = []
    number = 7
    for i in range(number):
        data = {
            "name": f"Test{i}",
            "ticker": f"T{i}",
            "index_id": str(index_db["_id"]),
        }
        stocks_list.append(data)
        database.stocks.insert_one(data)
    yield stocks_list
    database.stocks.delete_many({"name": {"$regex": "Test"}})
