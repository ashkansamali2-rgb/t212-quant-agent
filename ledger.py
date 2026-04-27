import csv
import os

CSV_FILE = 'active_positions.csv'

def _ensure_file_exists():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ticker', 'price', 'quantity'])

def add_position(ticker, price, quantity):
    _ensure_file_exists()
    remove_position(ticker)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ticker, price, quantity])

def remove_position(ticker):
    _ensure_file_exists()
    rows = []
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['ticker'] != ticker:
                rows.append(row)
    
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['ticker', 'price', 'quantity'])
        writer.writeheader()
        writer.writerows(rows)

def get_active_positions():
    """Returns a dict of ticker -> {'price': float, 'quantity': float}"""
    _ensure_file_exists()
    positions = {}
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            positions[row['ticker']] = {
                'price': float(row['price']),
                'quantity': float(row['quantity'])
            }
    return positions
