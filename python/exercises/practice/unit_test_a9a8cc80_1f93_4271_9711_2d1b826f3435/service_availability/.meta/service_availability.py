import time
import threading

CACHE_TTL = 60.0
DISCOUNT_PER_PROMO = 10.0

# Global cache and lock for thread-safe caching
cache = {}
cache_lock = threading.Lock()


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=1.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'
        self.lock = threading.Lock()

    def call(self, func, *args, **kwargs):
        with self.lock:
            if self.state == 'open':
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    # Transition to half-open state
                    self.state = 'half-open'
                else:
                    raise Exception("Circuit open")
        try:
            result = func(*args, **kwargs)
        except Exception as ex:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = 'open'
            raise ex
        else:
            with self.lock:
                # Reset the breaker on successful call.
                self.failure_count = 0
                self.state = 'closed'
            return result


def call_with_retry(func, retries=3, initial_delay=0.05, multiplier=2, *args, **kwargs):
    delay = initial_delay
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            if i == retries - 1:
                raise ex
            time.sleep(delay)
            delay *= multiplier


class InventoryService:
    circuit_breaker = CircuitBreaker()

    @staticmethod
    def checkAvailability(product_id):
        def _check():
            # Default simulated behavior: product is in stock.
            return True
        return InventoryService.circuit_breaker.call(_check)


class PricingService:
    circuit_breaker = CircuitBreaker()

    @staticmethod
    def getPrice(product_id):
        def _get():
            # Default simulated behavior: return base price.
            return 100.0
        return PricingService.circuit_breaker.call(_get)


class PromotionService:
    circuit_breaker = CircuitBreaker()

    @staticmethod
    def getPromotions(product_id):
        def _get():
            # Default simulated behavior: no promotions.
            return []
        return PromotionService.circuit_breaker.call(_get)


def check_product_availability(product_id):
    """
    Check product availability by querying InventoryService, PricingService,
    and PromotionService with caching, retries, and circuit breakers.

    Returns:
        tuple: (availability: bool, final_price: float, promotions: list[str])
            - availability: True if the product is in stock and pricing is available.
            - final_price: The base price after deducting a fixed discount per promotion.
            - promotions: List of promotion names returned by the PromotionService.
    
    Design Decisions:
        - Caching: The result for each product_id is cached with a TTL of CACHE_TTL seconds
          to reduce load on backend services.
        - Concurrency: A threading.Lock is used to ensure thread-safe access to the cache.
        - Retry Mechanism: call_with_retry is implemented to handle transient failures,
          particularly for the PricingService.getPrice operation.
        - Circuit Breaker: Each service is wrapped using a simple circuit breaker pattern to
          prevent cascading failures.
        - Failure Handling: If InventoryService reports the product is not available, or if PricingService
          fails after retries, the product is treated as not available.
    """
    # Check cache first.
    with cache_lock:
        if product_id in cache:
            result, expiry = cache[product_id]
            if time.time() < expiry:
                return result
            else:
                del cache[product_id]

    # Query InventoryService.
    try:
        available = InventoryService.checkAvailability(product_id)
    except Exception:
        # If the circuit is open or service call fails, treat as unavailable.
        available = False

    # If product is not available, cache and return.
    if not available:
        result = (False, 0.0, [])
        with cache_lock:
            cache[product_id] = (result, time.time() + CACHE_TTL)
        return result

    # Product is available, fetch price with retry.
    try:
        price = call_with_retry(PricingService.getPrice, 3, 0.05, 2, product_id)
    except Exception:
        # On persistent pricing failures, treat the product as unavailable.
        result = (False, 0.0, [])
        with cache_lock:
            cache[product_id] = (result, time.time() + CACHE_TTL)
        return result

    # Fetch promotions (no retry mechanism here; on failure assume no promotions).
    try:
        promotions = PromotionService.getPromotions(product_id)
    except Exception:
        promotions = []

    final_price = price - DISCOUNT_PER_PROMO * len(promotions)
    result = (True, final_price, promotions)

    # Cache the resulting availability data.
    with cache_lock:
        cache[product_id] = (result, time.time() + CACHE_TTL)
    return result