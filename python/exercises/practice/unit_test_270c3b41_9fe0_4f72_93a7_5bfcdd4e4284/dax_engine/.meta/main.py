import json
import sys
from .dax_engine import process_order, cancel_order

def main():
    """Main function to process orders from stdin"""
    for line in sys.stdin:
        try:
            order = json.loads(line.strip())
            trades = process_order(order)
            print(json.dumps(trades))
        except json.JSONDecodeError:
            # Handle invalid JSON
            print("[]")
        except Exception as e:
            # Handle other errors
            print(f"Error: {e}")
            print("[]")

if __name__ == "__main__":
    main()