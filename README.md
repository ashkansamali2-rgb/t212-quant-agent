# T212 Quant Agent

An automated, quantitative day-trading system built for the Trading 212 API.

## Core Architecture

This project is built using:
- **Python**: The core language powering the trading logic and orchestration.
- **pandas**: Used for fast, vectorized mathematical operations and technical indicator calculations.
- **yfinance**: Utilized for fetching live market data and dynamic stock screening.

## The Strategy (The Brain)

The agent operates on a systematic, rule-based approach:
- **Timeframe**: Evaluates the market on a 5-minute interval.
- **Dynamic Universe**: Continuously scans for the top 20 most active US stocks to ensure sufficient liquidity and volatility.
- **Momentum Detection**: Utilizes a fast 9-period and 21-period Simple Moving Average (SMA) crossover system.
- **Trend Strength**: Incorporates an Average Directional Index (ADX) filter. Buy signals are only validated if the ADX is strictly greater than 25, preventing "whipsawing" and false signals in flat, ranging markets.

## Risk Management (The Armor)

Strict capital protection rules are enforced automatically on every single trade:
- **Risk-Adjusted Sizing**: Position sizing is dynamically calculated based on volatility to risk a maximum of exactly €25 per trade.
- **Trailing Stop-Loss**: A strict 2.5% trailing stop-loss is actively tracked to cut losses early if a trade moves against the position.
- **Limit Orders**: Executes limit orders strictly at the current evaluated market price to prevent adverse execution slippage.
- **End-Of-Day (EOD) Liquidation**: A specialized function flattens the entire portfolio between 3:45 PM and 4:00 PM EST, ensuring zero overnight gap risk.

## System State & Memory

The bot maintains a persistent, local state to ensure reliable and safe execution across reboots:
- **Ledger Tracking**: `ledger.py` reads and writes to an `active_positions.csv` file to track all open and closed trades.
- **Execution Protection**: This state memory prevents illegal short-selling (selling assets not owned), stops the bot from "doubling up" on existing positions, and acts as the source of truth for calculating Realized and Unrealized PnL.

## Setup & Execution

### Prerequisites
1. Clone the repository to your local environment.
2. Create a virtual environment and install the required dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Configuration
Create a `.env` file in the root directory with your Trading 212 Demo or Live API credentials:
```env
T212_API_KEY=your_api_key_here
T212_API_SECRET=your_api_secret_here
```

### Execution
Start the quantitative trading engine:
```bash
./.venv/bin/python main_bot.py
```
