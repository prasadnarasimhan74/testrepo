"""
Stock Trading Agent

A simple autonomous trading agent that can analyze stock data,
make trading decisions based on strategies, and manage a portfolio.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Action(Enum):
    """Trading actions"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Stock:
    """Represents a stock with historical price data"""
    
    def __init__(self, symbol: str, current_price: float):
        self.symbol = symbol
        self.current_price = current_price
        self.price_history: List[float] = []
    
    def update_price(self, new_price: float):
        """Update the stock price and add to history"""
        self.price_history.append(self.current_price)
        self.current_price = new_price
    
    def get_moving_average(self, periods: int) -> Optional[float]:
        """Calculate moving average for the specified number of periods"""
        if len(self.price_history) < periods:
            return None
        recent_prices = self.price_history[-periods:]
        return sum(recent_prices) / len(recent_prices)


class Portfolio:
    """Manages the trading portfolio with cash and stock holdings"""
    
    def __init__(self, initial_cash: float = 10000.0):
        self.cash = initial_cash
        self.holdings: Dict[str, int] = {}  # symbol -> quantity
        self.transaction_history: List[Dict] = []
    
    def buy(self, symbol: str, quantity: int, price: float) -> bool:
        """Buy stocks if sufficient cash is available"""
        cost = quantity * price
        if cost > self.cash:
            return False
        
        self.cash -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.transaction_history.append({
            'action': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now()
        })
        return True
    
    def sell(self, symbol: str, quantity: int, price: float) -> bool:
        """Sell stocks if available in portfolio"""
        if self.holdings.get(symbol, 0) < quantity:
            return False
        
        self.cash += quantity * price
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        
        self.transaction_history.append({
            'action': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now()
        })
        return True
    
    def get_portfolio_value(self, stock_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value (cash + holdings)"""
        holdings_value = sum(
            quantity * stock_prices.get(symbol, 0)
            for symbol, quantity in self.holdings.items()
        )
        return self.cash + holdings_value
    
    def get_holdings_summary(self) -> Dict[str, int]:
        """Get current holdings"""
        return self.holdings.copy()


class TradingStrategy:
    """Base class for trading strategies"""
    
    def analyze(self, stock: Stock) -> Action:
        """Analyze stock and return trading action"""
        raise NotImplementedError


class MovingAverageCrossoverStrategy(TradingStrategy):
    """
    Simple Moving Average Crossover Strategy
    - Buy when short-term MA crosses above long-term MA
    - Sell when short-term MA crosses below long-term MA
    """
    
    def __init__(self, short_period: int = 5, long_period: int = 20):
        self.short_period = short_period
        self.long_period = long_period
    
    def analyze(self, stock: Stock) -> Action:
        """Make trading decision based on moving average crossover"""
        short_ma = stock.get_moving_average(self.short_period)
        long_ma = stock.get_moving_average(self.long_period)
        
        # Not enough data yet
        if short_ma is None or long_ma is None:
            return Action.HOLD
        
        # Check for crossover signals
        if short_ma > long_ma * 1.02:  # 2% threshold to avoid noise
            return Action.BUY
        elif short_ma < long_ma * 0.98:
            return Action.SELL
        
        return Action.HOLD


class StockDataSimulator:
    """Simulates stock price data for testing"""
    
    def __init__(self, symbols: List[str], initial_prices: Dict[str, float]):
        self.symbols = symbols
        self.stocks = {
            symbol: Stock(symbol, initial_prices.get(symbol, 100.0))
            for symbol in symbols
        }
    
    def simulate_price_update(self):
        """Simulate random price movements"""
        for symbol, stock in self.stocks.items():
            # Random walk: ±2% change
            change_percent = random.uniform(-0.02, 0.02)
            new_price = stock.current_price * (1 + change_percent)
            stock.update_price(new_price)
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        """Get stock by symbol"""
        return self.stocks.get(symbol)
    
    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all stocks"""
        return {symbol: stock.current_price for symbol, stock in self.stocks.items()}


class StockTradingAgent:
    """
    Autonomous Stock Trading Agent
    
    The agent monitors stock prices, applies trading strategies,
    and executes trades to manage a portfolio.
    """
    
    def __init__(
        self,
        portfolio: Portfolio,
        strategy: TradingStrategy,
        data_source: StockDataSimulator
    ):
        self.portfolio = portfolio
        self.strategy = strategy
        self.data_source = data_source
        self.trade_size = 10  # Number of shares per trade
    
    def run_trading_cycle(self):
        """Execute one trading cycle: analyze and trade"""
        # Update market data
        self.data_source.simulate_price_update()
        
        # Analyze each stock and make trading decisions
        current_prices = self.data_source.get_current_prices()
        
        for symbol in self.data_source.symbols:
            stock = self.data_source.get_stock(symbol)
            if stock is None:
                continue
            
            # Get trading signal from strategy
            action = self.strategy.analyze(stock)
            
            # Execute trade based on signal
            if action == Action.BUY:
                success = self.portfolio.buy(symbol, self.trade_size, stock.current_price)
                if success:
                    print(f"[BUY] {symbol}: {self.trade_size} shares @ ${stock.current_price:.2f}")
            
            elif action == Action.SELL:
                success = self.portfolio.sell(symbol, self.trade_size, stock.current_price)
                if success:
                    print(f"[SELL] {symbol}: {self.trade_size} shares @ ${stock.current_price:.2f}")
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        current_prices = self.data_source.get_current_prices()
        portfolio_value = self.portfolio.get_portfolio_value(current_prices)
        
        return {
            'cash': self.portfolio.cash,
            'holdings': self.portfolio.get_holdings_summary(),
            'portfolio_value': portfolio_value,
            'current_prices': current_prices
        }
    
    def print_status(self):
        """Print current status in a readable format"""
        status = self.get_status()
        print("\n" + "="*50)
        print("TRADING AGENT STATUS")
        print("="*50)
        print(f"Cash: ${status['cash']:.2f}")
        print(f"Portfolio Value: ${status['portfolio_value']:.2f}")
        print("\nHoldings:")
        if status['holdings']:
            for symbol, quantity in status['holdings'].items():
                price = status['current_prices'][symbol]
                value = quantity * price
                print(f"  {symbol}: {quantity} shares @ ${price:.2f} = ${value:.2f}")
        else:
            print("  None")
        print("\nCurrent Prices:")
        for symbol, price in status['current_prices'].items():
            print(f"  {symbol}: ${price:.2f}")
        print("="*50)


def main():
    """Example usage of the Stock Trading Agent"""
    print("Stock Trading Agent Demo\n")
    
    # Initialize components
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    initial_prices = {'AAPL': 150.0, 'GOOGL': 2800.0, 'MSFT': 300.0}
    
    portfolio = Portfolio(initial_cash=50000.0)
    strategy = MovingAverageCrossoverStrategy(short_period=5, long_period=20)
    data_source = StockDataSimulator(symbols, initial_prices)
    
    agent = StockTradingAgent(portfolio, strategy, data_source)
    
    # Warm up the price history
    print("Initializing market data...")
    for _ in range(25):
        data_source.simulate_price_update()
    
    # Run trading simulation
    print("Starting trading simulation...\n")
    agent.print_status()
    
    for cycle in range(1, 11):
        print(f"\n--- Trading Cycle {cycle} ---")
        agent.run_trading_cycle()
    
    # Final status
    agent.print_status()
    
    # Show transaction history
    print("\nTransaction History:")
    for i, tx in enumerate(portfolio.transaction_history, 1):
        print(f"{i}. {tx['action']} {tx['quantity']} {tx['symbol']} @ ${tx['price']:.2f}")


if __name__ == "__main__":
    main()
