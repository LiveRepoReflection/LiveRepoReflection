import time
import threading
from collections import defaultdict, deque

_lock = threading.Lock()
_requests = defaultdict(deque)

def allow_request(user_id, api_endpoint, rate_limit, time_window):
    current_time = time.time()
    key = (user_id, api_endpoint)
    with _lock:
        req_deque = _requests[key]
        while req_deque and req_deque[0] <= current_time - time_window:
            req_deque.popleft()
        if len(req_deque) < rate_limit:
            req_deque.append(current_time)
            return True
        return False