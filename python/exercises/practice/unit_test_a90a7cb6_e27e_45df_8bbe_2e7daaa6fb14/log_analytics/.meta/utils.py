import time
import random
import json
from datetime import datetime

def generate_sample_logs(count=100):
    services = ["auth_service", "payment_service", "inventory_service", 
               "shipping_service", "user_service", "notification_service"]
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    messages = [
        "User login successful",
        "Transaction processed",
        "Failed to authenticate",
        "Database connection timeout",
        "Cache miss occurred",
        "Request processed in {} ms".format(random.randint(1, 500)),
        "Resource not found",
        "Invalid input parameters",
        "Starting service initialization",
        "Service shutdown completed"
    ]
    
    logs = []
    for _ in range(count):
        logs.append({
            "timestamp": int(time.time()) - random.randint(0, 86400),
            "service_id": random.choice(services),
            "log_level": random.choice(levels),
            "message": random.choice(messages).format(random.randint(1, 1000))
        })
    
    return logs

def save_logs_to_file(logs, filename):
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=2)

def load_logs_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')