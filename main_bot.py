import time
import logging
import schedule
import pytz
from datetime import datetime
import t212_client
from data_engine import DataEngine, get_top_gainers
from strategy import evaluate_strategy
import ledger

# --- Configuration ---
DRY_RUN = False  # Set to False to execute real trades
MAX_RISK_PER_TRADE_EURO = 25
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
    active_positions = ledger.get_active_positions()
    logging.info(f"Current active positions: {list(active_positions.keys())}")
    
    # Fetch dynamic universe (20 highest volume)
    dynamic_tickers = get_top_gainers()
    
    # Ensure active positions are evaluated even if they fall out of top 20
    universe = list(set(dynamic_tickers).union(set(active_positions.keys())))
    
    engine = DataEngine(universe)
    unrealized_pnl = 0.0
    
    for ticker in universe:
        try:
            df = engine.get_processed_data(ticker)
            if df is None or len(df) < 2:
                logging.warning(f"Insufficient data for {ticker}")
                continue
            
            result = evaluate_strategy(ticker, df)
            action = result['action']
            reason = result.get('reason', 'MA_CROSS')
            
            latest_price = float(df['Close'].iloc[-1])
            
            # Calculate unrealized PnL for active positions
            if ticker in active_positions:
                entry_price = active_positions[ticker]['price']
                quantity = active_positions[ticker]['quantity']
                unrealized_pnl += (latest_price - entry_price) * quantity

            logging.info(f"Ticker: {ticker} | Price: {latest_price:.2f} | Strategy Result: {action} ({reason})")

            if action in ['BUY', 'SELL']:
                logging.info(f"Signal triggered! Action: {action} for {ticker}")
                
                # Smart Execution Logic
                if action == 'SELL' and ticker not in active_positions:
                    logging.info(f"[SKIP] SELL signal for {ticker} but no position owned.")
                    continue
                    
                if action == 'BUY' and ticker in active_positions:
                    logging.info(f"[SKIP] BUY signal for {ticker} but position already exists.")
                    continue
                
                if not t212_client.validate_keys():
                    logging.error("API keys missing. Cannot execute trade.")
                    continue

                # Calculate risk-based position sizing
                per_share_risk = latest_price * 0.025
                quantity = round(MAX_RISK_PER_TRADE_EURO / per_share_risk, 2)

                # For sells, use the quantity we actually have in the ledger if available
                if action == 'SELL' and ticker in active_positions:
                    quantity = float(active_positions[ticker]['quantity'])

                success, response = t212_client.execute_t212_limit_order(
                    ticker=ticker,
                    action=action,
                    quantity=quantity,
                    limit_price=latest_price,
                    dry_run=DRY_RUN
                )
                
                if success:
                    logging.info(f"Trade successful for {ticker}: {response}")
                    if action == 'BUY':
                        ledger.add_position(ticker, latest_price, quantity)
                        logging.info(f"Logged BUY for {ticker} in ledger.")
                    elif action == 'SELL':
                        ledger.remove_position(ticker, latest_price)
                        logging.info(f"Removed {ticker} from ledger.")
                else:
                    logging.error(f"Trade failed for {ticker}: {response}")
                    
        except Exception as e:
            logging.error(f"Error processing {ticker}: {e}")

    # Log analytics at the end of cycle
    realized_pnl = ledger.get_realized_pnl()
    logging.info(f"--- Cycle Complete | Total Realized PnL: €{realized_pnl:.2f} | Total Unrealized PnL: €{unrealized_pnl:.2f} ---")

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
