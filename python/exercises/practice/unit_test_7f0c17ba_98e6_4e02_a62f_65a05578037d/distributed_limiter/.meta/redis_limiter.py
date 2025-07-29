import time
import redis
import threading
from typing import Dict, Deque

class RedisRateLimiter:
    def __init__(self, max_requests: int, time_window_seconds: int, 
                 redis_host='localhost', redis_port=6379):
        self.max_requests = max_requests
        self.time_window = time_window_seconds
        self.redis = redis.StrictRedis(host=redis_host, port=redis_port)
        self.lock = threading.Lock()
        
    def allow_request(self, client_id: str, request) -> bool:
        current_time = time.time()
        request_time = request.timestamp if hasattr(request, 'timestamp') else current_time
        
        with self.lock:
            # Use Redis sorted set for tracking requests
            key = f"ratelimit:{client_id}"
            
            # Remove old requests
            self.redis.zremrangebyscore(key, '-inf', request_time - self.time_window)
            
            # Count current requests
            count = self.redis.zcard(key)
            
            if count < self.max_requests:
                self.redis.zadd(key, {str(request_time): request_time})
                self.redis.expire(key, self.time_window)
                return True
            return False
    
    def clear_client(self, client_id: str):
        with self.lock:
            self.redis.delete(f"ratelimit:{client_id}")