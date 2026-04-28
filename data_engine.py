import yfinance as yf
import pandas as pd

def get_top_gainers():
    """
    Uses yfinance to pull a list of the 20 highest-volume stocks 
    currently trading in the US market.
    """
    try:
        response = yf.screen("most_actives")
        if 'quotes' in response:
            symbols = [q['symbol'] for q in response['quotes']]
            return symbols[:20]
    except Exception as e:
        print(f"[!] Error fetching top gainers: {e}")
    # Fallback list if screener fails or structure changes
    return ["NVDA", "AAPL", "TSLA", "AMD", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "COIN"]

def calculate_adx(df, window=14):
    """
    Computes Average Directional Index (ADX) to measure trend strength.
    """
    if df is None or len(df) < window * 2:
        if df is not None:
            df['ADX_14'] = 0
        return df
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # TR
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # DM+ and DM-
    up = high - high.shift(1)
    down = low.shift(1) - low
    
    pos_dm = up.where((up > down) & (up > 0), 0.0)
    neg_dm = down.where((down > up) & (down > 0), 0.0)
    
    # Smoothed TR, DM+, DM-
    tr_smooth = tr.ewm(alpha=1/window, adjust=False).mean()
    pos_dm_smooth = pos_dm.ewm(alpha=1/window, adjust=False).mean()
    neg_dm_smooth = neg_dm.ewm(alpha=1/window, adjust=False).mean()
    
    # DI+ and DI-
    pos_di = 100 * (pos_dm_smooth / tr_smooth)
    neg_di = 100 * (neg_dm_smooth / tr_smooth)
    
    # DX and ADX
    dx = 100 * (pos_di - neg_di).abs() / (pos_di + neg_di)
    adx = dx.ewm(alpha=1/window, adjust=False).mean()
    
    df['ADX_14'] = adx
    return df

class DataEngine:
    def __init__(self, tickers):
        self.tickers = tickers

    def fetch_data(self, ticker, period="1d", interval="1m"):
        """
        Fetch historical and live price data for a specified ticker.
        Columns: Open, High, Low, Close, Volume
        """
        print(f"[*] Fetching data for {ticker}...")
        df = yf.download(ticker, period=period, interval=interval)
        if df.empty:
            print(f"[!] No data found for {ticker}")
            return None
        
        # Flatten multi-index columns if necessary
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Ensure standard column names
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        return df

    def add_indicators(self, df):
        """
        Append columns for the 20-period MA and Bollinger Bands (Upper/Lower).
        """
        if df is None or len(df) < 20:
            return df
        
        # Calculate MA20
        df['MA20'] = df['Close'].rolling(window=20).mean()
        
        # Calculate Standard Deviation
        df['STD20'] = df['Close'].rolling(window=20).std()
        
        # Calculate Bollinger Bands
        df['Upper_Band'] = df['MA20'] + (2 * df['STD20'])
        df['Lower_Band'] = df['MA20'] - (2 * df['STD20'])
        
        return df

    def get_processed_data(self, ticker):
        df = self.fetch_data(ticker)
        if df is not None:
            df = self.add_indicators(df)
        return df
