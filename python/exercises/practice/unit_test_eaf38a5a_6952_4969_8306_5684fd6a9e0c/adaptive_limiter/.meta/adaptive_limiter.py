import time
import threading
import dataclasses
import os
import logging
from typing import Optional, Dict, Any, Union, Tuple
import math
import json
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclasses.dataclass
class RateLimitResult:
    """Class representing the result of a rate limit check."""
    allowed: bool
    limit: int
    remaining: int
    retry_after: Optional[float] = None
    request_id: Optional[str] = None


class SystemMetrics:
    """
    Class to collect and provide system metrics for adaptive rate limiting.
    In a real-world scenario, this would collect data from actual system monitoring tools.
    """
    def __init__(self):
        self._cpu_utilization = 0.0  # Between 0 and 1
        self._request_latency = 0.0  # In milliseconds
        self._error_rate = 0.0       # Between 0 and 1
        self._last_update = 0
        self._update_lock = threading.Lock()
        
    def update_metrics(self) -> None:
        """Update all metrics from their respective sources."""
        with self._update_lock:
            self._cpu_utilization = self._get_cpu_utilization_from_system()
            self._request_latency = self._get_request_latency_from_system()
            self._error_rate = self._get_error_rate_from_system()
            self._last_update = time.time()
            
    def _get_cpu_utilization_from_system(self) -> float:
        """
        Get the current CPU utilization from the system.
        
        In a production environment, this would retrieve real CPU metrics from an
        observability system like Prometheus, DataDog, etc.
        """
        # Mock implementation - in reality would get from actual system metrics
        try:
            # On Linux systems, we could read /proc/stat for real data
            if os.path.exists('/proc/stat'):
                return self._read_proc_stat()
            # Otherwise use a simulated value for testing/demo
            return random.uniform(0.3, 0.8)
        except Exception as e:
            logger.error(f"Error getting CPU utilization: {e}")
            return 0.5  # Default to a moderate utilization on error
            
    def _read_proc_stat(self) -> float:
        """Read CPU utilization from /proc/stat on Linux systems."""
        try:
            with open('/proc/stat', 'r') as f:
                for line in f:
                    if line.startswith('cpu '):
                        fields = line.strip().split()
                        user = int(fields[1])
                        nice = int(fields[2])
                        system = int(fields[3])
                        idle = int(fields[4])
                        iowait = int(fields[5]) if len(fields) > 5 else 0
                        irq = int(fields[6]) if len(fields) > 6 else 0
                        softirq = int(fields[7]) if len(fields) > 7 else 0
                        
                        idle_time = idle + iowait
                        non_idle_time = user + nice + system + irq + softirq
                        total = idle_time + non_idle_time
                        
                        # Return CPU utilization as a fraction (0-1)
                        return non_idle_time / total if total > 0 else 0.5
            return 0.5  # Default if we couldn't parse the file
        except Exception as e:
            logger.error(f"Error reading /proc/stat: {e}")
            return 0.5
            
    def _get_request_latency_from_system(self) -> float:
        """
        Get the current API request latency from the system.
        
        In a production environment, this would retrieve real latency metrics
        from an observability system like Prometheus, DataDog, etc.
        """
        # Mock implementation - in reality would get from actual system metrics
        # Return random latency between 50ms and 500ms
        return random.uniform(50, 500)
            
    def _get_error_rate_from_system(self) -> float:
        """
        Get the current API error rate from the system.
        
        In a production environment, this would retrieve real error rate metrics
        from an observability system like Prometheus, DataDog, etc.
        """
        # Mock implementation - in reality would get from actual system metrics
        # Return random error rate between 0% and 10%
        return random.uniform(0, 0.1)
            
    def get_cpu_utilization(self) -> float:
        """Get the most recent CPU utilization value."""
        # If data is stale (older than 5 seconds), fetch new data
        if time.time() - self._last_update > 5:
            self.update_metrics()
        return self._cpu_utilization
        
    def get_request_latency(self) -> float:
        """Get the most recent request latency value in milliseconds."""
        # If data is stale (older than 5 seconds), fetch new data
        if time.time() - self._last_update > 5:
            self.update_metrics()
        return self._request_latency
        
    def get_error_rate(self) -> float:
        """Get the most recent error rate value."""
        # If data is stale (older than 5 seconds), fetch new data
        if time.time() - self._last_update > 5:
            self.update_metrics()
        return self._error_rate


class AdaptiveThresholder:
    """
    Class that dynamically adjusts rate limits based on system metrics.
    Implements the adaptive thresholding algorithm.
    """
    
    def __init__(
        self, 
        base_limit: int,
        metrics: SystemMetrics,
        cpu_weight: float = 0.4,
        latency_weight: float = 0.4, 
        error_weight: float = 0.2,
        update_interval: int = 5,
        min_limit_percentage: float = 0.2,
        max_limit_percentage: float = 2.0,
        cpu_threshold: float = 0.7,
        latency_threshold: float = 300.0,  # 300ms
        error_threshold: float = 0.05  # 5% error rate
    ):
        """
        Initialize the adaptive thresholder.
        
        Args:
            base_limit: The base rate limit to adjust from
            metrics: SystemMetrics object for retrieving system metrics
            cpu_weight: Weight given to CPU utilization in the adjustment algorithm
            latency_weight: Weight given to latency in the adjustment algorithm
            error_weight: Weight given to error rate in the adjustment algorithm
            update_interval: How often to update the limit (seconds)
            min_limit_percentage: Minimum limit as percentage of base_limit
            max_limit_percentage: Maximum limit as percentage of base_limit
            cpu_threshold: CPU utilization threshold above which limits are reduced
            latency_threshold: Latency threshold above which limits are reduced
            error_threshold: Error rate threshold above which limits are reduced
        """
        self.base_limit = base_limit
        self.metrics = metrics
        self.cpu_weight = cpu_weight
        self.latency_weight = latency_weight
        self.error_weight = error_weight
        self.update_interval = update_interval
        self.min_limit_percentage = min_limit_percentage
        self.max_limit_percentage = max_limit_percentage
        self.cpu_threshold = cpu_threshold
        self.latency_threshold = latency_threshold
        self.error_threshold = error_threshold
        
        self.current_limit = base_limit
        self._running = False
        self._update_thread = None
        self._lock = threading.Lock()
        
        # Initialize historical metrics storage for trend analysis
        self.metric_history = {
            'cpu': [],
            'latency': [],
            'error_rate': []
        }
        self.history_size = 10  # Keep last 10 measurements
        
    def start(self):
        """Start the periodic update thread."""
        with self._lock:
            if not self._running:
                self._running = True
                self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
                self._update_thread.start()
                logger.info("Adaptive thresholder started")
        
    def stop(self):
        """Stop the periodic update thread."""
        with self._lock:
            if self._running:
                self._running = False
                if self._update_thread:
                    self._update_thread.join(timeout=2)
                logger.info("Adaptive thresholder stopped")
        
    def _update_loop(self):
        """Background thread to periodically update the rate limit."""
        while self._running:
            try:
                self._update_limit()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in thresholder update loop: {e}")
                time.sleep(1)  # Sleep briefly before retrying
                
    def _update_limit(self):
        """Update the current limit based on latest metrics."""
        try:
            # Update the metrics
            self.metrics.update_metrics()
            
            # Store metrics in history
            self._update_metric_history()
            
            # Calculate the new limit
            new_limit = self.calculate_adaptive_limit()
            
            # Bound the limit by min/max percentages
            min_limit = int(self.base_limit * self.min_limit_percentage)
            max_limit = int(self.base_limit * self.max_limit_percentage)
            new_limit = max(min_limit, min(new_limit, max_limit))
            
            # Update the current limit
            with self._lock:
                old_limit = self.current_limit
                self.current_limit = new_limit
                
            logger.info(f"Rate limit updated: {old_limit} -> {new_limit}")
            return new_limit
        except Exception as e:
            logger.error(f"Error updating limit: {e}")
            return self.current_limit  # Return current limit on error
            
    def _update_metric_history(self):
        """Update the metric history for trend analysis."""
        cpu = self.metrics.get_cpu_utilization()
        latency = self.metrics.get_request_latency()
        error_rate = self.metrics.get_error_rate()
        
        # Add current metrics to history
        self.metric_history['cpu'].append(cpu)
        self.metric_history['latency'].append(latency)
        self.metric_history['error_rate'].append(error_rate)
        
        # Trim history to maintain history size
        if len(self.metric_history['cpu']) > self.history_size:
            self.metric_history['cpu'] = self.metric_history['cpu'][-self.history_size:]
        if len(self.metric_history['latency']) > self.history_size:
            self.metric_history['latency'] = self.metric_history['latency'][-self.history_size:]
        if len(self.metric_history['error_rate']) > self.history_size:
            self.metric_history['error_rate'] = self.metric_history['error_rate'][-self.history_size:]
            
    def _calculate_trend_factor(self) -> float:
        """
        Calculate a trend factor based on historical metrics.
        
        Returns:
            A value between 0 and 1 where:
            - Values closer to 0 indicate worsening conditions (reduce limit)
            - Values closer to 1 indicate improving conditions (increase limit)
        """
        if (len(self.metric_history['cpu']) < 2 or 
            len(self.metric_history['latency']) < 2 or 
            len(self.metric_history['error_rate']) < 2):
            return 0.5  # Not enough data for trend, return neutral value
        
        # Calculate slopes (change over time)
        cpu_trend = (self.metric_history['cpu'][-1] - self.metric_history['cpu'][0]) / len(self.metric_history['cpu'])
        latency_trend = (self.metric_history['latency'][-1] - self.metric_history['latency'][0]) / len(self.metric_history['latency'])
        error_trend = (self.metric_history['error_rate'][-1] - self.metric_history['error_rate'][0]) / len(self.metric_history['error_rate'])
        
        # Normalize trends to -1 to 1 range
        # Positive trends are bad (increasing values), negative trends are good (decreasing values)
        max_cpu_change = 0.1  # 10% change is significant
        max_latency_change = 50  # 50ms change is significant
        max_error_change = 0.02  # 2% change is significant
        
        norm_cpu_trend = min(1, max(-1, cpu_trend / max_cpu_change)) * -1  # Invert so negative is bad
        norm_latency_trend = min(1, max(-1, latency_trend / max_latency_change)) * -1
        norm_error_trend = min(1, max(-1, error_trend / max_error_change)) * -1
        
        # Combine trends with weights
        combined_trend = (
            norm_cpu_trend * self.cpu_weight +
            norm_latency_trend * self.latency_weight +
            norm_error_trend * self.error_weight
        )
        
        # Convert to 0-1 range
        return (combined_trend + 1) / 2
            
    def calculate_adaptive_limit(self) -> int:
        """
        Calculate a new rate limit based on current system metrics.
        
        Returns:
            The adaptive rate limit as an integer
        """
        cpu = self.metrics.get_cpu_utilization()
        latency = self.metrics.get_request_latency()
        error_rate = self.metrics.get_error_rate()
        
        # Convert each metric to a factor between 0 and 1
        # where 0 means reduce limit to minimum and 1 means allow maximum limit
        
        # CPU factor: 1 when CPU is 0%, linearly decreasing to 0 when CPU reaches threshold
        cpu_factor = max(0, 1 - (cpu / self.cpu_threshold)) if self.cpu_threshold > 0 else 1
        
        # Latency factor: 1 when latency is 0, linearly decreasing to 0 at threshold
        latency_factor = max(0, 1 - (latency / self.latency_threshold)) if self.latency_threshold > 0 else 1
        
        # Error rate factor: 1 when error rate is 0, linearly decreasing to 0 at threshold
        error_factor = max(0, 1 - (error_rate / self.error_threshold)) if self.error_threshold > 0 else 1
        
        # Get trend factor (0-1)
        trend_factor = self._calculate_trend_factor()
        
        # Combine factors with weights
        combined_factor = (
            cpu_factor * self.cpu_weight + 
            latency_factor * self.latency_weight + 
            error_factor * self.error_weight
        )
        
        # Further adjust by trend factor - weight trend as 20% of decision
        trend_weight = 0.2
        final_factor = combined_factor * (1 - trend_weight) + trend_factor * trend_weight
        
        # Scale the base limit by the final factor
        min_limit = int(self.base_limit * self.min_limit_percentage)
        max_limit = int(self.base_limit * self.max_limit_percentage)
        
        # Calculate the adaptative limit
        adaptive_limit = int(min_limit + (max_limit - min_limit) * final_factor)
        
        logger.debug(f"Adaptive calculation: CPU={cpu:.2f} ({cpu_factor:.2f}), "
                    f"Latency={latency:.2f} ({latency_factor:.2f}), "
                    f"Error={error_rate:.3f} ({error_factor:.2f}), "
                    f"Trend={trend_factor:.2f}, "
                    f"Final={adaptive_limit}")
                    
        return adaptive_limit
        
    def get_current_limit(self) -> int:
        """Get the current rate limit."""
        with self._lock:
            return self.current_limit


class MockRedisClient:
    """
    A simple mock implementation of a Redis client for testing purposes.
    In production, you would use a real Redis client.
    """
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()
        
    def incr(self, key):
        with self.lock:
            if key not in self.data:
                self.data[key] = 0
            self.data[key] += 1
            return self.data[key]
            
    def get(self, key):
        with self.lock:
            return self.data.get(key, 0)
            
    def set(self, key, value, ex=None):
        with self.lock:
            self.data[key] = value
            
    def expire(self, key, seconds):
        # In a real implementation, this would set an expiration time
        pass
        
    def ttl(self, key):
        # In a real implementation, this would return the remaining time to live
        return 60  # Default ttl for tests


class DistributedRateLimiter:
    """
    Implements a distributed rate limiter using a fixed window algorithm.
    Uses Redis (or mock Redis for testing) for distributed counter storage.
    """
    
    def __init__(
        self,
        redis_client=None,
        thresholder=None,
        window_size=60,  # Window size in seconds
        request_id_prefix="req_"
    ):
        """
        Initialize the rate limiter.
        
        Args:
            redis_client: Redis client or compatible interface
            thresholder: AdaptiveThresholder object for dynamic limit adjustments
            window_size: Time window size in seconds for rate limiting
            request_id_prefix: Prefix for request IDs
        """
        # Use provided redis client or create a mock one for testing
        self.redis = redis_client or MockRedisClient()
        self.thresholder = thresholder
        self.window_size = window_size
        self.request_id_prefix = request_id_prefix
        self.request_counter = 0
        self.lock = threading.Lock()
        
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        with self.lock:
            self.request_counter += 1
            return f"{self.request_id_prefix}{int(time.time())}_{self.request_counter}"
            
    def _get_counter_key(self, user_id=None, endpoint=None) -> str:
        """
        Generate a Redis key for storing the rate limit counter.
        
        Args:
            user_id: Optional user ID for user-specific rate limiting
            endpoint: Optional endpoint for endpoint-specific rate limiting
            
        Returns:
            A string key for Redis storage
        """
        # Format depends on what granularity is being used
        if user_id and endpoint:
            return f"ratelimit:user:{user_id}:endpoint:{endpoint}:counter"
        elif user_id:
            return f"ratelimit:user:{user_id}:counter"
        elif endpoint:
            return f"ratelimit:endpoint:{endpoint}:counter"
        else:
            return "ratelimit:global:counter"
            
    def _get_window_key(self, user_id=None, endpoint=None) -> str:
        """
        Generate a Redis key for storing the current time window.
        
        Args:
            user_id: Optional user ID for user-specific rate limiting
            endpoint: Optional endpoint for endpoint-specific rate limiting
            
        Returns:
            A string key for Redis storage
        """
        # Format depends on what granularity is being used
        if user_id and endpoint:
            return f"ratelimit:user:{user_id}:endpoint:{endpoint}:window"
        elif user_id:
            return f"ratelimit:user:{user_id}:window"
        elif endpoint:
            return f"ratelimit:endpoint:{endpoint}:window"
        else:
            return "ratelimit:global:window"
            
    def _get_rate_limit(self, user_id=None, endpoint=None) -> int:
        """
        Get the current rate limit for the specified granularity.
        
        Args:
            user_id: Optional user ID for user-specific rate limiting
            endpoint: Optional endpoint for endpoint-specific rate limiting
            
        Returns:
            The current rate limit as an integer
        """
        # In a real implementation, we might have different base limits
        # for different users or endpoints.
        
        # If we have a thresholder, use its adaptive limit
        if self.thresholder:
            return self.thresholder.get_current_limit()
        
        # Otherwise use a default limit
        return 100  # Default limit
        
    def _get_current_window(self) -> int:
        """
        Get the current time window identifier.
        Windows are identified by the start time of the window.
        
        Returns:
            The current window identifier as an integer timestamp
        """
        # Calculate the start of the current window
        current_time = int(time.time())
        return current_time - (current_time % self.window_size)
            
    def check_rate_limit(self, user_id=None, endpoint=None) -> RateLimitResult:
        """
        Check if a request should be allowed or rate limited.
        
        Args:
            user_id: Optional user ID for user-specific rate limiting
            endpoint: Optional endpoint for endpoint-specific rate limiting
            
        Returns:
            A RateLimitResult object containing the result of the check
        """
        try:
            request_id = self._generate_request_id()
            current_window = self._get_current_window()
            counter_key = self._get_counter_key(user_id, endpoint)
            window_key = self._get_window_key(user_id, endpoint)
            
            # Check if we're in a new window
            stored_window = int(self.redis.get(window_key) or 0)
            if stored_window != current_window:
                # Reset counter for new window
                self.redis.set(counter_key, 0)
                self.redis.set(window_key, current_window, ex=self.window_size * 2)  # Double to ensure overlap
                
            # Get the rate limit
            rate_limit = self._get_rate_limit(user_id, endpoint)
            
            # Increment counter and check against limit
            counter = self.redis.incr(counter_key)
            
            # Ensure key expires after window
            self.redis.expire(counter_key, self.window_size * 2)  # Double to ensure overlap
            
            # Calculate remaining requests in this window
            remaining = max(0, rate_limit - counter)
            
            # Calculate when the limit will reset
            ttl = self.redis.ttl(counter_key)
            retry_after = ttl if ttl > 0 else self.window_size
            
            # Determine if request is allowed
            allowed = counter <= rate_limit
            
            return RateLimitResult(
                allowed=allowed,
                limit=rate_limit,
                remaining=remaining,
                retry_after=retry_after if not allowed else None,
                request_id=request_id
            )
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request on error
            return RateLimitResult(
                allowed=True,
                limit=0,
                remaining=0,
                request_id=request_id
            )


class RedisAdapter:
    """
    Adapter for Redis clients to handle connection errors and failover.
    This provides a level of fault tolerance for the rate limiter.
    """
    
    def __init__(
        self,
        redis_clients,
        retry_attempts=3,
        retry_delay=0.1
    ):
        """
        Initialize the Redis adapter with multiple Redis clients for redundancy.
        
        Args:
            redis_clients: List of Redis client objects
            retry_attempts: Number of retry attempts per operation
            retry_delay: Delay between retries in seconds
        """
        self.clients = redis_clients
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self._primary_index = 0
        self.lock = threading.Lock()
        
    def _execute_with_failover(self, operation, *args, **kwargs):
        """
        Execute a Redis operation with retry and failover logic.
        
        Args:
            operation: String name of the Redis operation to execute
            *args, **kwargs: Arguments to pass to the operation
            
        Returns:
            The result of the Redis operation
            
        Raises:
            Exception: If all Redis clients fail
        """
        # Try with the primary client first
        with self.lock:
            primary = self._primary_index
            
        for attempt in range(self.retry_attempts):
            client_index = (primary + attempt) % len(self.clients)
            client = self.clients[client_index]
            
            try:
                # Get the operation method from the client
                op_method = getattr(client, operation)
                # Execute the operation
                result = op_method(*args, **kwargs)
                
                # If successful, update primary client
                if client_index != primary:
                    with self.lock:
                        self._primary_index = client_index
                    logger.info(f"Switched to Redis client {client_index}")
                
                return result
            except Exception as e:
                logger.warning(f"Redis client {client_index} failed: {e}")
                time.sleep(self.retry_delay)
                
        # If we get here, all clients failed
        logger.error("All Redis clients failed")
        raise Exception("All Redis clients failed")
        
    # Implement Redis methods we need
    def incr(self, key):
        return self._execute_with_failover("incr", key)
        
    def get(self, key):
        return self._execute_with_failover("get", key)
        
    def set(self, key, value, ex=None):
        return self._execute_with_failover("set", key, value, ex=ex)
        
    def expire(self, key, seconds):
        return self._execute_with_failover("expire", key, seconds)
        
    def ttl(self, key):
        return self._execute_with_failover("ttl", key)


if __name__ == "__main__":
    # Simple demo of the rate limiter
    
    # Set up the metrics and thresholder
    metrics = SystemMetrics()
    thresholder = AdaptiveThresholder(
        base_limit=100,
        metrics=metrics,
        update_interval=2
    )
    thresholder.start()
    
    # Create the rate limiter
    limiter = DistributedRateLimiter(
        thresholder=thresholder,
        window_size=5  # Small window for demo purposes
    )
    
    # Simulate requests with increasing CPU usage
    print("Simulating requests with increasing CPU load:")
    for i in range(20):
        # Simulate increasing CPU load
        metrics._cpu_utilization = min(0.95, 0.2 + i * 0.04)
        
        result = limiter.check_rate_limit()
        print(f"Request {i+1}: CPU={metrics._cpu_utilization:.2f}, Limit={result.limit}, " +
              f"Remaining={result.remaining}, Allowed={result.allowed}")
        time.sleep(0.5)
    
    # Wait for all windows to clear
    print("\nWaiting for rate limit window to reset...")
    time.sleep(6)
    
    # Simulate requests with decreasing CPU usage
    print("\nSimulating requests with decreasing CPU load:")
    for i in range(20):
        # Simulate decreasing CPU load
        metrics._cpu_utilization = max(0.2, 0.9 - i * 0.04)
        
        result = limiter.check_rate_limit()
        print(f"Request {i+1}: CPU={metrics._cpu_utilization:.2f}, Limit={result.limit}, " +
              f"Remaining={result.remaining}, Allowed={result.allowed}")
        time.sleep(0.5)
        
    # Stop the thresholder before exiting
    thresholder.stop()