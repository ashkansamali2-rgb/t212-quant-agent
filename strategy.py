def evaluate_strategy(df):
    """
    Strict Moving Average Crossover strategy:
    - If 50 SMA crosses strictly ABOVE the 200 SMA AND the RSI is < 70: Return {'action': 'BUY'}.
    - If 50 SMA crosses strictly BELOW the 200 SMA: Return {'action': 'SELL'}.
    - Otherwise: Return {'action': 'HOLD'}.
    """
    if df is None or len(df) < 2:
        return {'action': 'HOLD'}
    
    # Required indicators check
    if 'SMA_50' not in df.columns or 'SMA_200' not in df.columns or 'RSI_14' not in df.columns:
        return {'action': 'HOLD'}

    # We need at least the last two rows to detect a crossover
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Handle potential NaN values
    if any(pd.isna([latest['SMA_50'], latest['SMA_200'], previous['SMA_50'], previous['SMA_200']])):
        return {'action': 'HOLD'}

    action = 'HOLD'

    # 50 SMA crosses strictly ABOVE the 200 SMA
    is_cross_above = (previous['SMA_50'] <= previous['SMA_200']) and (latest['SMA_50'] > latest['SMA_200'])
    
    # 50 SMA crosses strictly BELOW the 200 SMA
    is_cross_below = (previous['SMA_50'] >= previous['SMA_200']) and (latest['SMA_50'] < latest['SMA_200'])

    if is_cross_above and latest['RSI_14'] < 70:
        action = 'BUY'
    elif is_cross_below:
        action = 'SELL'

    return {'action': action}

import pandas as pd # Needed for pd.isna
