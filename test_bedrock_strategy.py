"""
Test script for Bedrock LLM strategy
"""

from stock_trading_agent import (
    Portfolio, BedrockLLMStrategy, StockDataSimulator, StockTradingAgent
)

print("="*60)
print("Testing Amazon Bedrock LLM Trading Strategy")
print("="*60)

# Initialize
symbols = ['AAPL', 'TSLA']
initial_prices = {'AAPL': 150.0, 'TSLA': 200.0}

portfolio = Portfolio(initial_cash=20000.0)
strategy = BedrockLLMStrategy(
    risk_tolerance="moderate",
    use_bedrock=False  # Simulation mode
)

data_source = StockDataSimulator(symbols, initial_prices)
agent = StockTradingAgent(portfolio, strategy, data_source)

# Warm up
print("\nInitializing market data...")
for _ in range(25):
    data_source.simulate_price_update()

print("\nRunning trading simulation with LLM strategy...\n")
agent.print_status()

# Run cycles
for cycle in range(1, 11):
    print(f"\n{'='*60}")
    print(f"Cycle {cycle}")
    print('='*60)
    agent.run_trading_cycle()

# Final status
print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
agent.print_status()

# Show decisions
print("\n" + "="*60)
print("LLM DECISION SUMMARY")
print("="*60)
decisions = strategy.get_decision_history()
buy_count = sum(1 for d in decisions if d['action'].value == 'BUY')
sell_count = sum(1 for d in decisions if d['action'].value == 'SELL')
hold_count = len(decisions) - buy_count - sell_count

print(f"Total Decisions: {len(decisions)}")
print(f"  BUY: {buy_count}")
print(f"  SELL: {sell_count}")
print(f"  HOLD: {hold_count}")

print("\nRecent Decisions with Reasoning:")
for decision in decisions[-5:]:
    if decision['action'].value != 'HOLD':
        print(f"\n{decision['symbol']} - {decision['action'].value}")
        print(f"  Confidence: {decision['confidence']*100:.0f}%")
        print(f"  Reasoning: {decision['reasoning']}")

print("\n" + "="*60)
