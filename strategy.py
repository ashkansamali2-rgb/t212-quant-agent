import pandas as pd
import ledger

def evaluate_strategy(ticker, df):
    """
    High-Frequency Bollinger Band Mean Reversion Strategy:
    - BUY if current price < Lower_Band.
    - SELL if current price > Upper_Band.
    - CLOSE (flatten position) if we own the stock and price crosses back over the MA20.
    """
    if df is None or len(df) < 2:
        return {'action': 'HOLD'}

    latest = df.iloc[-1]
    previous = df.iloc[-2]
    latest_price = float(latest['Close'])
    positions = ledger.get_active_positions()
    
    # Required indicators check
    if 'MA20' not in df.columns or 'Upper_Band' not in df.columns or 'Lower_Band' not in df.columns:
        return {'action': 'HOLD'}

    # Handle potential NaN values
    if pd.isna(latest['MA20']) or pd.isna(latest['Upper_Band']) or pd.isna(latest['Lower_Band']):
        return {'action': 'HOLD'}

    # Strategy Logic
    if ticker in positions:
        # Exit logic for active positions
        if latest_price > latest['Upper_Band']:
            return {'action': 'SELL', 'reason': 'UPPER_BAND_TOUCH'}
        
        # Close if price crosses back over the MA20 (from below to above)
        if previous['Close'] < previous['MA20'] and latest_price >= latest['MA20']:
            return {'action': 'SELL', 'reason': 'MEAN_REVERSION_EXIT'}
            
        # Optional: Keep the trailing stop-loss from previous version for safety
        entry_price = positions[ticker]['price']
        if latest_price < entry_price * 0.975:
            return {'action': 'SELL', 'reason': 'STOP_LOSS'}
    else:
        # Entry logic
        if latest_price < latest['Lower_Band']:
            return {'action': 'BUY', 'reason': 'LOWER_BAND_TOUCH'}

    return {'action': 'HOLD'}
