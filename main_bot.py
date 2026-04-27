import time
import logging
import schedule
import pytz
from datetime import datetime
import t212_client
from data_engine import DataEngine
from strategy import evaluate_strategy
import ledger

# --- Configuration ---
DRY_RUN = False  # Set to False to execute real trades
TICKERS = ["NVDA", "AAPL", "TSLA", "AMD", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "COIN"]
TRADE_QUANTITY = 1
LOG_FILE = "bot_execution.log"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def is_market_open():
    """
    Checks if the US market is open (9:30 AM - 4:00 PM EST, Monday-Friday).
    """
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Monday = 0, Sunday = 6
    if now.weekday() >= 5:
        return False
    
    start_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return start_time <= now <= end_time

def job():
    if not is_market_open():
        logging.info("Market is currently closed. Skipping execution.")
        return

    logging.info("--- Starting Strategy Evaluation Cycle ---")
    engine = DataEngine(TICKERS)
    
    for ticker in TICKERS:
        try:
            df = engine.get_processed_data(ticker)
            if df is None or len(df) < 2:
                logging.warning(f"Insufficient data for {ticker}")
                continue
            
            result = evaluate_strategy(df)
            action = result['action']
            
            latest_price = df['Close'].iloc[-1]
            logging.info(f"Ticker: {ticker} | Price: {latest_price:.2f} | Strategy Result: {action}")

            if action in ['BUY', 'SELL']:
                logging.info(f"Signal triggered! Action: {action} for {ticker}")
                
                if not t212_client.validate_keys():
                    logging.error("API keys missing. Cannot execute trade.")
                    continue

                success, response = t212_client.execute_t212_market_order(
                    ticker=ticker,
                    action=action,
                    quantity=TRADE_QUANTITY,
                    dry_run=DRY_RUN
                )
                
                if success:
                    logging.info(f"Trade successful for {ticker}: {response}")
                else:
                    logging.error(f"Trade failed for {ticker}: {response}")
                    
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")

def main():
    logging.info(f"Bot started. Dry Run: {DRY_RUN}")
    
    # Run once immediately on start
    job()
    
    # Schedule every 15 minutes
    schedule.every(15).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
g.info(f"Removed {ticker} from ledger.")
                else:
                    logging.error(f"Trade failed for {ticker}: {response}")
                    
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")

def main():
    logging.info(f"Bot started. Dry Run: {DRY_RUN}")
    
    # Run once immediately on start
    job()
    
    # Schedule every 15 minutes
    schedule.every(15).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
