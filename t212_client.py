import os
import base64
import requests
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

T212_API_BASE = "https://demo.trading212.com/api/v0/equity"

def get_auth_header():
    """Implements strict HTTP Basic Authentication encoding."""
    key = os.getenv("T212_API_KEY")
    secret = os.getenv("T212_API_SECRET")
    if not key or not secret:
        return None
    # Precise ASCII encoding as requested
    creds = f"{key}:{secret}"
    encoded_creds = base64.b64encode(creds.encode('ascii')).decode('ascii')
    return {"Authorization": f"Basic {encoded_creds}"}

def validate_keys():
    """Validates that the required API keys are present."""
    if not os.getenv("T212_API_KEY") or not os.getenv("T212_API_SECRET"):
        print("[ERROR] T212_API_KEY or T212_API_SECRET not found in environment variables.")
        return False
    return True

def execute_t212_limit_order(ticker, action, quantity, limit_price, dry_run=False):
    """
    Targets Demo Invest endpoint with _US_EQ suffix.
    action: "BUY" or "SELL"
    """
    mapped_ticker = f"{ticker}_US_EQ"
    url = f"{T212_API_BASE}/orders/limit"
    headers = get_auth_header()
    if headers is None:
        print("[ERROR] Could not generate auth headers.")
        return False
    
    headers["Content-Type"] = "application/json"
    
    # Buy: positive, Sell: negative
    # Mapped from strategy actions to API quantities
    final_quantity = abs(quantity) if action == "BUY" else -abs(quantity)
    payload = {
        "ticker": mapped_ticker, 
        "quantity": final_quantity,
        "limitPrice": limit_price
    }

    if dry_run:
        msg = f"[DRY RUN] Would execute {action} order for {mapped_ticker} with quantity {final_quantity} at limit {limit_price}"
        print(msg)
        return True, msg

    print(f"[*] Executing {action} order for {mapped_ticker}...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201, 202]:
            print(f"[SUCCESS] Order filled for {mapped_ticker}")
            return True, response.json()
        else:
            print(f"[FAILED] API {response.status_code}: {response.text}")
            return False, response.text
    except Exception as e:
        print(f"[ERROR] API connection failed: {e}")
        return False, str(e)
