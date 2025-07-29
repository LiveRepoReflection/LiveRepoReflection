import threading
import heapq

_lock = threading.Lock()
_event_map = {}
_event_heap = []

def schedule_event(event_id, execution_time, payload, priority):
    global _event_map, _event_heap
    with _lock:
        if event_id in _event_map:
            return False
        _event_map[event_id] = (execution_time, payload, priority)
        heapq.heappush(_event_heap, (execution_time, event_id))
    return True

def cancel_event(event_id):
    global _event_map
    with _lock:
        if event_id in _event_map:
            del _event_map[event_id]
            return True
    return False

def get_next_events(current_time, max_events):
    global _event_map, _event_heap
    eligible_candidates = []
    remaining_candidates = []
    with _lock:
        # Extract all eligible events from the heap
        while _event_heap and _event_heap[0][0] <= current_time:
            exec_time, event_id = heapq.heappop(_event_heap)
            if event_id not in _event_map:
                continue
            # Retrieve the current event details
            et, payload, priority = _event_map[event_id]
            eligible_candidates.append((priority, exec_time, event_id, payload))
        
        # Sort the eligible events:
        # First by descending priority and then by ascending execution time.
        eligible_candidates.sort(key=lambda x: (-x[0], x[1]))
        
        # Select up to max_events events to return and reinsert the remainder
        selected_candidates = eligible_candidates[:max_events]
        remaining_candidates = eligible_candidates[max_events:]
        
        for candidate in selected_candidates:
            _, _, event_id, _ = candidate
            if event_id in _event_map:
                del _event_map[event_id]
        
        for candidate in remaining_candidates:
            _, exec_time, event_id, _ = candidate
            heapq.heappush(_event_heap, (exec_time, event_id))
    
    result = [(event_id, payload) for (_, _, event_id, payload) in selected_candidates]
    return result