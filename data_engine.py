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

class DataEngine:
    def __init__(self, tickers):
        self.tickers = tickers

    def fetch_data(self, ticker, period="5d", interval="5m"):
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
        Append columns for the 9-period SMA, 21-period SMA, and 14-period RSI.
        """
        if df is None or len(df) < 21:
            return df
        
        # Calculate SMAs
        df['SMA_9'] = df['Close'].rolling(window=9).mean()
        df['SMA_21'] = df['Close'].rolling(window=21).mean()
        
        # Calculate RSI (14-period)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0))
        loss = (-delta.where(delta < 0, 0))
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        
        return df

    def get_processed_data(self, ticker):
        df = self.fetch_data(ticker)
        if df is not None:
            df = self.add_indicators(df)
        return df
