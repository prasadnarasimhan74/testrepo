"""
Unit tests for the Stock Trading Agent
"""

import unittest
from stock_trading_agent import (
    Stock, Portfolio, Action, MovingAverageCrossoverStrategy,
    StockDataSimulator, StockTradingAgent
)


class TestStock(unittest.TestCase):
    """Test Stock class"""
    
    def test_stock_initialization(self):
        stock = Stock("AAPL", 150.0)
        self.assertEqual(stock.symbol, "AAPL")
        self.assertEqual(stock.current_price, 150.0)
        self.assertEqual(len(stock.price_history), 0)
    
    def test_update_price(self):
        stock = Stock("AAPL", 150.0)
        stock.update_price(155.0)
        self.assertEqual(stock.current_price, 155.0)
        self.assertEqual(len(stock.price_history), 1)
        self.assertEqual(stock.price_history[0], 150.0)
    
    def test_moving_average(self):
        stock = Stock("AAPL", 100.0)
        # Add price history
        for price in [100, 102, 104, 106, 108]:
            stock.update_price(price)
        
        # Test with 3 periods
        ma = stock.get_moving_average(3)
        self.assertIsNotNone(ma)
        self.assertAlmostEqual(ma, 104.0, places=2)
    
    def test_moving_average_insufficient_data(self):
        stock = Stock("AAPL", 100.0)
        stock.update_price(102.0)
        
        # Not enough data for 5-period MA
        ma = stock.get_moving_average(5)
        self.assertIsNone(ma)


class TestPortfolio(unittest.TestCase):
    """Test Portfolio class"""
    
    def test_portfolio_initialization(self):
        portfolio = Portfolio(10000.0)
        self.assertEqual(portfolio.cash, 10000.0)
        self.assertEqual(len(portfolio.holdings), 0)
    
    def test_buy_stock(self):
        portfolio = Portfolio(10000.0)
        success = portfolio.buy("AAPL", 10, 150.0)
        
        self.assertTrue(success)
        self.assertEqual(portfolio.cash, 8500.0)  # 10000 - 10*150
        self.assertEqual(portfolio.holdings["AAPL"], 10)
        self.assertEqual(len(portfolio.transaction_history), 1)
    
    def test_buy_insufficient_cash(self):
        portfolio = Portfolio(1000.0)
        success = portfolio.buy("AAPL", 10, 150.0)
        
        self.assertFalse(success)
        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(len(portfolio.holdings), 0)
    
    def test_sell_stock(self):
        portfolio = Portfolio(10000.0)
        portfolio.buy("AAPL", 10, 150.0)
        success = portfolio.sell("AAPL", 5, 160.0)
        
        self.assertTrue(success)
        self.assertEqual(portfolio.cash, 9300.0)  # 8500 + 5*160
        self.assertEqual(portfolio.holdings["AAPL"], 5)
    
    def test_sell_insufficient_shares(self):
        portfolio = Portfolio(10000.0)
        portfolio.buy("AAPL", 10, 150.0)
        success = portfolio.sell("AAPL", 15, 160.0)
        
        self.assertFalse(success)
        self.assertEqual(portfolio.holdings["AAPL"], 10)
    
    def test_portfolio_value(self):
        portfolio = Portfolio(10000.0)
        portfolio.buy("AAPL", 10, 150.0)
        portfolio.buy("GOOGL", 5, 2800.0)
        
        stock_prices = {"AAPL": 160.0, "GOOGL": 2900.0}
        value = portfolio.get_portfolio_value(stock_prices)
        
        # Cash: 10000 - 1500 - 14000 = -5500 (negative)
        # Actually: cash would be insufficient, let's fix the test
        portfolio = Portfolio(50000.0)
        portfolio.buy("AAPL", 10, 150.0)
        portfolio.buy("GOOGL", 5, 2800.0)
        
        value = portfolio.get_portfolio_value(stock_prices)
        # Cash: 50000 - (10*150) - (5*2800) = 50000 - 1500 - 14000 = 34500
        # Holdings value: 10*160 + 5*2900 = 1600 + 14500 = 16100
        # Total: 34500 + 16100 = 50600
        expected = 50600.0
        self.assertEqual(value, expected)


class TestMovingAverageCrossoverStrategy(unittest.TestCase):
    """Test Moving Average Crossover Strategy"""
    
    def test_hold_insufficient_data(self):
        strategy = MovingAverageCrossoverStrategy(short_period=5, long_period=20)
        stock = Stock("AAPL", 100.0)
        
        # Add some data but not enough for long MA
        for i in range(10):
            stock.update_price(100.0 + i)
        
        action = strategy.analyze(stock)
        self.assertEqual(action, Action.HOLD)
    
    def test_buy_signal(self):
        strategy = MovingAverageCrossoverStrategy(short_period=3, long_period=5)
        stock = Stock("AAPL", 100.0)
        
        # Create uptrend: prices going up
        for price in [100, 101, 102, 103, 104, 110, 115, 120]:
            stock.update_price(price)
        
        action = strategy.analyze(stock)
        # Should be BUY when short MA > long MA
        self.assertEqual(action, Action.BUY)


class TestStockDataSimulator(unittest.TestCase):
    """Test Stock Data Simulator"""
    
    def test_simulator_initialization(self):
        symbols = ["AAPL", "GOOGL"]
        initial_prices = {"AAPL": 150.0, "GOOGL": 2800.0}
        simulator = StockDataSimulator(symbols, initial_prices)
        
        self.assertEqual(len(simulator.stocks), 2)
        self.assertEqual(simulator.stocks["AAPL"].current_price, 150.0)
    
    def test_price_update(self):
        symbols = ["AAPL"]
        initial_prices = {"AAPL": 150.0}
        simulator = StockDataSimulator(symbols, initial_prices)
        
        initial_price = simulator.stocks["AAPL"].current_price
        simulator.simulate_price_update()
        new_price = simulator.stocks["AAPL"].current_price
        
        # Price should have changed
        self.assertNotEqual(initial_price, new_price)
        # Price should be within ±2% range
        self.assertGreater(new_price, initial_price * 0.98)
        self.assertLess(new_price, initial_price * 1.02)


class TestStockTradingAgent(unittest.TestCase):
    """Test Stock Trading Agent"""
    
    def test_agent_initialization(self):
        portfolio = Portfolio(10000.0)
        strategy = MovingAverageCrossoverStrategy()
        symbols = ["AAPL"]
        initial_prices = {"AAPL": 150.0}
        data_source = StockDataSimulator(symbols, initial_prices)
        
        agent = StockTradingAgent(portfolio, strategy, data_source)
        
        self.assertIsNotNone(agent.portfolio)
        self.assertIsNotNone(agent.strategy)
        self.assertIsNotNone(agent.data_source)
    
    def test_trading_cycle(self):
        portfolio = Portfolio(50000.0)
        strategy = MovingAverageCrossoverStrategy()
        symbols = ["AAPL"]
        initial_prices = {"AAPL": 150.0}
        data_source = StockDataSimulator(symbols, initial_prices)
        
        agent = StockTradingAgent(portfolio, strategy, data_source)
        
        # Warm up data
        for _ in range(25):
            data_source.simulate_price_update()
        
        # Run a trading cycle
        initial_cash = agent.portfolio.cash
        agent.run_trading_cycle()
        
        # Agent should have made some decision (cash might change or stay same)
        self.assertIsNotNone(agent.portfolio.cash)
    
    def test_get_status(self):
        portfolio = Portfolio(10000.0)
        strategy = MovingAverageCrossoverStrategy()
        symbols = ["AAPL", "GOOGL"]
        initial_prices = {"AAPL": 150.0, "GOOGL": 2800.0}
        data_source = StockDataSimulator(symbols, initial_prices)
        
        agent = StockTradingAgent(portfolio, strategy, data_source)
        status = agent.get_status()
        
        self.assertIn('cash', status)
        self.assertIn('holdings', status)
        self.assertIn('portfolio_value', status)
        self.assertIn('current_prices', status)
        self.assertEqual(status['cash'], 10000.0)


if __name__ == '__main__':
    unittest.main()
