"""
Streamlit UI for Stock Trading Agent with Amazon Bedrock Integration

This app provides an interactive interface to:
- Configure and run the trading agent
- Visualize portfolio performance
- Monitor LLM-based trading decisions
- Track transaction history
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

from stock_trading_agent import (
    Portfolio, BedrockLLMStrategy, MovingAverageCrossoverStrategy,
    StockDataSimulator, StockTradingAgent, Action
)

# Page configuration
st.set_page_config(
    page_title="AI Stock Trading Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .buy-signal {
        color: #28a745;
        font-weight: bold;
    }
    .sell-signal {
        color: #dc3545;
        font-weight: bold;
    }
    .hold-signal {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.agent = None
    st.session_state.portfolio = None
    st.session_state.data_source = None
    st.session_state.strategy = None
    st.session_state.cycle_count = 0
    st.session_state.portfolio_history = []
    st.session_state.price_history_data = {}

def initialize_agent(initial_cash, stocks, strategy_type, risk_tolerance, use_bedrock):
    """Initialize the trading agent with selected parameters"""
    
    # Parse stock symbols and prices
    stock_dict = {}
    for stock in stocks.split(','):
        parts = stock.strip().split(':')
        if len(parts) == 2:
            symbol = parts[0].strip()
            try:
                price = float(parts[1].strip())
                stock_dict[symbol] = price
            except ValueError:
                st.error(f"Invalid price for {symbol}")
                return False
    
    if not stock_dict:
        st.error("Please provide at least one valid stock (format: SYMBOL:PRICE)")
        return False
    
    # Create components
    st.session_state.portfolio = Portfolio(initial_cash=initial_cash)
    st.session_state.data_source = StockDataSimulator(
        symbols=list(stock_dict.keys()),
        initial_prices=stock_dict
    )
    
    # Create strategy
    if strategy_type == "Amazon Bedrock LLM":
        st.session_state.strategy = BedrockLLMStrategy(
            risk_tolerance=risk_tolerance.lower(),
            use_bedrock=use_bedrock
        )
    else:
        st.session_state.strategy = MovingAverageCrossoverStrategy(
            short_period=5,
            long_period=20
        )
    
    # Create agent
    st.session_state.agent = StockTradingAgent(
        st.session_state.portfolio,
        st.session_state.strategy,
        st.session_state.data_source
    )
    
    # Warm up price history
    for _ in range(25):
        st.session_state.data_source.simulate_price_update()
    
    # Initialize tracking
    st.session_state.cycle_count = 0
    st.session_state.portfolio_history = []
    st.session_state.price_history_data = {symbol: [] for symbol in stock_dict.keys()}
    st.session_state.initialized = True
    
    return True

def run_trading_cycle():
    """Execute one trading cycle"""
    if not st.session_state.initialized:
        return
    
    # Run cycle
    st.session_state.agent.run_trading_cycle()
    st.session_state.cycle_count += 1
    
    # Track portfolio value
    status = st.session_state.agent.get_status()
    st.session_state.portfolio_history.append({
        'cycle': st.session_state.cycle_count,
        'value': status['portfolio_value'],
        'cash': status['cash']
    })
    
    # Track prices
    for symbol, price in status['current_prices'].items():
        st.session_state.price_history_data[symbol].append({
            'cycle': st.session_state.cycle_count,
            'price': price
        })

def create_portfolio_chart():
    """Create portfolio value chart"""
    if not st.session_state.portfolio_history:
        return None
    
    df = pd.DataFrame(st.session_state.portfolio_history)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['cycle'],
        y=df['value'],
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Portfolio Value Over Time',
        xaxis_title='Trading Cycle',
        yaxis_title='Portfolio Value ($)',
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_price_chart():
    """Create stock price chart"""
    if not st.session_state.price_history_data:
        return None
    
    fig = go.Figure()
    
    for symbol, data in st.session_state.price_history_data.items():
        if data:
            df = pd.DataFrame(data)
            fig.add_trace(go.Scatter(
                x=df['cycle'],
                y=df['price'],
                mode='lines',
                name=symbol,
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title='Stock Prices Over Time',
        xaxis_title='Trading Cycle',
        yaxis_title='Price ($)',
        hovermode='x unified',
        height=400
    )
    
    return fig

# Main app layout
st.markdown('<div class="main-header">📈 AI Stock Trading Agent</div>', unsafe_allow_html=True)
st.markdown("### Powered by Amazon Bedrock & Streamlit")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Initial settings
    initial_cash = st.number_input(
        "Initial Cash ($)",
        min_value=1000.0,
        max_value=1000000.0,
        value=50000.0,
        step=1000.0
    )
    
    stocks_input = st.text_input(
        "Stocks (SYMBOL:PRICE, ...)",
        value="AAPL:150.0, GOOGL:2800.0, MSFT:300.0",
        help="Enter stocks in format: SYMBOL:PRICE, separated by commas"
    )
    
    strategy_type = st.selectbox(
        "Trading Strategy",
        ["Amazon Bedrock LLM", "Moving Average Crossover"]
    )
    
    if strategy_type == "Amazon Bedrock LLM":
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive"]
        )
        
        use_bedrock = st.checkbox(
            "Use Real Bedrock API",
            value=False,
            help="Requires AWS credentials. Unchecked uses simulation."
        )
        
        if use_bedrock:
            st.info("ℹ️ Ensure AWS credentials are configured")
    else:
        risk_tolerance = "Moderate"
        use_bedrock = False
    
    st.divider()
    
    # Initialize button
    if st.button("🚀 Initialize Agent", type="primary", use_container_width=True):
        with st.spinner("Initializing trading agent..."):
            if initialize_agent(initial_cash, stocks_input, strategy_type, risk_tolerance, use_bedrock):
                st.success("✅ Agent initialized!")
            else:
                st.error("❌ Failed to initialize agent")
    
    # Trading controls
    if st.session_state.initialized:
        st.divider()
        st.header("🎮 Trading Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Run 1 Cycle", use_container_width=True):
                run_trading_cycle()
                st.rerun()
        
        with col2:
            if st.button("⏩ Run 10 Cycles", use_container_width=True):
                for _ in range(10):
                    run_trading_cycle()
                st.rerun()
        
        if st.button("🔄 Reset Agent", use_container_width=True):
            st.session_state.initialized = False
            st.rerun()
        
        st.divider()
        st.metric("Trading Cycles", st.session_state.cycle_count)

# Main content area
if not st.session_state.initialized:
    # Welcome screen
    st.info("👈 Configure your trading agent in the sidebar and click 'Initialize Agent' to begin")
    
    st.markdown("""
    ### Features
    
    - **Amazon Bedrock Integration**: Uses Claude LLM for intelligent trading decisions
    - **Real-time Visualization**: Track portfolio value and stock prices
    - **Multiple Strategies**: Choose between LLM-based or traditional technical analysis
    - **Risk Management**: Configurable risk tolerance levels
    - **Transaction History**: Complete audit trail of all trades
    
    ### How to Use
    
    1. Set your initial cash amount
    2. Enter stock symbols and prices (e.g., AAPL:150.0, GOOGL:2800.0)
    3. Choose your trading strategy
    4. Click "Initialize Agent"
    5. Run trading cycles and monitor performance
    """)
    
else:
    # Trading dashboard
    status = st.session_state.agent.get_status()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Cash",
            f"${status['cash']:,.2f}"
        )
    
    with col2:
        st.metric(
            "📊 Portfolio Value",
            f"${status['portfolio_value']:,.2f}"
        )
    
    with col3:
        initial_value = initial_cash
        profit = status['portfolio_value'] - initial_value
        profit_pct = (profit / initial_value) * 100
        st.metric(
            "📈 P&L",
            f"${profit:,.2f}",
            f"{profit_pct:+.2f}%"
        )
    
    with col4:
        st.metric(
            "🔄 Transactions",
            len(st.session_state.portfolio.transaction_history)
        )
    
    st.divider()
    
    # Charts
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio", "💹 Prices", "📝 Holdings", "🔍 Decisions"])
    
    with tab1:
        st.subheader("Portfolio Performance")
        chart = create_portfolio_chart()
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Run some trading cycles to see portfolio performance")
    
    with tab2:
        st.subheader("Stock Prices")
        chart = create_price_chart()
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Run some trading cycles to see price movements")
    
    with tab3:
        st.subheader("Current Holdings")
        holdings = status['holdings']
        if holdings:
            holdings_data = []
            for symbol, quantity in holdings.items():
                price = status['current_prices'][symbol]
                value = quantity * price
                holdings_data.append({
                    'Symbol': symbol,
                    'Quantity': quantity,
                    'Price': f"${price:.2f}",
                    'Value': f"${value:.2f}"
                })
            st.dataframe(pd.DataFrame(holdings_data), use_container_width=True, hide_index=True)
        else:
            st.info("No holdings yet")
        
        st.subheader("Transaction History")
        if st.session_state.portfolio.transaction_history:
            tx_data = []
            for tx in st.session_state.portfolio.transaction_history:
                action_class = "buy-signal" if tx['action'] == 'BUY' else "sell-signal"
                tx_data.append({
                    'Time': tx['timestamp'].strftime('%H:%M:%S'),
                    'Action': tx['action'],
                    'Symbol': tx['symbol'],
                    'Quantity': tx['quantity'],
                    'Price': f"${tx['price']:.2f}",
                    'Total': f"${tx['quantity'] * tx['price']:.2f}"
                })
            st.dataframe(pd.DataFrame(tx_data), use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet")
    
    with tab4:
        st.subheader("LLM Trading Decisions")
        
        if hasattr(st.session_state.strategy, 'get_decision_history'):
            decisions = st.session_state.strategy.get_decision_history()
            
            if decisions:
                # Recent decisions
                st.markdown("#### Recent Decisions")
                for decision in decisions[-10:]:
                    action = decision['action']
                    if action == Action.BUY:
                        action_class = "buy-signal"
                    elif action == Action.SELL:
                        action_class = "sell-signal"
                    else:
                        action_class = "hold-signal"
                    
                    with st.expander(f"{decision['symbol']} - {action.value} (Confidence: {decision['confidence']*100:.0f}%)"):
                        st.markdown(f"**Reasoning:** {decision['reasoning']}")
                        st.markdown(f"**Source:** {decision['source']}")
                        if 'metrics' in decision:
                            metrics = decision['metrics']
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Trend", metrics['trend'])
                            with col2:
                                st.metric("Volatility", f"{metrics['volatility']*100:.2f}%")
                            with col3:
                                st.metric("Momentum", f"{metrics['momentum']*100:.2f}%")
                
                # Summary statistics
                st.markdown("#### Decision Summary")
                buy_count = sum(1 for d in decisions if d['action'] == Action.BUY)
                sell_count = sum(1 for d in decisions if d['action'] == Action.SELL)
                hold_count = sum(1 for d in decisions if d['action'] == Action.HOLD)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("BUY Signals", buy_count)
                with col2:
                    st.metric("SELL Signals", sell_count)
                with col3:
                    st.metric("HOLD Signals", hold_count)
            else:
                st.info("No decisions made yet")
        else:
            st.info("LLM decisions are only available with Bedrock LLM strategy")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>AI Stock Trading Agent | Powered by Amazon Bedrock & Streamlit | For educational purposes only</small>
</div>
""", unsafe_allow_html=True)
