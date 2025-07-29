class RateLimiter:
    def __init__(self, config):
        # config: dict mapping client_id to a dict {"limit": int, "window": int}
        self.config = config
        # State stores the client_id with its current window start time and count of requests
        self.state = {}

    def process(self, request):
        client_id = request.get("client_id")
        timestamp = request.get("request_timestamp")
        if client_id is None or timestamp is None:
            raise ValueError("Invalid request: missing client_id or request_timestamp")

        # For unknown clients, there is no rate limit
        if client_id not in self.config:
            return {"allowed": True, "remaining_requests": float("inf")}

        client_config = self.config[client_id]
        limit = client_config.get("limit")
        window = client_config.get("window")
        if limit is None or window is None:
            raise ValueError("Invalid configuration for client: missing limit or window")

        # Initialize client state if not present.
        if client_id not in self.state:
            self.state[client_id] = {"window_start": timestamp, "count": 1}
            remaining = limit - 1
            return {"allowed": True, "remaining_requests": remaining}

        client_state = self.state[client_id]
        window_start = client_state["window_start"]
        count = client_state["count"]

        if timestamp - window_start < window:
            if count < limit:
                client_state["count"] += 1
                remaining = limit - client_state["count"]
                return {"allowed": True, "remaining_requests": remaining}
            else:
                # Rate limit exceeded; calculate time until window resets.
                retry_after = window - (timestamp - window_start)
                if retry_after < 0:
                    retry_after = 0
                return {"allowed": False, "remaining_requests": 0, "retry_after": retry_after}
        else:
            # New window started; reset the state.
            self.state[client_id] = {"window_start": timestamp, "count": 1}
            remaining = limit - 1
            return {"allowed": True, "remaining_requests": remaining}