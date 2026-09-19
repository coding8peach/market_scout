import yfinance as yf

ticker = yf.Ticker("NVDA")

income = ticker.get_income_stmt(freq="yearly")
revenue = income.loc["TotalRevenue"]

print("\nRevenue:")
print(revenue)

latest = revenue.iloc[0]
previous = revenue.iloc[1]

growth = latest / previous - 1

print("\nCalculated Revenue Growth:")
print(growth)
print(income)