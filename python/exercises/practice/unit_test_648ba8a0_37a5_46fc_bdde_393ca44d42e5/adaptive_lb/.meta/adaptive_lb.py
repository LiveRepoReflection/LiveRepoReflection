import time

class BackendServer:
    def __init__(self, id, capacity, latency):
        self.id = id
        self.capacity = capacity
        self.latency = latency
        self.current_load = 0
        self.last_heartbeat = time.time()
        self.available = True

    def report_heartbeat(self, load, latency):
        self.current_load = load
        self.latency = latency
        self.last_heartbeat = time.time()
        self.available = True

class LoadBalancer:
    def __init__(self, heartbeat_timeout):
        self.heartbeat_timeout = heartbeat_timeout
        self.servers = []

    def add_server(self, server):
        self.servers.append(server)

    def update_server_statuses(self):
        current_time = time.time()
        for server in self.servers:
            if current_time - server.last_heartbeat > self.heartbeat_timeout:
                server.available = False
            else:
                server.available = True

    def select_server(self):
        self.update_server_statuses()
        candidates = [s for s in self.servers if s.available and s.current_load < s.capacity]
        if not candidates:
            raise Exception("No available backend servers")
        selected = min(candidates, key=lambda s: s.latency)
        return selected