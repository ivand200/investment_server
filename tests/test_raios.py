from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ratios import momentum_12, momentum_avg, div_p, e_p, ma_10, define_time


def test_define_time():
    """
    GIVEN Current date
    WHEN Call define_time function
    THEN check year_ago == 12 months ago 28th, last_month == last ended month 28th
    """
    # Current month on 28th
    start_month = datetime.now().replace(day=28)
    # Previous month 28th
    last_month = start_month + relativedelta(months=-1)
    # Minus 12 months, 28th
    year_ago = last_month + relativedelta(months=-12)
    time_test = define_time()

    assert time_test[0].strftime("%Y-%m-%d") == year_ago.strftime("%Y-%m-%d")
    assert time_test[1].strftime("%Y-%m-%d") == last_month.strftime("%Y-%m-%d")


@pytest.mark.parametrize("ticker", ["MMM", "MSFT", "AAPL", "GS", "MCD", "V"])
def test_momentum_12_1(ticker):
    """
    GIVEN ticker str, upper to get momentum_12_1
    WHEN userfunction momentum_12
    THEN check result not None, result is float
    """
    mom = momentum_12(ticker)
    assert isinstance(float(mom), float)
    assert mom


@pytest.mark.parametrize("ticker", ["MMM", "MSFT", "AAPL", "GS", "MCD", "V"])
def test_momentum_12_2(ticker):
    """
    GIVEN
    WHEN
    THEN
    """
    mom_12_2 = momentum_12(ticker, -2)
    assert isinstance(float(mom_12_2), float)
    assert mom_12_2


@pytest.mark.parametrize("ticker", ["MMM", "MSFT", "AAPL", "GS", "MCD", "V"])
def test_momentum_avg(ticker):
    """
    GIVEN get momentum_12_2 by ticker
    WHEN call momentum_12_2 function by ticker
    THEN check result is not None, result is float
    """
    mom_avg = momentum_avg(ticker)
    assert isinstance(float(mom_avg), float)
    assert mom_avg


@pytest.mark.parametrize("ticker", ["MMM", "MSFT", "AAPL", "GS", "MCD", "V"])
def test_ma_10(ticker):
    """
    GIVEN get moving average 10 status by ticker
    WHEN call function ma_10
    THEN check result is integer, result == 1 or result == 0
    """
    ma10 = ma_10(ticker)
    assert isinstance(int(ma10), int)
    assert ma10 == 1 or ma10 == 0


@pytest.mark.parametrize("ticker", ["MMM", "MSFT", "AAPL", "GS", "MCD", "V", "CRM"])
def test_div_p(ticker):
    """
    GIVEN Get average dividends / last ended month close price
    WHEN call function div_p
    THEN check result not nan
    """
    dividends_price = div_p(ticker)

    assert dividends_price or dividends_price == 0


@pytest.mark.parametrize("ticker", ["MMM", "MSFT", "AAPL", "GS", "MCD", "V", "CRM"])
def test_e_p(ticker):
    """
    GIVEN Get e/p ratio by ticker
    WHEN call e_p function
    THEN check e_p is float
    """
    earnings_price = e_p(ticker)

    assert isinstance(earnings_price, float)
