import csv
import os

CSV_FILE = 'active_positions.csv'

def _ensure_file_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ticker', 'price', 'quantity', 'status', 'sell_price'])

def _upgrade_file():
    _ensure_file_exists()
    rows = []
    needs_upgrade = False
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if header and 'status' not in header:
            needs_upgrade = True
            header.extend(['status', 'sell_price'])
            rows.append(header)
            for row in reader:
                row.extend(['OPEN', ''])
                rows.append(row)
        else:
            if header:
                rows.append(header)
            for row in reader:
                rows.append(row)
                
    if needs_upgrade:
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

def add_position(ticker, price, quantity):
    _upgrade_file()
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ticker, price, quantity, 'OPEN', ''])

def remove_position(ticker, sell_price=0.0):
    _upgrade_file()
    rows = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['ticker'] == ticker and row.get('status', 'OPEN') == 'OPEN':
                row['status'] = 'CLOSED'
                row['sell_price'] = str(sell_price)
            rows.append(row)
    
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['ticker', 'price', 'quantity', 'status', 'sell_price'])
        writer.writeheader()
        writer.writerows(rows)

def get_active_positions():
    """Returns a dict of ticker -> {'price': float, 'quantity': float}"""
    _upgrade_file()
    positions = {}
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('status', 'OPEN') == 'OPEN':
                positions[row['ticker']] = {
                    'price': float(row['price']),
                    'quantity': float(row['quantity'])
                }
    return positions

def get_realized_pnl():
    """Calculates realized profit/loss from closed positions."""
    _upgrade_file()
    pnl = 0.0
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('status') == 'CLOSED':
                try:
                    buy_price = float(row['price'])
                    sell_price = float(row['sell_price'])
                    quantity = float(row['quantity'])
                    pnl += (sell_price - buy_price) * quantity
                except (ValueError, TypeError):
                    pass
    return pnl
