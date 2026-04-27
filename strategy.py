import pandas as pd # Needed for pd.isna
import ledger

def evaluate_strategy(ticker, df):
    """
    Fast Day-Trading Moving Average Crossover strategy:
    - If SMA_9 crosses strictly ABOVE SMA_21 AND RSI_14 < 70: Return {'action': 'BUY'}.
    - If SMA_9 crosses strictly BELOW SMA_21: Return {'action': 'SELL'}.
    - Otherwise: Return {'action': 'HOLD'}.
    """
    if df is None or len(df) < 2:
        return {'action': 'HOLD'}

    latest_price = df['Close'].iloc[-1]
    positions = ledger.get_active_positions()
    
    # Trailing Stop-Loss: Drop > 2.5% from entry price
    if ticker in positions:
        entry_price = positions[ticker]['price']
        if latest_price < entry_price * 0.975:
            return {'action': 'SELL', 'reason': 'STOP_LOSS'}
    
    # Required indicators check
    if 'SMA_9' not in df.columns or 'SMA_21' not in df.columns or 'RSI_14' not in df.columns:
        return {'action': 'HOLD'}

    # We need at least the last two rows to detect a crossover
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Handle potential NaN values
    if any(pd.isna([latest['SMA_9'], latest['SMA_21'], previous['SMA_9'], previous['SMA_21']])):
        return {'action': 'HOLD'}

    action = 'HOLD'

    # SMA_9 crosses strictly ABOVE SMA_21
    is_cross_above = (previous['SMA_9'] <= previous['SMA_21']) and (latest['SMA_9'] > latest['SMA_21'])
    
    # SMA_9 crosses strictly BELOW SMA_21
    is_cross_below = (previous['SMA_9'] >= previous['SMA_21']) and (latest['SMA_9'] < latest['SMA_21'])

    if is_cross_above and latest['RSI_14'] < 70 and latest.get('ADX_14', 0) > 25:
        action = 'BUY'
    elif is_cross_below:
        action = 'SELL'

    return {'action': action}
