import heapq
from collections import defaultdict

def aggregate_transactions(worker_ids, start_time, end_time, fetch_log):
    """
    Aggregate and deduplicate transactions from multiple worker nodes within a time window.
    
    Args:
        worker_ids: List of worker node IDs to fetch logs from
        start_time: Start timestamp (ms since epoch) of the time window
        end_time: End timestamp (ms since epoch) of the time window
        fetch_log: Function that takes a worker_id and returns its transaction log
    
    Returns:
        List of unique transactions within the time window, ordered by timestamp
    """
    # Dictionary to track the earliest version of each transaction
    tx_dict = defaultdict(dict)
    
    # Min-heap to maintain global ordering
    min_heap = []
    
    # Process each worker's log
    for worker_id in worker_ids:
        try:
            for tx in fetch_log(worker_id):
                tx_id = tx["transaction_id"]
                timestamp = tx["timestamp"]
                
                # Skip transactions outside the time window
                if timestamp < start_time or timestamp > end_time:
                    continue
                
                # Keep only the earliest version of each transaction
                if tx_id not in tx_dict or timestamp < tx_dict[tx_id]["timestamp"]:
                    tx_dict[tx_id] = {
                        "transaction_id": tx_id,
                        "timestamp": timestamp,
                        "payload": tx["payload"]
                    }
                    
                    # Push to heap (timestamp as priority, tx_id as tiebreaker)
                    heapq.heappush(min_heap, (timestamp, tx_id, tx_dict[tx_id]))
                    
        except Exception as e:
            # Handle potential errors in fetching logs
            print(f"Error processing worker {worker_id}: {str(e)}")
            continue
    
    # Extract transactions from heap in order
    result = []
    while min_heap:
        _, tx_id, tx = heapq.heappop(min_heap)
        # Verify this is still the current version (in case of updates)
        if tx_id in tx_dict and tx_dict[tx_id]["timestamp"] == tx["timestamp"]:
            result.append(tx_dict[tx_id])
            # Remove from dict to prevent duplicates
            del tx_dict[tx_id]
    
    return result