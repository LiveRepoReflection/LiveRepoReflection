import threading
import time
import random
import hashlib

# Global variables for metrics
_metrics_lock = threading.Lock()
_processed_latencies = []
_rejected_requests = 0

# For utilization sampling
_utilization_records = []
_utilization_lock = threading.Lock()

# Global request counter
_request_counter = 0
_request_counter_lock = threading.Lock()

# Event to signal simulation end
_stop_event = threading.Event()

class Request:
    def __init__(self, req_id, arrival_time, duration):
        self.req_id = req_id
        self.arrival_time = arrival_time
        self.duration = duration

class Server:
    def __init__(self, server_id, capacity, queue_size):
        self.server_id = server_id
        self.capacity = capacity
        self.queue_size = queue_size
        self.active_count = 0
        self.processed_count = 0
        self.queue = []
        self.health_lock = threading.Lock()
        self.status = True  # True means healthy/up, False means down
        self.server_lock = threading.Lock()
        self.processing_threads = []

    def can_accept(self):
        with self.server_lock:
            if not self.status:
                return False
            if self.active_count < self.capacity:
                return True
            if self.queue_size > len(self.queue):
                return True
            return False

    def add_request(self, req):
        with self.server_lock:
            if not self.status:
                return False
            if self.active_count < self.capacity:
                self._start_processing(req)
                return True
            elif self.queue_size > len(self.queue):
                self.queue.append(req)
                return True
            else:
                return False

    def _start_processing(self, req):
        self.active_count += 1
        thread = threading.Thread(target=self.process_request, args=(req,))
        thread.start()
        self.processing_threads.append(thread)

    def process_request(self, req):
        start_processing = time.time()
        # Simulate processing time
        time.sleep(req.duration)
        end_processing = time.time()

        # Record latency
        latency = end_processing - req.arrival_time
        with _metrics_lock:
            _processed_latencies.append(latency)
        with self.server_lock:
            self.processed_count += 1
            self.active_count -= 1
            # If queue has waiting requests, process next
            if self.queue and self.status:
                next_req = self.queue.pop(0)
                self._start_processing(next_req)

def health_check_thread(servers, health_check_interval, health_timeline):
    while not _stop_event.is_set():
        current_time = time.time()
        for server in servers:
            with server.server_lock:
                # For simulation, if active_count exceeds 80% of capacity, mark down, else up.
                threshold = 0.8 * server.capacity
                new_status = True
                if server.capacity > 0 and server.active_count > threshold:
                    new_status = False
                if new_status != server.status:
                    server.status = new_status
                    event = {
                        "time": current_time,
                        "server_id": server.server_id,
                        "status": "up" if new_status else "down"
                    }
                    health_timeline.append(event)
        time.sleep(health_check_interval)

def utilization_sampler_thread(servers, sample_interval):
    while not _stop_event.is_set():
        sample = []
        for server in servers:
            with server.server_lock:
                utilization = (server.active_count / server.capacity * 100) if server.capacity > 0 else 0
                sample.append(utilization)
        with _utilization_lock:
            _utilization_records.append(sum(sample)/len(sample) if sample else 0)
        time.sleep(sample_interval)

def request_arrival_thread(servers, config, lb_state):
    global _request_counter, _rejected_requests
    request_durations = config["request_durations"]
    arrival_rate = config["request_arrival_rate"]
    simulation_end = time.time() + config["simulation_time"]
    # For weighted algorithms pre-calc weighted sequence if necessary
    weighted_sequence = []
    if config["load_balancing_algorithm"] == "weighted_round_robin":
        for idx, weight in enumerate(config["server_weights"]):
            weighted_sequence.extend([idx] * weight)
    round_robin_index = 0

    while time.time() < simulation_end and not _stop_event.is_set():
        # Calculate sleep time between arrivals
        sleep_time = 1.0 / arrival_rate
        time.sleep(sleep_time)
        with _request_counter_lock:
            req_id = _request_counter
            _request_counter += 1
        arrival_time = time.time()
        duration = random.choice(request_durations)
        req = Request(req_id, arrival_time, duration)

        selected_server = None
        algorithm = config["load_balancing_algorithm"]
        healthy_servers = [s for s in servers if s.status]
        if not healthy_servers:
            with _metrics_lock:
                _rejected_requests += 1
            continue

        if algorithm == "round_robin":
            # Cycle through servers in order
            selected_server = servers[lb_state["round_robin_index"] % len(servers)]
            lb_state["round_robin_index"] = (lb_state["round_robin_index"] + 1) % len(servers)
            if not selected_server.status:
                # Find next healthy
                for s in servers:
                    if s.status:
                        selected_server = s
                        break
        elif algorithm == "least_connections":
            selected_server = min(healthy_servers, key=lambda s: s.active_count)
        elif algorithm == "weighted_round_robin":
            # Cycle through weighted sequence
            index = weighted_sequence[lb_state["weighted_rr_index"] % len(weighted_sequence)]
            lb_state["weighted_rr_index"] = (lb_state["weighted_rr_index"] + 1) % len(weighted_sequence)
            selected_server = servers[index]
            if not selected_server.status:
                # fallback to least connections if selected server down
                selected_server = min(healthy_servers, key=lambda s: s.active_count)
        elif algorithm == "consistent_hashing":
            # Use hash of request id to pick a server among healthy ones.
            hash_val = int(hashlib.sha256(str(req_id).encode()).hexdigest(), 16)
            idx = hash_val % len(healthy_servers)
            selected_server = healthy_servers[idx]
        else:
            # Default fallback: round robin.
            selected_server = servers[lb_state["round_robin_index"] % len(servers)]
            lb_state["round_robin_index"] = (lb_state["round_robin_index"] + 1) % len(servers)

        # Try to add request to selected server
        accepted = selected_server.add_request(req)
        if not accepted:
            with _metrics_lock:
                _rejected_requests += 1

def simulate_load_balancer(config):
    global _processed_latencies, _rejected_requests, _utilization_records, _request_counter, _stop_event
    # Validate configuration
    if config["N"] <= 0:
        raise ValueError("Number of servers must be positive")
    if config["server_capacity"] < 0:
        raise ValueError("Server capacity must be non-negative")
    if config["request_arrival_rate"] < 0:
        raise ValueError("Request arrival rate must be non-negative")
    if config["simulation_time"] <= 0:
        raise ValueError("Simulation time must be positive")

    # Reset global metrics
    _processed_latencies = []
    _rejected_requests = 0
    _utilization_records = []
    _request_counter = 0
    _stop_event.clear()

    # Create servers
    servers = []
    for i in range(1, config["N"] + 1):
        servers.append(Server(i, config["server_capacity"], config.get("queue_size", 0)))

    # Health timeline for recording health check events
    health_timeline = []

    # Load balancer state for round robin counters
    lb_state = {"round_robin_index": 0, "weighted_rr_index": 0}

    # Start health check thread
    health_thread = threading.Thread(target=health_check_thread, args=(servers, config["health_check_interval"], health_timeline))
    health_thread.start()

    # Start utilization sampler thread
    sampler_thread = threading.Thread(target=utilization_sampler_thread, args=(servers, 0.1))
    sampler_thread.start()

    # Start request arrival thread
    arrival_thread = threading.Thread(target=request_arrival_thread, args=(servers, config, lb_state))
    arrival_thread.start()

    # Wait for simulation time to expire
    time.sleep(config["simulation_time"])
    _stop_event.set()

    # Wait for arrival thread to finish
    arrival_thread.join()
    # Wait for health and sampler threads to finish
    health_thread.join()
    sampler_thread.join()

    # Wait for all processing threads on servers to complete
    for server in servers:
        for thread in server.processing_threads:
            thread.join()

    # Calculate average latency
    with _metrics_lock:
        total_processed = len(_processed_latencies)
        avg_latency = sum(_processed_latencies) / total_processed if total_processed > 0 else 0
        total_rejections = _rejected_requests

    # Calculate average utilization
    with _utilization_lock:
        avg_utilization = sum(_utilization_records) / len(_utilization_records) if _utilization_records else 0

    # Build server processed count dictionary
    server_processed = {}
    for server in servers:
        server_processed[server.server_id] = server.processed_count

    # Calculate rejection rate
    total_requests = _request_counter
    rejection_rate = (total_rejections / total_requests * 100) if total_requests > 0 else 0

    metrics = {
        "avg_utilization": avg_utilization,
        "avg_latency": avg_latency,
        "rejection_rate": rejection_rate,
        "server_processed": server_processed,
        "health_timeline": health_timeline
    }
    return metrics

# If run as main, perform a simple simulation.
if __name__ == "__main__":
    config = {
        "N": 5,
        "server_capacity": 10,
        "load_balancing_algorithm": "round_robin",  # Options: round_robin, least_connections, weighted_round_robin, consistent_hashing
        "server_weights": [1, 1, 1, 1, 1],
        "queue_size": 5,
        "health_check_interval": 1,
        "request_arrival_rate": 10,
        "request_durations": [0.1, 0.2, 0.15],
        "simulation_time": 5
    }
    metrics = simulate_load_balancer(config)
    print("Metrics:")
    print(metrics)