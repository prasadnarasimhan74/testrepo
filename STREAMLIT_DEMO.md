# 📈 Stock Trading Agent - Streamlit UI Demo

## Application Interface

### Main Dashboard
```
============================================================
📈 AI Stock Trading Agent
Powered by Amazon Bedrock & Streamlit
============================================================

Sidebar Configuration:
┌─────────────────────────────────────┐
│ ⚙️ Configuration                     │
│                                     │
│ Initial Cash ($): 50,000            │
│ Stocks: AAPL:150.0, GOOGL:2800.0   │
│ Trading Strategy: Amazon Bedrock LLM│
│ Risk Tolerance: Moderate            │
│ ☐ Use Real Bedrock API             │
│                                     │
│ [🚀 Initialize Agent]               │
│                                     │
│ ─────────────────────────────────   │
│ 🎮 Trading Controls                 │
│ [▶️ Run 1 Cycle] [⏩ Run 10 Cycles] │
│ [🔄 Reset Agent]                    │
│                                     │
│ Trading Cycles: 45                  │
└─────────────────────────────────────┘

Main Dashboard (Tabs):
┌────────────────────────────────────────────────────────┐
│ [📊 Portfolio] [💹 Prices] [📝 Holdings] [🔍 Decisions]│
├────────────────────────────────────────────────────────┤
│                                                        │
│ Key Metrics:                                          │
│ ┌─────────────┬──────────────┬──────────┬────────────┐│
│ │💰 Cash      │📊 Portfolio  │📈 P&L    │🔄 Trans    ││
│ │$34,523.45   │$52,150.22    │+$2,150   │15          ││
│ │             │              │(+4.30%)  │            ││
│ └─────────────┴──────────────┴──────────┴────────────┘│
│                                                        │
│ Portfolio Value Over Time:                            │
│     $52k ┤                                    ╭──     │
│          │                               ╭────╯       │
│     $51k ┤                          ╭────╯            │
│          │                     ╭────╯                 │
│     $50k ┤────────────────╭────╯                      │
│          │                                            │
│     $49k ┤                                            │
│          └──────────────────────────────────────      │
│            0    10   20   30   40   50               │
│                   Trading Cycles                      │
└────────────────────────────────────────────────────────┘
```

### LLM Decisions Tab
```
┌────────────────────────────────────────────────────────┐
│ 🔍 LLM Trading Decisions                              │
├────────────────────────────────────────────────────────┤
│                                                        │
│ Recent Decisions:                                     │
│                                                        │
│ ▼ AAPL - BUY (Confidence: 80%)                       │
│   Reasoning: Strong uptrend with 6.2% momentum and   │
│   low volatility (1.5%). Good buying opportunity.    │
│   Source: simulated                                   │
│   Trend: uptrend | Volatility: 1.50% | Momentum: 6.2%│
│                                                        │
│ ▼ GOOGL - SELL (Confidence: 70%)                     │
│   Reasoning: Strong downtrend with -5.3% negative    │
│   momentum. Recommend selling to minimize losses.    │
│   Source: simulated                                   │
│   Trend: downtrend | Volatility: 2.1% | Momentum:-5.3│
│                                                        │
│ Decision Summary:                                     │
│ ┌──────────────┬──────────────┬──────────────┐       │
│ │ BUY Signals  │ SELL Signals │ HOLD Signals │       │
│ │      8       │      5       │     32       │       │
│ └──────────────┴──────────────┴──────────────┘       │
└────────────────────────────────────────────────────────┘
```

### Holdings & Transactions Tab
```
┌────────────────────────────────────────────────────────┐
│ 📝 Current Holdings                                    │
├────────────────────────────────────────────────────────┤
│ Symbol │ Quantity │ Price     │ Value                 │
│ AAPL   │ 50       │ $155.23   │ $7,761.50            │
│ MSFT   │ 30       │ $305.45   │ $9,163.50            │
│ GOOGL  │ 4        │ $2,756.31 │ $11,025.24           │
├────────────────────────────────────────────────────────┤
│ Transaction History                                    │
├────────────────────────────────────────────────────────┤
│ Time     │ Action │ Symbol │ Qty │ Price   │ Total   │
│ 14:23:15 │ BUY    │ AAPL   │ 10  │ $150.25 │ $1,502.5│
│ 14:24:32 │ BUY    │ MSFT   │ 10  │ $300.50 │ $3,005.0│
│ 14:25:01 │ SELL   │ GOOGL  │ 5   │ $2,801  │$14,005.0│
│ 14:26:18 │ BUY    │ AAPL   │ 20  │ $152.10 │ $3,042.0│
│ ...      │ ...    │ ...    │ ... │ ...     │ ...     │
└────────────────────────────────────────────────────────┘
```

## Key Features Demonstrated

✅ Real-time portfolio tracking
✅ Interactive charts with Plotly
✅ LLM decision transparency with reasoning
✅ Multi-strategy support (LLM vs Traditional)
✅ Risk tolerance configuration
✅ Detailed transaction history
✅ Performance metrics (P&L tracking)
✅ Amazon Bedrock integration (with fallback)

## Running the Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Streamlit app
streamlit run streamlit_app.py
```

The app will open at http://localhost:8501

## Amazon Bedrock Integration

- **Simulation Mode**: Works immediately without AWS setup
- **Real Mode**: Configure AWS credentials to use Claude AI
- Intelligent fallback if Bedrock unavailable
- Transparent source labeling (Bedrock vs Simulated)
