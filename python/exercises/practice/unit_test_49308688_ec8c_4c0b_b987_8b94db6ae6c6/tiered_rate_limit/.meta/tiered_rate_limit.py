import threading
from functools import lru_cache

# Provided Interfaces (Assumed to exist and not modifiable in production)
def get_client_tier(client_id: str) -> str:
    # Simulate a remote call to fetch client tier.
    # In a real system, this would be a network call.
    return "Free"

def get_rate_limit(tier: str) -> int:
    # Simulate a remote call to fetch dynamic configuration.
    # In a real system, this would retrieve up-to-date rate limits.
    limits = {"Free": 10, "Basic": 100, "Premium": 1000}
    return limits.get(tier, 10)

def log_request(client_id: str, timestamp: int, allowed: bool):
    # Simulate asynchronous logging.
    # In a real system, logging would go to an external system.
    print(f"Client: {client_id}, Timestamp: {timestamp}, Allowed: {allowed}")

# Global state for the simulation.
# In a distributed system, this state would be managed by shared storage or caching (e.g., Redis).
client_lock = threading.Lock()
client_counters = {}

def is_request_allowed(client_id: str, timestamp: int) -> bool:
    """
    Determines if a request from a given client at the provided timestamp is allowed based
    on the client's tier and the configured rate limits. The time window is defined as each minute.
    
    Args:
        client_id (str): Unique identifier for the client.
        timestamp (int): Unix epoch time of the request in seconds.
        
    Returns:
        bool: True if the request is allowed; False if it is rate-limited.
    """
    # Define the current time window (each window spans 60 seconds)
    window = timestamp // 60

    # Fetch client tier and associated rate limit.
    tier = get_client_tier(client_id)
    limit = get_rate_limit(tier)
    
    allowed = False
    with client_lock:
        # Retrieve the current counter for the client. If not present, initialize it for the current window.
        current_window, count = client_counters.get(client_id, (window, 0))
        
        if current_window == window:
            if count < limit:
                count += 1
                allowed = True
            else:
                allowed = False
        else:
            # New time window: reset count.
            current_window = window
            count = 1
            allowed = True
        # Update the client's counter.
        client_counters[client_id] = (current_window, count)
    
    # Log the request attempt.
    log_request(client_id, timestamp, allowed)
    return allowed