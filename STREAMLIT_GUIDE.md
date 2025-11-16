# Streamlit Trading Agent UI Guide

## Running the Application

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## Features

### 1. Configuration Panel (Left Sidebar)
- **Initial Cash**: Set starting capital ($1,000 - $1,000,000)
- **Stock Selection**: Enter stocks in format `SYMBOL:PRICE` (e.g., `AAPL:150.0, GOOGL:2800.0`)
- **Trading Strategy**: Choose between:
  - **Amazon Bedrock LLM**: AI-powered decisions using Claude
  - **Moving Average Crossover**: Traditional technical analysis
- **Risk Tolerance**: Set to Conservative, Moderate, or Aggressive
- **Bedrock API Toggle**: Use real AWS Bedrock or simulation mode

### 2. Trading Controls
- **Run 1 Cycle**: Execute single trading cycle
- **Run 10 Cycles**: Batch execute 10 cycles
- **Reset Agent**: Start fresh with new configuration

### 3. Dashboard Tabs

#### 📊 Portfolio Tab
- Real-time portfolio value chart
- Performance tracking over trading cycles
- Interactive Plotly visualization

#### 💹 Prices Tab
- Stock price movements over time
- Multi-stock price comparison
- Trend visualization

#### 📝 Holdings Tab
- Current stock holdings with quantities and values
- Complete transaction history
- Buy/sell timestamps and prices

#### 🔍 Decisions Tab
- LLM reasoning for each trade decision
- Confidence scores
- Market metrics (trend, volatility, momentum)
- Decision summary statistics

## Amazon Bedrock Integration

### Simulation Mode (Default)
- Works without AWS credentials
- Simulates LLM reasoning based on market metrics
- Perfect for testing and demo

### Real Bedrock Mode
1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Ensure Bedrock access in your AWS account

3. Check "Use Real Bedrock API" in the app

4. Agent will use Claude AI for real trading decisions

## Example Workflow

1. **Initialize**:
   - Set initial cash: $50,000
   - Add stocks: `AAPL:150.0, TSLA:200.0, MSFT:300.0`
   - Select "Amazon Bedrock LLM" strategy
   - Choose "Moderate" risk tolerance
   - Click "Initialize Agent"

2. **Trade**:
   - Click "Run 10 Cycles" to execute trades
   - Watch portfolio value change in real-time
   - Monitor LLM decisions in the Decisions tab

3. **Analyze**:
   - Review portfolio performance chart
   - Check transaction history
   - Read LLM reasoning for each decision
   - Adjust strategy and reset to try again

## Key Metrics

- **Cash**: Available funds for trading
- **Portfolio Value**: Total value (cash + holdings)
- **P&L**: Profit/Loss with percentage change
- **Transactions**: Total number of trades executed

## Tips

- Start with simulation mode to understand the system
- Use moderate risk tolerance for balanced trading
- Run multiple cycles to see pattern recognition
- Compare LLM vs traditional strategies
- Monitor confidence scores in LLM decisions
