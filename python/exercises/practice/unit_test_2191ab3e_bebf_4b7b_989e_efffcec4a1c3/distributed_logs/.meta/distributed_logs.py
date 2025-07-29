import threading

# Global in-memory storage for logs
LOG_STORE = []
# Lock for thread-safe operations on the LOG_STORE
store_lock = threading.Lock()

def clear_logs():
    """
    Clears all stored logs.
    """
    global LOG_STORE
    with store_lock:
        LOG_STORE = []

def ingest_log(log_entry):
    """
    Ingests a log entry into the system.
    
    log_entry: dictionary with keys:
        - timestamp (int)
        - service_name (str)
        - log_level (str)
        - message (str)
        - trace_id (str or None, optional)
        - metadata (dict, optional)
    """
    # Ensure required keys exist; if metadata or trace_id not provided, set to default.
    new_entry = {
        "timestamp": log_entry.get("timestamp"),
        "service_name": log_entry.get("service_name"),
        "log_level": log_entry.get("log_level"),
        "message": log_entry.get("message"),
        "trace_id": log_entry.get("trace_id") if "trace_id" in log_entry else None,
        "metadata": log_entry.get("metadata") if "metadata" in log_entry else {}
    }
    with store_lock:
        LOG_STORE.append(new_entry)

def query_logs(timestamp_range=None, service_name=None, log_level=None, message_contains=None, trace_id=None, metadata_filter=None, page=1, page_size=10):
    """
    Queries the stored logs based on provided criteria.
    
    Parameters:
    - timestamp_range: tuple (start, end) in milliseconds (inclusive)
    - service_name: string to filter logs by service name
    - log_level: list of strings; log's level must be one of these
    - message_contains: string; case-insensitive substring search in the message
    - trace_id: string; filter logs with this trace id
    - metadata_filter: dict; each key-value pair must match the log's metadata.
        For each key, if the filter's value is not None, the log's metadata must contain 
        that key and have exactly that value. If the filter's value is None, then the log 
        qualifies if the key does not exist in its metadata or its value is None.
    - page: integer, page number starting from 1
    - page_size: integer, number of items per page
    
    Returns:
    - List of logs matching the criteria, sorted by timestamp ascending.
    """
    with store_lock:
        # Make a copy of logs for query stability
        logs = LOG_STORE[:]
    
    filtered = []
    for log in logs:
        # Check timestamp range
        if timestamp_range is not None:
            start, end = timestamp_range
            if log["timestamp"] < start or log["timestamp"] > end:
                continue

        # Check service_name
        if service_name is not None:
            if log["service_name"] != service_name:
                continue

        # Check log_level; expecting log_level as a list of string values.
        if log_level is not None:
            if log["log_level"] not in log_level:
                continue

        # Check message_contains; case-insensitive search
        if message_contains is not None:
            if message_contains.lower() not in log["message"].lower():
                continue

        # Check trace_id
        if trace_id is not None:
            if log["trace_id"] != trace_id:
                continue

        # Check metadata_filter
        if metadata_filter is not None:
            metadata = log.get("metadata", {})
            match = True
            for key, value in metadata_filter.items():
                if value is not None:
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                else:  # value is None
                    # If the key exists and is not None, then does not match
                    if key in metadata and metadata[key] is not None:
                        match = False
                        break
            if not match:
                continue

        # If all filters passed, add to the filtered list.
        filtered.append(log)
    
    # Sort results by timestamp ascending.
    filtered.sort(key=lambda x: x["timestamp"])
    
    # Pagination
    if page < 1:
        page = 1
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated = filtered[start_index:end_index]
    return paginated