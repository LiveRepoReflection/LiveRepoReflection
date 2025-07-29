import time
import threading

class Node:
    def __init__(self, address):
        self.address = address
        self.data_store = {}
        self.lock = threading.Lock()
        self.healthy = True

    def put(self, key, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        with self.lock:
            if key not in self.data_store or self.data_store[key][1] <= timestamp:
                self.data_store[key] = (value, timestamp)

    def get(self, key):
        with self.lock:
            item = self.data_store.get(key, (None, None))
            return item[0]

    def delete(self, key):
        with self.lock:
            if key in self.data_store:
                del self.data_store[key]

    def health_check(self):
        return self.healthy

class Client:
    def __init__(self, nodes, replication_factor=2):
        self.nodes = nodes
        self.replication_factor = replication_factor

    def _hash(self, key):
        return sum(ord(c) for c in key)

    def _get_nodes_for_key(self, key):
        index = self._hash(key) % len(self.nodes)
        selected = []
        for i in range(self.replication_factor):
            selected.append(self.nodes[(index + i) % len(self.nodes)])
        return selected

    def put(self, key, value):
        timestamp = time.time()
        nodes = self._get_nodes_for_key(key)
        for node in nodes:
            node.put(key, value, timestamp)

    def get(self, key):
        nodes = self._get_nodes_for_key(key)
        result = None
        latest_ts = -1
        for node in nodes:
            if node.health_check():
                with node.lock:
                    if key in node.data_store:
                        val, ts = node.data_store[key]
                        if ts > latest_ts:
                            latest_ts = ts
                            result = val
        return result

    def delete(self, key):
        nodes = self._get_nodes_for_key(key)
        for node in nodes:
            node.delete(key)

    def health_check(self):
        return all(node.health_check() for node in self.nodes)