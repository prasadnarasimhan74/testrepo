"""
Advanced example of the Stock Trading Agent with more active trading
"""

from stock_trading_agent import (
    Portfolio, MovingAverageCrossoverStrategy,
    StockDataSimulator, StockTradingAgent
)


def main():
    """Run an extended trading simulation"""
    print("Stock Trading Agent - Extended Simulation\n")
    
    # Initialize with fewer stocks for more focused trading
    symbols = ['TSLA']
    initial_prices = {'TSLA': 200.0}
    
    portfolio = Portfolio(initial_cash=20000.0)
    # Use shorter periods for more active trading
    strategy = MovingAverageCrossoverStrategy(short_period=3, long_period=8)
    data_source = StockDataSimulator(symbols, initial_prices)
    
    agent = StockTradingAgent(portfolio, strategy, data_source)
    agent.trade_size = 5  # Trade 5 shares at a time
    
    # Warm up the price history
    print("Initializing market data...")
    for _ in range(15):
        data_source.simulate_price_update()
    
    print("Starting extended trading simulation with 50 cycles...\n")
    agent.print_status()
    
    # Run more cycles to see trading activity
    for cycle in range(1, 51):
        if cycle % 10 == 0:
            print(f"\n--- Trading Cycle {cycle} ---")
        agent.run_trading_cycle()
        
        # Print status every 10 cycles
        if cycle % 10 == 0:
            agent.print_status()
    
    # Final summary
    print("\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    
    status = agent.get_status()
    initial_value = 20000.0
    final_value = status['portfolio_value']
    profit = final_value - initial_value
    profit_pct = (profit / initial_value) * 100
    
    print(f"Initial Portfolio Value: ${initial_value:.2f}")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    print(f"Profit/Loss: ${profit:.2f} ({profit_pct:+.2f}%)")
    print(f"\nTotal Transactions: {len(portfolio.transaction_history)}")
    
    # Show transaction summary
    buy_count = sum(1 for tx in portfolio.transaction_history if tx['action'] == 'BUY')
    sell_count = sum(1 for tx in portfolio.transaction_history if tx['action'] == 'SELL')
    print(f"  Buys: {buy_count}")
    print(f"  Sells: {sell_count}")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    main()
