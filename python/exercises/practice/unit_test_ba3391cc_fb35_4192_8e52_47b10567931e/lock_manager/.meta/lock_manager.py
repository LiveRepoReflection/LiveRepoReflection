import threading
import time
import heapq
from collections import defaultdict, namedtuple

class LockManager:
    """
    A distributed lock manager that provides mechanisms for multiple clients
    to safely coordinate access to shared resources.
    """
    
    # Named tuple to store lock information
    Lock = namedtuple('Lock', ['expiry_time', 'client_id', 'resource_id', 'reentry_count'])
    
    def __init__(self, default_expiry_time=30000):
        """
        Initialize the lock manager.
        
        Args:
            default_expiry_time (int): Default lock expiry time in milliseconds.
        """
        self.default_expiry_time = default_expiry_time
        
        # Main data structure to store active locks
        # Key: resource_id, Value: (client_id, expiry_time, reentry_count)
        self.locks = {}
        
        # Priority queue for efficient lock expiry checks
        # Each item is a tuple: (expiry_time, resource_id)
        self.expiry_heap = []
        
        # Client lock tracking for quick lookups
        # Key: client_id, Value: set of resource_ids locked by this client
        self.client_locks = defaultdict(set)
        
        # Thread lock for synchronization
        self.thread_lock = threading.Lock()
        
        # Start the lock expiry background thread
        self.running = True
        self.expiry_thread = threading.Thread(target=self._expiry_checker)
        self.expiry_thread.daemon = True
        self.expiry_thread.start()
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        self.running = False
        if hasattr(self, 'expiry_thread') and self.expiry_thread.is_alive():
            self.expiry_thread.join(timeout=1.0)
    
    def acquire_lock(self, resource_id, client_id, timeout):
        """
        Attempt to acquire a lock on the specified resource.
        
        Args:
            resource_id (str): The resource to lock.
            client_id (str): The client requesting the lock.
            timeout (int): Maximum time in milliseconds to wait for the lock.
            
        Returns:
            bool: True if the lock was acquired, False otherwise.
        """
        if not isinstance(resource_id, str) or not isinstance(client_id, str) or not isinstance(timeout, int):
            return False
        
        if timeout < 0:
            return False
        
        # Convert timeout to seconds for time.time() compatibility
        timeout_seconds = timeout / 1000.0
        end_time = time.time() + timeout_seconds
        
        # First quick check without acquiring the thread lock
        if resource_id in self.locks and self.locks[resource_id][0] == client_id:
            return True
        
        while time.time() < end_time:
            with self.thread_lock:
                # Check if the resource is already locked
                if resource_id in self.locks:
                    current_client, expiry_time, reentry_count = self.locks[resource_id]
                    
                    # If the lock has expired, remove it
                    if time.time() * 1000 > expiry_time:
                        self._remove_lock(resource_id)
                    # If the same client is trying to reacquire, increment reentry count
                    elif current_client == client_id:
                        # Update with incremented reentry count
                        self.locks[resource_id] = (client_id, expiry_time, reentry_count + 1)
                        return True
                    # Otherwise, the resource is locked by another client
                    else:
                        pass  # Will retry after sleep
                else:
                    # Resource is not locked, acquire it
                    expiry_time = int(time.time() * 1000) + self.default_expiry_time
                    self.locks[resource_id] = (client_id, expiry_time, 1)  # Initial reentry count is 1
                    self.client_locks[client_id].add(resource_id)
                    
                    # Add to expiry heap
                    heapq.heappush(self.expiry_heap, (expiry_time, resource_id))
                    return True
            
            # Sleep a small amount before retrying
            # Use a short sleep to be responsive but not consume too much CPU
            time.sleep(0.01)
        
        # Timeout reached without acquiring the lock
        return False
    
    def release_lock(self, resource_id, client_id):
        """
        Release a lock on the specified resource.
        
        Args:
            resource_id (str): The resource to unlock.
            client_id (str): The client releasing the lock.
            
        Returns:
            bool: True if the lock was released, False otherwise.
        """
        if not isinstance(resource_id, str) or not isinstance(client_id, str):
            return False
        
        with self.thread_lock:
            # Check if the resource is locked and by the correct client
            if resource_id in self.locks:
                current_client, expiry_time, reentry_count = self.locks[resource_id]
                
                if current_client == client_id:
                    # Decrement reentry count
                    if reentry_count > 1:
                        self.locks[resource_id] = (client_id, expiry_time, reentry_count - 1)
                    else:
                        # Remove the lock completely
                        self._remove_lock(resource_id)
                    return True
            
            # Lock doesn't exist or is owned by a different client
            return False
    
    def extend_lock(self, resource_id, client_id, extension_time):
        """
        Extend the duration of a lock.
        
        Args:
            resource_id (str): The resource with the lock to extend.
            client_id (str): The client requesting the extension.
            extension_time (int): Time in milliseconds to extend the lock by.
            
        Returns:
            bool: True if the lock was extended, False otherwise.
        """
        if not isinstance(resource_id, str) or not isinstance(client_id, str) or not isinstance(extension_time, int):
            return False
        
        if extension_time <= 0:
            return False
        
        with self.thread_lock:
            # Check if the resource is locked and by the correct client
            if resource_id in self.locks:
                current_client, expiry_time, reentry_count = self.locks[resource_id]
                
                if current_client == client_id:
                    # Extend the lock
                    new_expiry_time = expiry_time + extension_time
                    self.locks[resource_id] = (client_id, new_expiry_time, reentry_count)
                    
                    # Update the expiry heap
                    # (Note: We're adding a new entry rather than removing the old one,
                    # which is simpler but less efficient. The old entry will be skipped 
                    # during expiry checking.)
                    heapq.heappush(self.expiry_heap, (new_expiry_time, resource_id))
                    return True
            
            # Lock doesn't exist or is owned by a different client
            return False
    
    def _remove_lock(self, resource_id):
        """
        Remove a lock from the internal data structures.
        
        Args:
            resource_id (str): The resource to remove the lock for.
        """
        if resource_id in self.locks:
            client_id = self.locks[resource_id][0]
            del self.locks[resource_id]
            
            # Remove from client_locks
            if client_id in self.client_locks:
                self.client_locks[client_id].discard(resource_id)
                if not self.client_locks[client_id]:
                    del self.client_locks[client_id]
            
            # Note: We don't remove from the expiry heap here for efficiency,
            # instead we skip expired/invalid entries during the expiry check.
    
    def _expiry_checker(self):
        """
        Background thread that periodically checks for and removes expired locks.
        """
        while self.running:
            expired_resources = []
            
            # Check for expired locks
            current_time_ms = int(time.time() * 1000)
            
            with self.thread_lock:
                # Process the heap until we find a non-expired lock
                while self.expiry_heap and self.expiry_heap[0][0] <= current_time_ms:
                    expiry_time, resource_id = heapq.heappop(self.expiry_heap)
                    
                    # Skip if the resource is no longer locked or has a different expiry time
                    if (resource_id not in self.locks or 
                        self.locks[resource_id][1] != expiry_time):
                        continue
                    
                    # This lock has expired
                    expired_resources.append(resource_id)
                
                # Remove all expired locks
                for resource_id in expired_resources:
                    self._remove_lock(resource_id)
            
            # Sleep before the next check
            # The sleep duration can be tuned based on requirements
            time.sleep(0.1)  # 100ms