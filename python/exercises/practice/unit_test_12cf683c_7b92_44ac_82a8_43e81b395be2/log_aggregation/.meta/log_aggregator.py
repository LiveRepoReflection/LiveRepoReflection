import threading
import heapq
import time
from collections import defaultdict
from bisect import bisect_left, bisect_right

class LogEntry:
    """Represents a single log entry with timestamp, server ID, and message."""
    def __init__(self, timestamp, server_id, message):
        self.timestamp = timestamp
        self.server_id = server_id
        self.message = message
    
    def __lt__(self, other):
        return self.timestamp < other.timestamp


class ServerLogger:
    """Manages logs for a single server."""
    def __init__(self, server_id, region_id):
        self.server_id = server_id
        self.region_id = region_id
        self.logs = []  # Sorted list of LogEntry objects
        self.lock = threading.RLock()
        self.failed = False
        self.backup_logs = []  # For fault tolerance
    
    def add_log(self, log_entry):
        with self.lock:
            # Binary search to find insertion point to maintain sorted order
            index = bisect_right([log.timestamp for log in self.logs], log_entry.timestamp)
            self.logs.insert(index, log_entry)
            
            # If server is marked as failed, also store in backup
            if self.failed:
                self.backup_logs.append(log_entry)
    
    def get_logs_in_range(self, start_time, end_time):
        with self.lock:
            # Binary search to find start and end indices
            timestamps = [log.timestamp for log in self.logs]
            start_idx = bisect_left(timestamps, start_time)
            end_idx = bisect_right(timestamps, end_time)
            
            return [log.message for log in self.logs[start_idx:end_idx]]
    
    def mark_failed(self):
        with self.lock:
            self.failed = True
    
    def recover(self):
        with self.lock:
            # Merge backup logs with main logs
            if self.failed and self.backup_logs:
                for log in self.backup_logs:
                    # Re-add using binary search to maintain order
                    index = bisect_right([log.timestamp for log in self.logs], log.timestamp)
                    # Check if this log is already in the main logs
                    if (index == 0 or self.logs[index-1].timestamp != log.timestamp or 
                        self.logs[index-1].message != log.message):
                        self.logs.insert(index, log)
                self.backup_logs = []
            self.failed = False


class RegionLogger:
    """Manages logs for servers within a region."""
    def __init__(self, region_id):
        self.region_id = region_id
        self.servers = {}  # Maps server_id to ServerLogger
        self.lock = threading.RLock()
    
    def add_server(self, server_id):
        with self.lock:
            if server_id not in self.servers:
                self.servers[server_id] = ServerLogger(server_id, self.region_id)
    
    def get_server(self, server_id):
        with self.lock:
            return self.servers.get(server_id)
    
    def get_logs_in_range(self, start_time, end_time):
        with self.lock:
            # Collect logs from all servers in this region
            all_logs = []
            for server in self.servers.values():
                server_logs = server.get_logs_in_range(start_time, end_time)
                all_logs.extend(server_logs)
            
            # Since logs from each server are already sorted, we just need to merge them
            return all_logs


class LogAggregator:
    """Main class for aggregating and querying logs from distributed servers."""
    def __init__(self):
        self.regions = {}  # Maps region_id to RegionLogger
        self.server_to_region = {}  # Maps server_id to region_id
        self.global_lock = threading.RLock()
        
        # For caching query results
        self.query_cache = {}
        self.cache_expiry = {}  # Maps cache_key to expiry timestamp
        self.cache_lock = threading.RLock()
        self.cache_ttl = 5000  # Cache TTL in milliseconds
        
        # For real-time aggregation
        self.recent_logs = []  # For quick access to most recent logs
        self.recent_logs_limit = 10000  # Limit size of recent logs buffer
        self.recent_logs_lock = threading.RLock()
    
    def register_server(self, server_id, region_id):
        with self.global_lock:
            if region_id not in self.regions:
                self.regions[region_id] = RegionLogger(region_id)
            
            self.regions[region_id].add_server(server_id)
            self.server_to_region[server_id] = region_id
    
    def ingest_log(self, timestamp, server_id, message):
        # Check if server is registered
        if server_id not in self.server_to_region:
            # Auto-register server to a default region if not registered
            self.register_server(server_id, "default")
        
        region_id = self.server_to_region[server_id]
        log_entry = LogEntry(timestamp, server_id, message)
        
        # Add to server's logs
        region = self.regions[region_id]
        server = region.get_server(server_id)
        if server:
            server.add_log(log_entry)
        
        # Add to recent logs buffer for quick access
        with self.recent_logs_lock:
            # Binary insert into recent_logs to maintain timestamp order
            index = bisect_right([log.timestamp for log in self.recent_logs], timestamp)
            self.recent_logs.insert(index, log_entry)
            
            # Trim if exceeding limit
            if len(self.recent_logs) > self.recent_logs_limit:
                self.recent_logs = self.recent_logs[-self.recent_logs_limit:]
        
        # Invalidate relevant cache entries
        self._invalidate_cache(server_id, region_id)
    
    def query(self, query_type, identifier, start_time, end_time):
        # Validate parameters
        if query_type not in ["server", "region", "global"]:
            raise ValueError(f"Invalid query type: {query_type}")
        
        if start_time > end_time:
            raise ValueError(f"Start time ({start_time}) must be less than or equal to end time ({end_time})")
        
        # Check cache first
        cache_key = (query_type, identifier, start_time, end_time)
        cached_result = self._check_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        results = []
        
        # Handle different query types
        if query_type == "server":
            if identifier in self.server_to_region:
                region_id = self.server_to_region[identifier]
                region = self.regions.get(region_id)
                if region:
                    server = region.get_server(identifier)
                    if server:
                        results = server.get_logs_in_range(start_time, end_time)
        
        elif query_type == "region":
            region = self.regions.get(identifier)
            if region:
                results = region.get_logs_in_range(start_time, end_time)
                # Sort results by timestamp since they come from multiple servers
                results.sort()
        
        elif query_type == "global":
            # Check if query can be satisfied from recent_logs buffer
            current_time = int(time.time() * 1000)
            if current_time - start_time < self.cache_ttl:
                # For very recent queries, use the recent_logs buffer
                with self.recent_logs_lock:
                    # Binary search to find start and end indices
                    timestamps = [log.timestamp for log in self.recent_logs]
                    start_idx = bisect_left(timestamps, start_time)
                    end_idx = bisect_right(timestamps, end_time)
                    
                    results = [log.message for log in self.recent_logs[start_idx:end_idx]]
            else:
                # Otherwise, query all regions
                all_logs = []
                for region in self.regions.values():
                    region_logs = region.get_logs_in_range(start_time, end_time)
                    all_logs.extend(region_logs)
                
                # For global queries, we need to sort the results
                results = sorted(all_logs)
        
        # Cache the result
        self._cache_result(cache_key, results)
        
        return results
    
    def mark_server_failed(self, server_id):
        if server_id in self.server_to_region:
            region_id = self.server_to_region[server_id]
            region = self.regions.get(region_id)
            if region:
                server = region.get_server(server_id)
                if server:
                    server.mark_failed()
                    return True
        return False
    
    def recover_server(self, server_id):
        if server_id in self.server_to_region:
            region_id = self.server_to_region[server_id]
            region = self.regions.get(region_id)
            if region:
                server = region.get_server(server_id)
                if server:
                    server.recover()
                    return True
        return False
    
    def _check_cache(self, cache_key):
        with self.cache_lock:
            if cache_key in self.query_cache:
                # Check if cache entry has expired
                if self.cache_expiry.get(cache_key, 0) > time.time():
                    return self.query_cache[cache_key]
                else:
                    # Remove expired entry
                    del self.query_cache[cache_key]
                    del self.cache_expiry[cache_key]
        return None
    
    def _cache_result(self, cache_key, result):
        with self.cache_lock:
            self.query_cache[cache_key] = result
            self.cache_expiry[cache_key] = time.time() + (self.cache_ttl / 1000)  # Convert ms to seconds
            
            # Clean up expired cache entries occasionally
            if len(self.query_cache) > 1000:  # Arbitrary threshold
                self._clean_cache()
    
    def _clean_cache(self):
        with self.cache_lock:
            current_time = time.time()
            expired_keys = [k for k, v in self.cache_expiry.items() if v <= current_time]
            for key in expired_keys:
                del self.query_cache[key]
                del self.cache_expiry[key]
    
    def _invalidate_cache(self, server_id, region_id):
        with self.cache_lock:
            # Invalidate server-specific cache entries
            keys_to_remove = []
            for key in self.query_cache:
                query_type, identifier, _, _ = key
                if (query_type == "server" and identifier == server_id) or \
                   (query_type == "region" and identifier == region_id) or \
                   (query_type == "global"):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                if key in self.query_cache:
                    del self.query_cache[key]
                if key in self.cache_expiry:
                    del self.cache_expiry[key]