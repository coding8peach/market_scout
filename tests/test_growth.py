import pandas as pd
from market_scout.tools.stock_screen_tool import (
    analyze_growth,
    analyze_prices,
    get_stock_universe,
    screen_stocks,
)


universe = get_stock_universe()

tickers = universe["Ticker"].tolist()#[:100]
import time

start = time.time()

growth = analyze_growth(tickers)

elapsed = time.time() - start

print(f"\nRetrieved growth for {len(growth)} stocks")
print(f"Time: {elapsed:.1f} seconds")

print("\nTOP 15 BY ANNUAL REVENUE GROWTH")
print(
    growth
    .sort_values("Revenue Growth", ascending=False)
    .head(15)
    .to_string(index=False)
)

# universe = get_stock_universe()
# tickers = universe["Ticker"].tolist()

# # Same parameters you normally use in the app
# min_return = 0.20
# max_volatility = 0.40

# analysis = analyze_prices(tickers)

# filtered = screen_stocks(
#     analysis,
#     min_return,
#     max_volatility
# )

# growth = analyze_growth(tickers)

# growth_ranked = (
#     growth
#     .sort_values("Revenue Growth", ascending=False)
#     .head(10)
# )

# # ----- Price candidates -----

# price_candidates = filtered.reset_index()

# price_candidates = price_candidates.merge(
#     growth,
#     on="Ticker",
#     how="left"
# )

# price_candidates = price_candidates.merge(
#     universe,
#     on="Ticker",
#     how="left"
# )

# price_candidates = price_candidates.rename(
#     columns={"GICS Sector": "Sector"}
# )

# price_candidates["Signal"] = "Price"


# # ----- Growth candidates -----

# growth_candidates = growth_ranked.merge(
#     analysis.reset_index(),
#     on="Ticker",
#     how="left"
# )

# growth_candidates = growth_candidates.merge(
#     universe,
#     on="Ticker",
#     how="left"
# )

# growth_candidates = growth_candidates.rename(
#     columns={"GICS Sector": "Sector"}
# )

# growth_candidates["Signal"] = "Growth"


# # ----- Combine -----

# candidates = pd.concat(
#     [price_candidates, growth_candidates],
#     ignore_index=True
# )

# print(
#     candidates[
#         [
#             "Ticker",
#             "Sector",
#             "Period Return",
#             "Volatility",
#             "Sharpe",
#             "Revenue Growth",
#             "Signal",
#         ]
#     ].to_string(index=False)
# )