import re
import json
from duckduckgo_search import DDGS
from mlx_lm import load, generate

# Configuration
WATCHLIST = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]
MODEL_PATH = "mlx-community/Qwen3.6-27B-mxfp4" # Exact model requested by user

def get_stock_news(ticker):
    """Extracts top 3 news snippets for a given ticker using DuckDuckGo."""
    print(f"[*] Sourcing news for {ticker}...")
    with DDGS() as ddgs:
        results = ddgs.text(f"{ticker} stock news today", max_results=3)
        snippets = [r['body'] for r in results]
    return "\n".join(snippets)

def call_llm(model, tokenizer, prompt):
    """Helper to generate text from the MLX model."""
    response = generate(model, tokenizer, prompt=prompt, verbose=False, max_tokens=1000)
    return response

def execute_t212_trade(ticker, shares):
    """Dummy function for Trading 212 execution."""
    print(f"[TRADE CONFIRMED] Executed order: {shares:.4f} shares of {ticker}")

def kelly_criterion(probability):
    """
    Basic Kelly Criterion stub.
    Calculates fraction of bankroll to wager.
    Formula: f* = (p*b - q) / b
    Assuming b = 1 (even money bet for simplicity in this stub)
    """
    p = probability / 100.0
    q = 1 - p
    b = 1 
    f_star = (p * b - q) / b
    return max(0, f_star) # Return 0 if negative edge

def run_syndicate(ticker, news_context, model, tokenizer):
    """Multi-agent logic: Bull, Bear, and Judge."""
    
    # 1. Bull Agent
    bull_prompt = f"""
    <system>Act as a bullish Wall Street analyst.</system>
    <context>{news_context}</context>
    <task>Write a 1-paragraph thesis on why {ticker} will close green today based on the news above.</task>
    """
    print(f"[+] Bull Agent analyzing {ticker}...")
    bull_thesis = call_llm(model, tokenizer, bull_prompt)

    # 2. Bear Agent
    bear_prompt = f"""
    <system>Act as a ruthless short-seller.</system>
    <context>{news_context}</context>
    <task>Write a 1-paragraph thesis on why {ticker} will drop today based on the news above.</task>
    """
    print(f"[-] Bear Agent analyzing {ticker}...")
    bear_thesis = call_llm(model, tokenizer, bear_prompt)

    # 3. Judge Agent
    judge_prompt = f"""
    <system>Act as a Quantitative Analyst.</system>
    <bull_thesis>{bull_thesis}</bull_thesis>
    <bear_thesis>{bear_thesis}</bear_thesis>
    <task>
    Read both theses. Output a brief 3-sentence summary of the mathematical/market reality. 
    Then, exit all <think> tags and output your final probability calculation on the last line exactly like this: 
    FINAL_PROBABILITY: [XX]%
    </task>
    """
    print(f"[!] Judge Agent delivering verdict for {ticker}...")
    judge_output = call_llm(model, tokenizer, judge_prompt)
    
    return judge_output

def main():
    print(f"--- Quant Agent Auto-Pilot Initializing ---")
    
    # Load Model
    print(f"[*] Loading model: {MODEL_PATH}...")
    model, tokenizer = load(MODEL_PATH)

    for ticker in WATCHLIST:
        print(f"\n{'='*40}")
        print(f"Processing: {ticker}")
        
        # Sourcing
        news = get_stock_news(ticker)
        
        # Syndicate Processing
        verdict = run_syndicate(ticker, news, model, tokenizer)
        print(f"\nJudge Output:\n{verdict}")

        # Parse Probability
        match = re.search(r"FINAL_PROBABILITY: \[?(\d+)\]?%", verdict)
        if match:
            prob = int(match.group(1))
            edge = abs(prob - 50)
            
            print(f"Detected Probability: {prob}% | Calculated Edge: {edge}%")

            if edge > 15:
                # Calculate size using Kelly (using the probability of the dominant direction)
                # If prob > 50, we go long. If prob < 50, we'd theoretically short (but Kelly here is for position size).
                # We'll treat prob as the confidence in the primary direction.
                win_prob = prob if prob > 50 else (100 - prob)
                fractional_size = kelly_criterion(win_prob)
                
                # Mock bankroll/shares calculation
                # For demo: 1.0 fractional size = 10 shares
                shares_to_buy = fractional_size * 10 
                
                if shares_to_buy > 0:
                    execute_t212_trade(ticker, shares_to_buy)
                else:
                    print(f"[IDLE] Edge detected but Kelly fraction too low.")
            else:
                print(f"[IDLE] Edge ({edge}%) below 15% threshold. No trade.")
        else:
            print("[ERROR] Could not parse FINAL_PROBABILITY from Judge.")

if __name__ == "__main__":
    main()
