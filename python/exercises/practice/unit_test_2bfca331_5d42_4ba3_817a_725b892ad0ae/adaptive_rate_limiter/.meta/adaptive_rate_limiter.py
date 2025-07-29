import threading

class RateLimiter:
    HIGH_THRESHOLD = 500  # in milliseconds
    LOW_THRESHOLD = 200   # in milliseconds

    def __init__(self):
        self._client_configs = {}
        self._client_usage = {}
        self.backend_response_time = None  # in milliseconds
        self.lock = threading.Lock()

    def update_client_config(self, client_id, rate_limit, time_window):
        with self.lock:
            self._client_configs[client_id] = {
                'rate_limit': rate_limit,
                'time_window': time_window
            }
            if client_id not in self._client_usage:
                self._client_usage[client_id] = []

    def update_backend_response_time(self, response_time):
        with self.lock:
            self.backend_response_time = response_time

    def _get_effective_limit(self, client_id):
        config = self._client_configs.get(client_id)
        if not config:
            return 0
        configured_limit = config['rate_limit']
        if self.backend_response_time is None:
            return configured_limit
        if self.backend_response_time > self.HIGH_THRESHOLD:
            effective = max(1, configured_limit // 2)
        elif self.backend_response_time < self.LOW_THRESHOLD:
            effective = configured_limit
        else:
            factor = (self.backend_response_time - self.LOW_THRESHOLD) / (self.HIGH_THRESHOLD - self.LOW_THRESHOLD)
            # Linear interpolation between half the rate and full rate.
            half_limit = configured_limit // 2
            effective = int(half_limit + (configured_limit - half_limit) * (1 - factor))
            if effective < 1:
                effective = 1
        return effective

    def process_request(self, client_id, request_timestamp):
        with self.lock:
            config = self._client_configs.get(client_id)
            if not config:
                return {'allowed': False, 'retry_after': 0}

            time_window = config['time_window']
            effective_limit = self._get_effective_limit(client_id)
            usage = self._client_usage.get(client_id, [])

            # Remove entries that fall outside the current time window.
            valid_usage = [ts for ts in usage if ts > request_timestamp - time_window]
            self._client_usage[client_id] = valid_usage

            if len(valid_usage) < effective_limit:
                self._client_usage[client_id].append(request_timestamp)
                return {'allowed': True, 'retry_after': 0}
            else:
                earliest = min(valid_usage)
                retry_after = time_window - (request_timestamp - earliest)
                retry_after = int(retry_after) if retry_after > 0 else 0
                return {'allowed': False, 'retry_after': retry_after}