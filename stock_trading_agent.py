"""
Stock Trading Agent

A simple autonomous trading agent that can analyze stock data,
make trading decisions based on strategies, and manage a portfolio.
"""

import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Amazon Bedrock imports (optional - will work without them in demo mode)
try:
    import boto3
    from botocore.exceptions import ClientError
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Warning: boto3 not available. Running in simulation mode.")


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


class BedrockLLMStrategy(TradingStrategy):
    """
    Amazon Bedrock LLM-Based Trading Strategy
    
    Uses Amazon Bedrock's Claude model to analyze stock data and make trading decisions.
    Falls back to simulated LLM reasoning if Bedrock is not available.
    """
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", 
                 risk_tolerance: str = "moderate",
                 use_bedrock: bool = True):
        """
        Initialize Bedrock LLM strategy
        
        Args:
            model_id: Amazon Bedrock model ID
            risk_tolerance: 'conservative', 'moderate', or 'aggressive'
            use_bedrock: Whether to use actual Bedrock API (requires AWS credentials)
        """
        self.model_id = model_id
        self.risk_tolerance = risk_tolerance
        self.use_bedrock = use_bedrock and BEDROCK_AVAILABLE
        self.decision_history: List[Dict] = []
        
        if self.use_bedrock:
            try:
                self.bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=os.environ.get('AWS_REGION', 'us-east-1')
                )
                print(f"✓ Connected to Amazon Bedrock with model: {model_id}")
            except Exception as e:
                print(f"⚠ Could not connect to Bedrock: {e}. Using simulation mode.")
                self.use_bedrock = False
    
    def _calculate_metrics(self, stock: Stock) -> Dict:
        """Calculate stock metrics for analysis"""
        if len(stock.price_history) < 2:
            return {
                'trend': 'insufficient_data',
                'volatility': 0.0,
                'momentum': 0.0,
                'price_change_pct': 0.0
            }
        
        # Calculate trend
        recent_prices = stock.price_history[-5:] if len(stock.price_history) >= 5 else stock.price_history
        price_changes = [recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))]
        avg_change = sum(price_changes) / len(price_changes) if price_changes else 0
        
        trend = "uptrend" if avg_change > 0 else ("downtrend" if avg_change < 0 else "neutral")
        
        # Calculate volatility
        lookback = min(10, len(stock.price_history))
        recent = stock.price_history[-lookback:]
        avg_price = sum(recent) / len(recent)
        variance = sum((p - avg_price) ** 2 for p in recent) / len(recent)
        volatility = (variance ** 0.5) / avg_price if avg_price > 0 else 0.0
        
        # Calculate momentum
        old_price = stock.price_history[-lookback] if len(stock.price_history) >= lookback else stock.price_history[0]
        momentum = (stock.current_price - old_price) / old_price if old_price > 0 else 0.0
        
        # Price change percentage
        if len(stock.price_history) >= 1:
            price_change_pct = (stock.current_price - stock.price_history[-1]) / stock.price_history[-1]
        else:
            price_change_pct = 0.0
        
        return {
            'trend': trend,
            'volatility': volatility,
            'momentum': momentum,
            'price_change_pct': price_change_pct
        }
    
    def _call_bedrock(self, prompt: str) -> str:
        """Call Amazon Bedrock Claude model"""
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return self._simulate_llm_response(prompt)
    
    def _simulate_llm_response(self, prompt: str) -> str:
        """Simulate LLM response when Bedrock is not available"""
        # Extract metrics from prompt to make intelligent decision
        if "momentum" in prompt.lower() and "%" in prompt:
            # Parse the data from prompt
            if "uptrend" in prompt.lower() and "5." in prompt:
                return "BUY|0.75|Strong uptrend with good momentum. Low volatility suggests stable buying opportunity."
            elif "downtrend" in prompt.lower() and "-5" in prompt:
                return "SELL|0.70|Downtrend detected with negative momentum. Recommend selling to minimize losses."
        
        return "HOLD|0.50|Market conditions unclear. Recommend holding position and monitoring."
    
    def _create_prompt(self, stock: Stock, metrics: Dict) -> str:
        """Create prompt for LLM analysis"""
        price_history_str = ", ".join([f"${p:.2f}" for p in stock.price_history[-10:]]) if stock.price_history else "N/A"
        
        prompt = f"""You are a professional stock trading analyst. Analyze the following stock data and provide a trading recommendation.

Stock: {stock.symbol}
Current Price: ${stock.current_price:.2f}
Recent Price History (last 10): {price_history_str}

Market Metrics:
- Trend: {metrics['trend']}
- Volatility: {metrics['volatility']*100:.2f}%
- Momentum: {metrics['momentum']*100:.2f}%
- Recent Price Change: {metrics['price_change_pct']*100:.2f}%

Risk Tolerance: {self.risk_tolerance}

Based on this data, should I BUY, SELL, or HOLD this stock?

Respond in the following format:
ACTION|CONFIDENCE|REASONING

Where:
- ACTION is one of: BUY, SELL, HOLD
- CONFIDENCE is a number between 0 and 1
- REASONING is a brief explanation (max 100 words)

Example: BUY|0.85|Strong uptrend with low volatility indicates good buying opportunity."""

        return prompt
    
    def analyze(self, stock: Stock) -> Action:
        """Analyze stock using Bedrock LLM or simulation"""
        metrics = self._calculate_metrics(stock)
        
        if metrics['trend'] == 'insufficient_data':
            self.decision_history.append({
                'symbol': stock.symbol,
                'action': Action.HOLD,
                'confidence': 0.3,
                'reasoning': 'Insufficient data for analysis',
                'source': 'rule-based'
            })
            return Action.HOLD
        
        # Create prompt and get LLM response
        prompt = self._create_prompt(stock, metrics)
        
        if self.use_bedrock:
            response = self._call_bedrock(prompt)
        else:
            response = self._simulate_llm_response(prompt)
        
        # Parse response
        try:
            parts = response.strip().split('|')
            action_str = parts[0].strip().upper()
            confidence = float(parts[1].strip()) if len(parts) > 1 else 0.5
            reasoning = parts[2].strip() if len(parts) > 2 else "No reasoning provided"
            
            # Convert to Action enum
            if action_str == 'BUY':
                action = Action.BUY
            elif action_str == 'SELL':
                action = Action.SELL
            else:
                action = Action.HOLD
                
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            action = Action.HOLD
            confidence = 0.5
            reasoning = "Error parsing response"
        
        # Store decision
        decision = {
            'symbol': stock.symbol,
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'metrics': metrics,
            'source': 'bedrock' if self.use_bedrock else 'simulated',
            'timestamp': datetime.now()
        }
        self.decision_history.append(decision)
        
        # Print decision if not HOLD
        if action != Action.HOLD:
            source_label = "🤖 BEDROCK LLM" if self.use_bedrock else "🔮 SIMULATED LLM"
            print(f"\n[{source_label} - {stock.symbol}]")
            print(f"  Decision: {action.value}")
            print(f"  Confidence: {confidence*100:.0f}%")
            print(f"  Reasoning: {reasoning}")
        
        return action
    
    def get_decision_history(self) -> List[Dict]:
        """Get all decision history"""
        return self.decision_history.copy()



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
