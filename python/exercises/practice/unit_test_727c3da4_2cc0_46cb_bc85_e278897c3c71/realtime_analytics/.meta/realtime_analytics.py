import time
from collections import defaultdict

# Global data structure to store events for each category.
# Each category maps to a list of events. Each event is a tuple: (timestamp, event_type)
_events_by_category = defaultdict(list)

# Allowed event types.
_allowed_event_types = {"click", "view", "purchase"}

# Sliding window duration in milliseconds (5 minutes)
_SLIDING_WINDOW_MS = 300000

def current_time_ms():
    return int(time.time() * 1000)

def ingest_event(event):
    """
    Ingest a single event. If the event is valid, store it in the global data structure.
    Valid event must have keys: 'timestamp', 'user_id', 'product_id', 'category_id', 'event_type'
    and event_type must be one of the allowed types.
    """
    required_keys = {"timestamp", "user_id", "product_id", "category_id", "event_type"}
    if not required_keys.issubset(event):
        return
    if event["event_type"] not in _allowed_event_types:
        return
    try:
        timestamp = int(event["timestamp"])
    except (ValueError, TypeError):
        return
    category_id = event["category_id"]
    # Append the event as a tuple (timestamp, event_type)
    _events_by_category[category_id].append((timestamp, event["event_type"]))

def get_current_metrics(category_id):
    """
    Retrieve aggregated metrics (clicks, views, purchases) for the given category
    using the sliding window of the last 5 minutes based on the current system time.
    """
    now = current_time_ms()
    window_start = now - _SLIDING_WINDOW_MS
    counts = {"clicks": 0, "views": 0, "purchases": 0}
    for timestamp, event_type in _events_by_category.get(category_id, []):
        if timestamp >= window_start and timestamp <= now:
            if event_type == "click":
                counts["clicks"] += 1
            elif event_type == "view":
                counts["views"] += 1
            elif event_type == "purchase":
                counts["purchases"] += 1
    return counts

def get_historical_metrics(category_id, start_timestamp, end_timestamp):
    """
    Retrieve aggregated historical metrics (clicks, views, purchases) for the given category
    within the specified time range [start_timestamp, end_timestamp].
    """
    counts = {"clicks": 0, "views": 0, "purchases": 0}
    for timestamp, event_type in _events_by_category.get(category_id, []):
        if timestamp >= start_timestamp and timestamp <= end_timestamp:
            if event_type == "click":
                counts["clicks"] += 1
            elif event_type == "view":
                counts["views"] += 1
            elif event_type == "purchase":
                counts["purchases"] += 1
    return counts

def get_top_k_categories(k):
    """
    Retrieve the top k categories with the highest number of purchase events
    in the current sliding window.
    Returns a list of tuples (category_id, purchase_count) sorted in descending order
    by purchase_count.
    """
    now = current_time_ms()
    window_start = now - _SLIDING_WINDOW_MS
    category_purchase_counts = []
    for category, events in _events_by_category.items():
        count = 0
        for timestamp, event_type in events:
            if event_type == "purchase" and window_start <= timestamp <= now:
                count += 1
        if count > 0:
            category_purchase_counts.append((category, count))
    # Sort by purchase count descending, and then by category id for consistent ordering
    category_purchase_counts.sort(key=lambda x: (-x[1], x[0]))
    return category_purchase_counts[:k]

def reset():
    """
    Reset the internal state. This is primarily for testing purposes.
    """
    global _events_by_category
    _events_by_category = defaultdict(list)