# T212 Quant Agent (High-Frequency Mean Reversion)

An automated, quantitative day-trading system built for the Trading 212 API, now pivoted to a high-frequency Bollinger Band strategy.

## Core Architecture

This project is built using:
- **Python**: The core language powering the trading logic and orchestration.
- **pandas**: Used for fast, vectorized mathematical operations and technical indicator calculations.
- **yfinance**: Utilized for fetching live market data and dynamic stock screening.

## The Strategy (Mean Reversion)

The agent operates on a systematic, rule-based mean reversion approach:
- **Timeframe**: Evaluates the market on a **1-minute** interval (60-second heartbeat).
- **Dynamic Universe**: Continuously scans for the top 20 most active US stocks to ensure sufficient liquidity and volatility.
- **Indicators**: 
    - **MA20**: 20-period Simple Moving Average.
    - **Bollinger Bands**: MA20 +/- (2 * 20-period Standard Deviation).
- **Logic**:
    - **BUY**: If current price < Lower Band.
    - **SELL (Profit Take)**: If current price > Upper Band.
    - **CLOSE (Mean Exit)**: If a position is held and price crosses back over the MA20 (the Mean).

## Risk Management (The Armor)

Strict capital protection rules are enforced automatically:
- **Risk-Adjusted Sizing**: Position sizing is dynamically calculated based on volatility to risk a maximum of exactly €25 per trade.
- **Trailing Stop-Loss**: A strict 2.5% trailing stop-loss is actively tracked as a safety fallback.
- **Limit Orders**: Executes limit orders strictly at the current evaluated market price to prevent slippage.
- **End-Of-Day (EOD) Liquidation**: A specialized function flattens the entire portfolio at **3:55 PM EST**, ensuring zero overnight gap risk.

## System State & Memory

The bot maintains a persistent, local state:
- **Ledger Tracking**: `ledger.py` reads and writes to an `active_positions.csv` file to track all open and closed trades.
- **Execution Protection**: Prevents illegal short-selling, stops "doubling up" on existing positions, and tracks Realized/Unrealized PnL.

## Setup & Execution

### Prerequisites
1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Configuration
Create a `.env` file with your Trading 212 credentials:
```env
T212_API_KEY=your_api_key_here
T212_API_SECRET=your_api_secret_here
```

### Execution
Start the engine:
```bash
./.venv/bin/python main_bot.py
```
