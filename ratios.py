from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import urllib.error
import json
import math

import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore
from dateutil.relativedelta import relativedelta


def define_time() -> tuple:
    """
    Define time period
    from 28th last ended month
    to 12 months back
    """
    start_month = datetime.now().replace(day=28)
    last_month = start_month + relativedelta(months=-1)
    year_ago = last_month + relativedelta(months=-12)
    return year_ago, last_month


def get_history(ticker: str, interval: str = "1d") -> pd.DataFrame:
    """
    Get ticker price history for last 12 months
    """
    ticker = yf.Ticker(ticker)
    start_period, end_period = define_time()
    ticker_history = ticker.history(
        start=start_period, end=end_period, interval=interval
    )
    return ticker_history


def momentum_12(ticker: str, period: int = -1) -> float:
    """
    Momentum_12_1 -> last ended month(28th) close price / close price year ago
    """
    series = get_history(ticker)
    momentum = (series["Close"][period] / series["Close"][0]) - 1
    return round(momentum, 3)


def momentum_avg(ticker: str) -> float:
    """
    Returns momentum average for 3, 6, 12 previous months
    """
    series = get_history(ticker)
    momentum_3 = series["Close"][-1] / series["Close"][-66]
    momentum_6 = series["Close"][-1] / series["Close"][-132]
    momentum_12_ = series["Close"][-1] / series["Close"][0]
    mom_avg = (momentum_3 + momentum_6 + momentum_12_) / 3
    return round(mom_avg, 2)


def div_p(ticker: str) -> float:
    """
    Returns average dividends / last ended month(28th) close price
    """
    series = get_history(ticker)
    share = yf.Ticker(ticker)
    divs = share.dividends[-16:].mean()
    last_close = series["Close"][-1]
    dividends_price = round(divs / last_close, 3)
    if math.isnan(dividends_price):
        dividends_price = 0
    return dividends_price


def get_shares(ticker: str) -> float:
    url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=defaultKeyStatistics"
    fhand = urllib.request.urlopen(url).read()
    data = json.loads(fhand)
    shares_outstanding = data["quoteSummary"]["result"][0]["defaultKeyStatistics"]["sharesOutstanding"]["raw"]
    return shares_outstanding


def e_p(ticker: str) -> float:
    """
    Returns average income(fcf) for last 4 years / price
    """
    url = (
        f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=incomeStatementHistory"
    )
    fhand = urllib.request.urlopen(url).read()
    data = json.loads(fhand)
    income_statements = data["quoteSummary"]["result"][0]["incomeStatementHistory"]["incomeStatementHistory"]
    income_for_last_4_years = [i["netIncome"]["raw"] for i in income_statements]

    shares = get_shares(ticker)
    earning_per_share = (sum(income_for_last_4_years) / 4) / shares
    series = get_history(ticker)
    average_earnings_per_share = earning_per_share / series["Close"][-1]

    return round(average_earnings_per_share, 3)


def ma_10(ticker: str) -> int:
    """
    Returns 1 if last month close price above MA_10, 0 if below
    """
    series = get_history(ticker, "1wk")
    end_days = ["25", "26", "27", "28", "29", "30", "31"]
    day_data = [series.loc[i]["Close"] for i in series.index if str(i.day) in end_days]
    average_10m_price = sum(day_data[3:]) / 10
    last_close_price = series["Close"][-1]
    ma10_status = 1 if last_close_price > average_10m_price else 0
    return ma10_status
