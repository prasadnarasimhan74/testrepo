# Stock Trading Agent

An autonomous stock trading agent with Amazon Bedrock LLM integration and Streamlit UI that analyzes market data, applies intelligent trading strategies, and manages a portfolio.

## Features

- **Amazon Bedrock LLM Integration**: Uses Claude AI for intelligent trading decisions
- **Interactive Streamlit UI**: Real-time visualization and control
- **Portfolio Management**: Track cash balance, stock holdings, and transaction history
- **Multiple Trading Strategies**: 
  - Amazon Bedrock LLM-based strategy with risk tolerance settings
  - Traditional Moving Average Crossover strategy
- **Stock Data Simulation**: Simulates realistic stock price movements for testing
- **Autonomous Decision Making**: Automatically makes buy/sell/hold decisions based on market analysis
- **Real-time Monitoring**: Track portfolio value, performance, and LLM reasoning

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the Streamlit App

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### Using Amazon Bedrock (Optional)

To use real Amazon Bedrock API:

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Ensure you have access to Amazon Bedrock and Claude models

3. In the Streamlit app, check "Use Real Bedrock API"

The app works in simulation mode without AWS credentials.

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
- **BedrockLLMStrategy**: Uses Amazon Bedrock's Claude model for AI-powered trading decisions
  - Analyzes trends, volatility, and momentum
  - Provides confidence scores and reasoning
  - Supports risk tolerance settings (conservative, moderate, aggressive)
  - Falls back to simulation mode without AWS credentials
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

### Streamlit UI (Recommended)

The easiest way to use the trading agent is through the interactive Streamlit interface:

```bash
streamlit run streamlit_app.py
```

Features:
- Configure initial cash and stock symbols
- Choose between LLM and traditional strategies  
- Run trading cycles with real-time visualization
- Monitor portfolio performance and LLM decisions
- View transaction history and holdings

### Python API

For programmatic usage:

```python
from stock_trading_agent import (
    Portfolio, BedrockLLMStrategy, MovingAverageCrossoverStrategy,
    StockDataSimulator, StockTradingAgent
)

# Initialize components with Bedrock LLM strategy
symbols = ['AAPL', 'GOOGL', 'MSFT']
initial_prices = {'AAPL': 150.0, 'GOOGL': 2800.0, 'MSFT': 300.0}

portfolio = Portfolio(initial_cash=50000.0)

# Use Bedrock LLM strategy (falls back to simulation without AWS credentials)
strategy = BedrockLLMStrategy(
    risk_tolerance="moderate",
    use_bedrock=False  # Set to True to use real Bedrock API
)

# Or use traditional strategy
# strategy = MovingAverageCrossoverStrategy(short_period=5, long_period=20)

data_source = StockDataSimulator(symbols, initial_prices)
agent = StockTradingAgent(portfolio, strategy, data_source)

# Warm up the price history
for _ in range(25):
    data_source.simulate_price_update()

# Run trading cycles
for cycle in range(10):
    agent.run_trading_cycle()
    agent.print_status()

# View LLM decisions
if hasattr(strategy, 'get_decision_history'):
    decisions = strategy.get_decision_history()
    for decision in decisions:
        print(f"{decision['symbol']}: {decision['action']} - {decision['reasoning']}")
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