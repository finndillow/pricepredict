import yfinance as yf
import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import tkinter

window = tkinter.Tk()
window.title('test')

window.geometry('1200x600')

choice = input('Enter a stock symbol: ')
choice = choice.upper()

window.mainloop()

currentStock = yf.download(tickers=choice, start='2021-01-01', end='2022-02-03', interval='1d')

currentStock.head()

currentStock['SMA_30'] = currentStock['Close'].rolling(window=30, min_periods=1).mean()
currentStock['SMA_9'] = currentStock['Close'].rolling(window=9, min_periods=1).mean()

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

print(get_current_price(choice))

trade_signals = pd.DataFrame(index=currentStock.index)

# Define the intervals for the Fast and Slow Simple Moving Averages (in days)
short_interval = 10
long_interval = 40

# Compute the Simple Moving Averages and add it to the dateframe as new columns
trade_signals['Short'] = currentStock['Close'].rolling(window=short_interval, min_periods=1).mean()
trade_signals['Long'] = currentStock['Close'].rolling(window=long_interval, min_periods=1).mean()

# Create a new column populated with zeros
trade_signals['Signal'] = 0.0

# Wherever the Shorter term SMA is above the Longer term SMA, set the Signal column to 1, otherwise 0
trade_signals['Signal'] = np.where(trade_signals['Short'] > trade_signals['Long'], 1.0, 0.0)  

trade_signals['Position'] = trade_signals['Signal'].diff()

initial_balance = 100.0 # ten thousand USD

# Create dataframe containing all the dates considered
backtest = pd.DataFrame(index=trade_signals.index)

# Add column containing the daily percent returns of Bitcoin
backtest['currentStock_Return'] = currentStock['Close'] / currentStock['Close'].shift(1)

# Add column containing the daily percent returns of the Moving Average Crossover strategy
backtest['Alg_Return'] = np.where(trade_signals.Signal == 1, backtest.currentStock_Return, 1.0)

# Add column containing the daily value of the portfolio using the Crossover strategy
backtest['Balance'] = initial_balance * backtest.Alg_Return.cumprod() # cumulative product

fig, ax = plt.subplots(dpi=150)

# Formatting the date axis
date_format = DateFormatter("%h-%d-%y")
ax.xaxis.set_major_formatter(date_format)
ax.tick_params(axis='x', labelsize=8)
fig.autofmt_xdate()

stock = yf.Ticker("ABEV3.SA")
price = stock.info['regularMarketPrice']

# Plotting the closing price against the date (1 day interval)
ax.plot(currentStock['Close'], lw=0.75, label='Closing Price') # Added label
# ax.plot(SPY['SMA_9'], lw=0.75, alpha=0.75, label='9 Day SMA')
# ax.plot(SPY['SMA_30'], lw=0.75, alpha=0.75, label='30 Day SMA')

ax.plot(initial_balance*backtest.currentStock_Return.cumprod(), lw=0.75, alpha=0.75, label='Buy and Hold')

# Plotting total value of Crossing Averages Strategy
ax.plot(backtest['Balance'], lw=0.75, alpha=0.75, label='Crossing Averages')

ax.plot(trade_signals['Short'], lw=0.75, alpha=0.75, color='orange', label='Short-term SMA')

# Plot the longer-term moving average
ax.plot(trade_signals['Long'], lw=0.75, alpha=0.75, color='purple', label='Long-term SMA')

ax.plot(trade_signals.loc[trade_signals['Position']==1.0].index, trade_signals.Short[trade_signals['Position'] == 1.0],
 marker=6, ms=4, linestyle='none', color='green')

 # Adding red arrows to indicate sell orders
ax.plot(trade_signals.loc[trade_signals['Position'] == -1.0].index, trade_signals.Short[trade_signals['Position'] == -1.0],
 marker=7, ms=4, linestyle='none', color='red')

# Adding labels and title to the plot
ax.set_ylabel('Dollars')
ax.set_title(choice) # adding a grid
ax.legend()

# Displaying the price chart
plt.show()
