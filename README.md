# Stock Trading Agent

An autonomous stock trading agent that analyzes market data, applies trading strategies, and manages a portfolio.

## Features

- **Portfolio Management**: Track cash balance, stock holdings, and transaction history
- **Trading Strategies**: Implements Moving Average Crossover strategy (extensible for other strategies)
- **Stock Data Simulation**: Simulates realistic stock price movements for testing
- **Autonomous Decision Making**: Automatically makes buy/sell/hold decisions based on market analysis
- **Real-time Monitoring**: Track portfolio value and performance

## Components

### 1. Stock
Represents individual stocks with price tracking and technical analysis capabilities:
- Current price tracking
- Price history management
- Moving average calculations

### 2. Portfolio
Manages trading portfolio:
- Cash balance tracking
- Stock holdings management
- Buy/sell transaction execution
- Transaction history
- Portfolio value calculation

### 3. Trading Strategy
Base class for implementing trading strategies:
- **MovingAverageCrossoverStrategy**: Trades based on short-term and long-term moving average crossovers
  - Buy signal: Short MA crosses above long MA
  - Sell signal: Short MA crosses below long MA

### 4. Stock Data Simulator
Simulates realistic market data:
- Random price movements (±2% per update)
- Multiple stock symbols support
- Price history tracking

### 5. Stock Trading Agent
The main autonomous agent that:
- Monitors stock prices
- Applies trading strategies
- Executes trades automatically
- Reports portfolio status

## Usage

### Basic Example

```python
from stock_trading_agent import (
    Portfolio, MovingAverageCrossoverStrategy,
    StockDataSimulator, StockTradingAgent
)

# Initialize components
symbols = ['AAPL', 'GOOGL', 'MSFT']
initial_prices = {'AAPL': 150.0, 'GOOGL': 2800.0, 'MSFT': 300.0}

portfolio = Portfolio(initial_cash=50000.0)
strategy = MovingAverageCrossoverStrategy(short_period=5, long_period=20)
data_source = StockDataSimulator(symbols, initial_prices)

agent = StockTradingAgent(portfolio, strategy, data_source)

# Warm up the price history
for _ in range(25):
    data_source.simulate_price_update()

# Run trading cycles
for cycle in range(10):
    agent.run_trading_cycle()
    agent.print_status()
```

### Running the Demo

```bash
python3 stock_trading_agent.py
```

This will run a demonstration with:
- 3 stocks (AAPL, GOOGL, MSFT)
- $50,000 initial cash
- Moving Average Crossover strategy
- 10 trading cycles

## Testing

Run the test suite:

```bash
python3 -m unittest test_trading_agent -v
```

Tests cover:
- Stock price tracking and moving averages
- Portfolio buy/sell operations
- Trading strategy decision making
- Stock data simulation
- Agent trading cycles

## Architecture

```
StockTradingAgent
├── Portfolio (manages cash and holdings)
├── TradingStrategy (makes trading decisions)
└── StockDataSimulator (provides market data)
    └── Stock[] (individual stock data)
```

## Extending the Agent

### Adding New Trading Strategies

Create a new strategy by extending the `TradingStrategy` base class:

```python
class MyCustomStrategy(TradingStrategy):
    def analyze(self, stock: Stock) -> Action:
        # Your analysis logic here
        if some_condition:
            return Action.BUY
        elif other_condition:
            return Action.SELL
        return Action.HOLD
```

### Customizing Trade Size

Adjust the number of shares per trade:

```python
agent = StockTradingAgent(portfolio, strategy, data_source)
agent.trade_size = 20  # Trade 20 shares at a time
```

## License

MIT License