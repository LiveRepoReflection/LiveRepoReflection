import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional
from threading import Lock, Event

@dataclass
class LockInfo:
    client_id: str
    expiry_time: float
    lock: Lock
    event: Event

class DistributedLockService:
    def __init__(self, lease_duration: int = 5):
        # Main lock to protect the locks dictionary
        self._global_lock = Lock()
        # Dictionary to store lock information for each resource
        self._locks: Dict[str, LockInfo] = {}
        # Default lease duration in seconds
        self._lease_duration = lease_duration
        # Start the cleanup thread
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Starts a background thread to clean up expired locks."""
        def cleanup():
            while True:
                current_time = time.time()
                with self._global_lock:
                    expired_resources = [
                        resource
                        for resource, lock_info in self._locks.items()
                        if current_time > lock_info.expiry_time
                    ]
                    for resource in expired_resources:
                        self._remove_lock(resource)
                time.sleep(1)  # Check every second

        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()

    def acquire_lock(self, resource_id: str, client_id: str, timeout: int) -> bool:
        """
        Attempts to acquire a lock on the specified resource.
        
        Args:
            resource_id: Unique identifier for the resource
            client_id: Unique identifier for the client
            timeout: Maximum time to wait for lock acquisition
        
        Returns:
            bool: True if lock was acquired, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self._global_lock:
                # Check if the resource is already locked
                if resource_id in self._locks:
                    lock_info = self._locks[resource_id]
                    
                    # If the lock has expired, remove it
                    if time.time() > lock_info.expiry_time:
                        self._remove_lock(resource_id)
                    # If the same client is trying to acquire the lock again
                    elif lock_info.client_id == client_id:
                        self._extend_lease(resource_id)
                        return True
                    else:
                        # Resource is locked by another client
                        event = lock_info.event
                else:
                    # Create new lock for the resource
                    self._locks[resource_id] = LockInfo(
                        client_id=client_id,
                        expiry_time=time.time() + self._lease_duration,
                        lock=Lock(),
                        event=Event()
                    )
                    return True

            # Wait for the lock to be released
            remaining_timeout = timeout - (time.time() - start_time)
            if remaining_timeout > 0:
                event.wait(timeout=remaining_timeout)
            
        return False

    def release_lock(self, resource_id: str, client_id: str) -> bool:
        """
        Releases the lock on the specified resource.
        
        Args:
            resource_id: Unique identifier for the resource
            client_id: Unique identifier for the client
        
        Returns:
            bool: True if lock was released, False if the lock didn't exist or wasn't owned by the client
        """
        with self._global_lock:
            if resource_id not in self._locks:
                return False
            
            lock_info = self._locks[resource_id]
            if lock_info.client_id != client_id:
                return False
                
            self._remove_lock(resource_id)
            return True

    def heartbeat(self, resource_id: str, client_id: str) -> bool:
        """
        Extends the lease on a lock if the client still owns it.
        
        Args:
            resource_id: Unique identifier for the resource
            client_id: Unique identifier for the client
        
        Returns:
            bool: True if lease was extended, False otherwise
        """
        with self._global_lock:
            if resource_id not in self._locks:
                return False
                
            lock_info = self._locks[resource_id]
            if lock_info.client_id != client_id:
                return False
                
            self._extend_lease(resource_id)
            return True

    def _extend_lease(self, resource_id: str):
        """Extends the lease duration for a lock."""
        if resource_id in self._locks:
            self._locks[resource_id].expiry_time = time.time() + self._lease_duration

    def _remove_lock(self, resource_id: str):
        """Removes a lock and notifies waiting clients."""
        if resource_id in self._locks:
            self._locks[resource_id].event.set()  # Notify waiting clients
            del self._locks[resource_id]