import threading
import logging
import time
from typing import List, Dict, Tuple, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Exception raised when a service operation fails."""
    pass

class TransactionManager:
    """Manages a distributed transaction across multiple services."""
    
    def __init__(self, operations: List[Tuple[str, str, Dict[str, Any]]], services: Dict[str, Any]):
        """
        Initialize the transaction manager.
        
        Args:
            operations: List of operations to perform. Each operation is a tuple of
                        (service_name, action, data).
            services: Dictionary mapping service names to service objects.
        """
        self.operations = operations
        self.services = services
        self.transaction_log = []
        self.lock = threading.RLock()
        self.max_retries = 3
        self.retry_backoff_base = 0.5  # seconds
    
    def execute(self) -> bool:
        """
        Execute the transaction.
        
        Returns:
            bool: True if the transaction was successful, False otherwise.
        """
        if not self.operations:
            logger.info("Empty operations list. Transaction completed successfully.")
            return True
        
        try:
            # Execute each operation in sequence
            for service_name, action, data in self.operations:
                if service_name not in self.services:
                    raise ServiceError(f"Service {service_name} not found")
                
                service = self.services[service_name]
                transaction_id = self._perform_with_retry(service, service_name, action, data)
                
                with self.lock:
                    self.transaction_log.append((service, action, transaction_id))
                
            logger.info("Transaction completed successfully")
            return True
            
        except ServiceError as e:
            logger.error(f"Transaction failed: {e}")
            # Rollback in reverse order
            self._rollback()
            return False
    
    def _perform_with_retry(self, service: Any, service_name: str, action: str, data: Dict[str, Any]) -> str:
        """
        Perform a service action with retry logic.
        
        Args:
            service: The service object
            service_name: Name of the service
            action: The action to perform
            data: The data for the action
            
        Returns:
            str: Transaction ID if successful
            
        Raises:
            ServiceError: If the action fails after all retries
        """
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                logger.info(f"Performing {action} on {service_name} (attempt {retries + 1})")
                transaction_id = service.perform(action, data)
                logger.info(f"Successfully performed {action} on {service_name}")
                return transaction_id
                
            except ServiceError as e:
                last_error = e
                retries += 1
                
                if retries < self.max_retries:
                    # Exponential backoff
                    wait_time = self.retry_backoff_base * (2 ** (retries - 1))
                    logger.warning(f"Attempt {retries} failed for {service_name}.{action}: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed for {service_name}.{action}")
        
        # If we get here, all retries failed
        raise ServiceError(f"Failed to perform {action} on {service_name} after {self.max_retries} attempts: {last_error}")
    
    def _rollback(self) -> None:
        """
        Roll back all completed operations in reverse order.
        """
        logger.info("Starting transaction rollback")
        
        # Make a copy to avoid race conditions
        with self.lock:
            operations_to_rollback = list(reversed(self.transaction_log))
            self.transaction_log = []
        
        rollback_errors = []
        
        for service, action, transaction_id in operations_to_rollback:
            try:
                logger.info(f"Rolling back {action} with transaction_id {transaction_id}")
                service.rollback(action, transaction_id)
                logger.info(f"Successfully rolled back {action}")
            except ServiceError as e:
                error_msg = f"Rollback failed for {action}: {e}"
                logger.error(error_msg)
                rollback_errors.append(error_msg)
        
        if rollback_errors:
            logger.error(f"Some rollbacks failed: {rollback_errors}")


class BatchTransactionManager(TransactionManager):
    """
    Enhanced transaction manager that supports batched operations.
    This version optimizes by grouping operations by service and
    processing them in parallel where possible.
    """
    
    def execute(self) -> bool:
        """
        Execute the transaction with optimization for batched operations.
        
        Returns:
            bool: True if the transaction was successful, False otherwise.
        """
        if not self.operations:
            logger.info("Empty operations list. Transaction completed successfully.")
            return True
        
        # Group operations by service
        service_operations = {}
        for service_name, action, data in self.operations:
            if service_name not in self.services:
                logger.error(f"Service {service_name} not found")
                return False
            
            if service_name not in service_operations:
                service_operations[service_name] = []
            
            service_operations[service_name].append((action, data))
        
        try:
            # Process each service's operations sequentially
            # (but could process different services in parallel if needed)
            for service_name, ops in service_operations.items():
                service = self.services[service_name]
                
                for action, data in ops:
                    transaction_id = self._perform_with_retry(service, service_name, action, data)
                    
                    with self.lock:
                        self.transaction_log.append((service, action, transaction_id))
            
            logger.info("Transaction completed successfully")
            return True
            
        except ServiceError as e:
            logger.error(f"Transaction failed: {e}")
            self._rollback()
            return False
    
    def _rollback(self) -> None:
        """
        Roll back all completed operations in reverse order.
        Uses parallel processing for rollbacks when possible.
        """
        logger.info("Starting transaction rollback with parallel processing")
        
        # Make a copy to avoid race conditions
        with self.lock:
            operations_to_rollback = list(reversed(self.transaction_log))
            self.transaction_log = []
        
        # Group rollback operations by service
        service_rollbacks = {}
        for service, action, transaction_id in operations_to_rollback:
            if service not in service_rollbacks:
                service_rollbacks[service] = []
            
            service_rollbacks[service].append((action, transaction_id))
        
        # Create threads for each service's rollbacks
        threads = []
        rollback_errors = []
        error_lock = threading.Lock()
        
        def rollback_service_operations(service, operations):
            for action, transaction_id in operations:
                try:
                    logger.info(f"Rolling back {action} with transaction_id {transaction_id}")
                    service.rollback(action, transaction_id)
                    logger.info(f"Successfully rolled back {action}")
                except ServiceError as e:
                    error_msg = f"Rollback failed for {action}: {e}"
                    logger.error(error_msg)
                    with error_lock:
                        rollback_errors.append(error_msg)
        
        # Start rollback threads
        for service, operations in service_rollbacks.items():
            thread = threading.Thread(
                target=rollback_service_operations,
                args=(service, operations)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all rollbacks to complete
        for thread in threads:
            thread.join()
        
        if rollback_errors:
            logger.error(f"Some rollbacks failed: {rollback_errors}")


def orchestrate_transaction(operations: List[Tuple[str, str, Dict[str, Any]]], 
                           services: Dict[str, Any]) -> bool:
    """
    Orchestrates a distributed transaction across multiple services.
    
    Args:
        operations: List of operations to perform. Each operation is a tuple of
                    (service_name, action, data).
        services: Dictionary mapping service names to service objects.
        
    Returns:
        bool: True if the transaction was successful, False otherwise.
    """
    # Use BatchTransactionManager for optimized processing
    transaction_manager = BatchTransactionManager(operations, services)
    return transaction_manager.execute()