from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
from crewai.tools import tool

def analyze_growth(tickers, max_workers=5):

    def fetch_growth(ticker):
        try:
            income = yf.Ticker(ticker).get_income_stmt(
                freq="yearly"
            )

            if income.empty:
                return None

            if "TotalRevenue" not in income.index:
                return None

            revenue = income.loc["TotalRevenue"].dropna()

            if len(revenue) < 2:
                return None

            # Make sure newest year comes first
            revenue = revenue.sort_index(ascending=False)

            latest = revenue.iloc[0]
            previous = revenue.iloc[1]

            if previous == 0:
                return None

            revenue_growth = latest / previous - 1

            return {
                "Ticker": ticker,
                "Revenue Growth": revenue_growth
            }

        except Exception as e:
            print(f"Growth lookup failed for {ticker}: {e}")
            return None

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_growth, ticker): ticker
            for ticker in tickers
        }

        for future in as_completed(futures):
            result = future.result()

            if result is not None:
                results.append(result)

    print(
        f"Growth data retrieved: "
        f"{len(results)} / {len(tickers)} stocks"
    )

    return pd.DataFrame(results)

def analyze_prices(tickers):
    stocks = yf.download(
        tickers,
        period="1y",
        auto_adjust=True
    )

    if stocks.empty:
        raise RuntimeError(
            "Unable to retrieve stock price data. "
            "The market data provider may be temporarily unavailable."
        )

    prices = stocks["Close"]

    if prices.empty:
        raise RuntimeError(
            "No price data was returned."
        )

    period_return = prices.iloc[-1] / prices.iloc[0] - 1

    daily_returns = prices.pct_change(fill_method=None)

    volatility = daily_returns.std() * (252 ** 0.5)

    sharpe = (
        daily_returns.mean()
        / daily_returns.std()
        * (252 ** 0.5)
    )

    return pd.DataFrame({
        "Period Return": period_return,
        "Volatility": volatility,
        "Sharpe": sharpe
    })

def screen_stocks(df, min_return, max_volatility, top_n=10):
    filtered = df.loc[(df["Volatility"] < max_volatility) & 
                      (df["Period Return"] > min_return)]


    ranked = filtered.sort_values(
        by="Sharpe",
        ascending=False
    )

    return ranked.head(top_n)

def get_stock_universe():
    url = (
        "https://raw.githubusercontent.com/"
        "datasets/s-and-p-500-companies/"
        "main/data/constituents.csv"
    )

    sp500 = pd.read_csv(url)

    sp500["Ticker"] = (
        sp500["Symbol"]
        .str.replace(".", "-", regex=False)
    )

    return sp500[["Ticker", "GICS Sector"]]


@tool("Stock Screener")
def stock_screener_tool(
    min_return: float,
    max_volatility: float
) -> list:
    """
    Screen S&P 500 stocks using quantitative criteria.

    Args:
        min_return: Minimum required period return.
        max_volatility: Maximum allowed annualized volatility.

    Returns:
        Ranked stock candidates.
    """

    universe = get_stock_universe()

    tickers = universe["Ticker"].tolist()

    analysis = analyze_prices(tickers)

    filtered = screen_stocks(
        analysis,
        min_return,
        max_volatility
    )

    growth = analyze_growth(tickers)

    growth_ranked = (
        growth
        .sort_values("Revenue Growth", ascending=False)
        .head(10)
    )

    # Top price candidates
    price_candidates = filtered.reset_index()

    # Add revenue growth to price candidates
    price_candidates = price_candidates.merge(
        growth,
        on="Ticker",
        how="left"
    )

    # Top growth candidates
    growth_candidates = growth_ranked.merge(
        analysis.reset_index(),
        on="Ticker",
        how="left"
    )

    # Add sector information
    price_candidates = price_candidates.merge(
        universe,
        on="Ticker",
        how="left"
    )

    growth_candidates = growth_candidates.merge(
        universe,
        on="Ticker",
        how="left"
    )

    # Rename sector consistently
    price_candidates = price_candidates.rename(
        columns={"GICS Sector": "Sector"}
    )

    growth_candidates = growth_candidates.rename(
        columns={"GICS Sector": "Sector"}
    )

    # Record how each candidate qualified
    price_candidates["Signal"] = "Price"
    growth_candidates["Signal"] = "Growth"

    # Combine both candidate pools
    candidates = pd.concat(
        [price_candidates, growth_candidates],
        ignore_index=True
    )

    # Combine candidates that qualified through both signals
    candidates = (
        candidates
        .groupby("Ticker", as_index=False)
        .agg({
            "Period Return": "first",
            "Volatility": "first",
            "Sharpe": "first",
            "Revenue Growth": "first",
            "Sector": "first",
            "Signal": lambda x: " + ".join(dict.fromkeys(x))
        })
    )
    #debug
    # candidate_view = candidates[
    #     [
    #         "Ticker",
    #         "Sector",
    #         "Period Return",
    #         "Volatility",
    #         "Sharpe",
    #         "Revenue Growth",
    #         "Signal"
    #     ]
    # ]

    # print(candidate_view.to_string(index=False))

    # candidate_view.to_csv(
    #     "candidate_debug.csv",
    #     index=False
    # )

    records = candidates.to_dict(orient="records")

    return records
