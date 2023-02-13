import pytest
import requests

from settings import Settings


settings = Settings()


def test_create_stock(backend, new_stock, database) -> None:
    """
    GIVEN Create new stock with name, ticker, index_id
    WHEN POST "/api/stocks/stock"
    THEN check status_code == 200, stock in database, stock ticker in response
    """
    r = requests.post(
        f"{backend}/api/stocks/stock",
        json=new_stock,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    r_body = r.json()
    index_db_check = database.stocks.find_one({"name": new_stock["name"]})

    assert r.status_code == 200
    assert index_db_check
    assert r_body["ticker"] == new_stock["ticker"]


def test_create_stock_no_header(backend, new_stock) -> None:
    """
    GIVEN Create new stock with no auth header
    WHEN POST "/api/stocks/stock"
    THEN status_code == 403
    """
    r = requests.post(
        f"{backend}/api/stocks/stock",
        json=new_stock,
        timeout=10,
    )

    assert r.status_code == 403


def test_create_stock_wrong_header(backend, new_stock) -> None:
    """
    GIVEN Create new stock woth wrong header
    WHEN POST "/api/stocks/stock"
    THEN status_code == 403
    """
    r = requests.post(
        f"{backend}/api/stocks/stock",
        json=new_stock,
        headers={"Authorization": "AFKjig435-0gjk34"},
        timeout=10,
    )

    assert r.status_code == 403


def test_create_stock_existing_ticker(backend, stock_db) -> None:
    """
    GIVEN Create new stock with existing ticker or name
    WHEN POST "/api/stocks/stock"
    THEN status_code == 409
    """
    del stock_db["_id"]
    r = requests.post(
        f"{backend}/api/stocks/stock",
        json=stock_db,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )

    assert r.status_code == 409


def test_create_stock_no_valid_schema(backend, new_stock, database) -> None:
    """
    GIVEN Create new stock with no valid schema
    WHEN POST "/api/stocks/stock"
    THEN status_code == 422
    """
    new_stock["ticker"] = 12
    r = requests.post(
        f"{backend}/api/stocks/stock",
        json=new_stock,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    stock_db_check = database.stocks.find_one({"name": new_stock["name"]})

    assert r.status_code == 422
    assert stock_db_check is None


def test_create_stock_wrong_index_id(backend, new_stock, database) -> None:
    """
    GIVEN Create new stock with wrong index_id field
    WHEN POST "/api/stocks/stock"
    THEN status_code == 500, None stock in database
    """
    new_stock["index_id"] = "oh45843u50354vfef5"
    r = requests.post(
        f"{backend}/api/stocks/stock",
        json=new_stock,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    stock_db_check = database.stocks.find_one({"name": new_stock["name"]})

    assert r.status_code == 500
    assert stock_db_check is None


def test_update_stock(backend, stock_db, database) -> None:
    """
    GIVEN Update stock
    WHEN PUT "/api/stocks/stock/<id>"
    THEN status_code == 200, changes in response and in database
    """
    payload = {"momentum_12_2": 0.53}
    r = requests.put(
        f"{backend}/api/stocks/stock/{str(stock_db['_id'])}",
        json=payload,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    r_body = r.json()
    stock_db_check = database.stocks.find_one({"_id": stock_db["_id"]})

    assert r.status_code == 200
    assert r_body["momentum_12_2"] == payload["momentum_12_2"]
    assert stock_db_check["momentum_12_2"] == payload["momentum_12_2"]


def test_update_stock_with_no_header(backend, stock_db, database) -> None:
    """
    GIVEN Update stock without auth header
    WHEN PUT "/api/stocks/stock/<id>"
    THEN status_code == 403
    """
    payload = {"momentum_12_2": 0.53}
    r = requests.put(
        f"{backend}/api/stocks/stock/{str(stock_db['_id'])}",
        json=payload,
        timeout=10,
    )

    assert r.status_code == 403


def test_update_stock_no_valid_data(backend, stock_db, database):
    """
    GIVEN Update stock with no valid data
    WHEN PUT "/api/stocks/stock/<id>"
    THEN status_code == 422
    """
    payload = {"momentum_12_2": "high"}
    r = requests.put(
        f"{backend}/api/stocks/stock/{str(stock_db['_id'])}",
        json=payload,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )

    assert r.status_code == 422


def test_get_stock(backend, stock_db):
    """
    GIVEN Get stock by id
    WHEN GET "/api/stocks/stock/<id>
    THEN
    """
    r = requests.get(
        f"{backend}/api/stocks/stock/{str(stock_db['_id'])}",
        timeout=10,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert r_body["id"] == str(stock_db['_id'])


def test_get_stock_by_ticker(backend, stock_db):
    """
    GIVEN Get stock data by ticker
    WHEN GET "/api/stocks/stock/ticker/<ticker>"
    THEN status_code == 200, ticker in response
    """
    r = requests.get(
        f"{backend}/api/stocks/stock/ticker/{stock_db['ticker']}",
        timeout=10,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert r_body["ticker"] == stock_db["ticker"]


def test_delete_stock(backend, stock_db, database):
    """
    GIVEN Delete stock by id
    WHEN DELETE "api/stocks/stock/<id>"
    THEN status_code == 200, deleted id in response
    """
    r = requests.delete(
        f"{backend}/api/stocks/stock/{str(stock_db['_id'])}",
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    r_body = r.json()
    stock_db_check = database.stocks.find_one({"_id": stock_db["_id"]})

    assert r.status_code == 200
    assert r_body["deleted"] == str(stock_db['_id'])
    assert stock_db_check is None


def test_get_stocks_list_by_index(backend, stocks_index, index_db):
    """
    GIVEN Get stocks list by index
    WHEN GET "api/stocks/<index>"
    THEN status_code == 200
    """
    r = requests.get(
        f"{backend}/api/stocks/{index_db['ticker']}",
        timeout=10,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert r_body[0]["index_id"] == str(index_db["_id"])
    assert len(r_body) == len(stocks_index)


def test_get_stock_list_by_index():
    """
    GIVEN
    WHEN
    THEN
    """
