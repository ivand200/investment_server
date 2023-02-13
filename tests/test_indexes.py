import pytest
import requests

from settings import Settings


settings = Settings()


def test_create_index(backend, new_index, database) -> None:
    """
    GIVEN Create new index
    WHEN POST "api/indexes/index"
    THEN check status_code == 200, check name, ticker fields, index in database
    """
    r = requests.post(
        f"{backend}/api/indexes/index",
        json=new_index,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    r_body = r.json()
    index_db_check = database.indexes.find_one({"name": new_index["name"]})

    assert r.status_code == 200
    assert index_db_check
    assert r_body["ticker"] == index_db_check["ticker"]


def test_create_index_no_header(backend, new_index) -> None:
    """
    GIVEN Create new index without auth header
    WHEN POST "api/indexes/index"
    THEN status_code == 403
    """
    r = requests.post(
        f"{backend}/api/indexes/index",
        json=new_index,
        timeout=10,
    )

    assert r.status_code == 403


def test_create_index_wrong_header(backend, new_index) -> None:
    """
    GIVEN Create index with wrong header
    WHEN POST "api/indexes/index"
    THEN status_code == 403
    """
    r = requests.post(
        f"{backend}/api/indexes/index",
        json=new_index,
        headers={"Authorization": "fewFE47Ofb7Q"},
        timeout=10,
    )

    assert r.status_code == 403


def test_create_index_existing_ticker(backend, index_db) -> None:
    """
    GIVEN Create index with existing name or ticker
    WHEN POST "api/indexes/index"
    THEN raise error 409
    """
    del index_db["_id"]
    r = requests.post(
        f"{backend}/api/indexes/index",
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        json=index_db,
        timeout=10,
    )

    assert r.status_code == 409


def test_create_index_no_valid_scheme(backend, new_index) -> None:
    """
    GIVEN Create new index with no valid scheme
    WHEN POST "api/indexes/index"
    THEN raise error 422
    """
    new_index["name"] = 112
    r = requests.post(
        f"{backend}/api/indexes/index",
        json=new_index,
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )

    assert r.status_code == 422


def test_update_index(backend, index_db, database):
    """
    GIVEN Update index with new name
    WHEN PUT "api/indexes/index/<id>"
    THEN check status_code == 200, changes in database, changes in response
    """
    payload = {"name": "Moscow Exchange"}
    r = requests.put(
        f"{backend}/api/indexes/index/{str(index_db['_id'])}",
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        json=payload,
        timeout=10,
    )
    r_body = r.json()
    index_db_check = database.indexes.find_one({"ticker": index_db["ticker"]})

    assert r.status_code == 200
    assert r_body["name"] == payload["name"]
    assert index_db_check["name"] == payload["name"]


def test_get_index(backend, index_db):
    """
    GIVEN Get index by id
    WHEN GET "api/indexes/index/<id>"
    THEN check status_code == 200, ticker, id in response
    """
    r = requests.get(
        f"{backend}/api/indexes/index/{str(index_db['_id'])}",
        timeout=10,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert r_body["ticker"] == index_db["ticker"]
    assert r_body["id"] == str(index_db["_id"])


def test_get_index_by_ticker(backend, index_db) -> None:
    """
    GIVEN
    WHEN
    THEN
    """
    r = requests.get(
        f"{backend}/api/indexes/index/ticker/{str(index_db['ticker'])}",
        timeout=10,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert r_body["ticker"] == index_db["ticker"]


def test_delete_index(backend, index_db, database) -> None:
    """
    GIVEN Delete index by id
    WHEN DELETE "api/indexes/index/<id>"
    THEN check status_code == 200, no index in database after deletion, index id in response
    """
    r = requests.delete(
        f"{backend}/api/indexes/index/{str(index_db['_id'])}",
        headers={"Authorization": f"{settings.ADMIN_HEADER}"},
        timeout=10,
    )
    r_body = r.json()
    index_db_check = database.indexes.find_one({"_id": index_db["_id"]})

    assert r.status_code == 200
    assert index_db_check is None
    assert r_body["deleted"] == str(index_db['_id'])


def test_get_index_list(backend, index_db) -> None:
    """
    GIVEN Get indexes list
    WHEN GET "api/indexes/index"
    THEN check status_code == 200, list len in response
    """
    r = requests.get(
        f"{backend}/api/indexes/list",
        timeout=10,
    )
    r_body = r.json()

    assert r.status_code == 200
    assert len(r_body) >= 1
