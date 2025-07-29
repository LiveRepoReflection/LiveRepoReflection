import threading
import time
from typing import Dict, List, Tuple, Optional


class Node:
    """
    Represents a participant in a distributed transaction.
    """
    def __init__(self, node_id: str):
        """
        Initialize a Node with a unique identifier.
        
        Args:
            node_id: A unique identifier for the node.
        """
        self.node_id: str = node_id
        self.current_operation: Optional[str] = None
        self._lock = threading.Lock()  # For thread safety
    
    def prepare(self, operation: str) -> bool:
        """
        Simulates the tentative execution of an operation.
        
        Args:
            operation: A string describing the operation to be performed.
            
        Returns:
            True if the operation can be prepared successfully, False otherwise.
        """
        with self._lock:
            # In a real implementation, we would attempt to validate and prepare the operation
            # For this simplified implementation, we always succeed
            self.current_operation = operation
            return True
    
    def commit(self) -> None:
        """
        Makes the prepared operation permanent.
        """
        with self._lock:
            # In a real implementation, we would commit the tentative changes
            # For this simplified implementation, we just clear the operation
            self.current_operation = None
    
    def rollback(self) -> None:
        """
        Undoes the prepared operation.
        """
        with self._lock:
            # In a real implementation, we would undo any tentative changes
            # For this simplified implementation, we just clear the operation
            self.current_operation = None


class TransactionCoordinator:
    """
    Manages distributed transactions across multiple participating nodes using
    the two-phase commit protocol.
    """
    def __init__(self, timeout: int):
        """
        Initialize a TransactionCoordinator with a timeout value.
        
        Args:
            timeout: Maximum time (in seconds) to wait for a node to respond
                   during the prepare phase.
        """
        self.timeout: int = timeout
        self.nodes: Dict[str, Node] = {}
        self._lock = threading.Lock()  # For thread safety
    
    def register_node(self, node: Node) -> None:
        """
        Registers a Node instance with the coordinator.
        
        Args:
            node: The Node instance to register.
            
        Raises:
            ValueError: If a node with the same ID is already registered.
        """
        with self._lock:
            if node.node_id in self.nodes:
                raise ValueError(f"Node with ID '{node.node_id}' is already registered")
            self.nodes[node.node_id] = node
    
    def execute_transaction(self, operations: List[Tuple[str, str]]) -> bool:
        """
        Executes a distributed transaction using the two-phase commit protocol.
        
        Args:
            operations: A list of tuples, where each tuple contains (node_id, operation).
                       node_id identifies the node that should execute the operation.
                       
        Returns:
            True if the transaction commits successfully, False if it rolls back.
            
        Raises:
            ValueError: If an operation references a node that is not registered.
        """
        # If there are no operations, the transaction succeeds trivially
        if not operations:
            return True
        
        # Phase 1: Prepare - Collect all participating nodes and ask them to prepare
        participating_nodes = {}
        prepare_results = {}
        
        with self._lock:
            # Verify all nodes exist before proceeding
            for node_id, _ in operations:
                if node_id not in self.nodes:
                    raise ValueError(f"Node with ID '{node_id}' is not registered")
                participating_nodes[node_id] = self.nodes[node_id]
        
        # Create threads to prepare each operation in parallel
        prepare_threads = []
        
        for node_id, operation in operations:
            node = participating_nodes[node_id]
            thread = threading.Thread(
                target=self._prepare_operation,
                args=(node, operation, prepare_results)
            )
            prepare_threads.append(thread)
            thread.start()
        
        # Wait for all prepare operations to complete or timeout
        start_time = time.time()
        for thread in prepare_threads:
            remaining_time = max(0, self.timeout - (time.time() - start_time))
            thread.join(remaining_time)
        
        # Check if all operations prepared successfully within the timeout
        all_prepared = True
        for node_id, operation in operations:
            if node_id not in prepare_results or not prepare_results[node_id]:
                all_prepared = False
                break
        
        # Phase 2: Commit or Rollback
        if all_prepared:
            # All nodes prepared successfully, proceed with commit
            commit_threads = []
            for node_id in participating_nodes:
                thread = threading.Thread(
                    target=self._commit_operation,
                    args=(participating_nodes[node_id],)
                )
                commit_threads.append(thread)
                thread.start()
            
            # Wait for all commit operations to complete
            for thread in commit_threads:
                thread.join()
            
            return True
        else:
            # At least one node failed to prepare or timed out, rollback all nodes
            rollback_threads = []
            for node_id in participating_nodes:
                thread = threading.Thread(
                    target=self._rollback_operation,
                    args=(participating_nodes[node_id],)
                )
                rollback_threads.append(thread)
                thread.start()
            
            # Wait for all rollback operations to complete
            for thread in rollback_threads:
                thread.join()
            
            return False
    
    def _prepare_operation(self, node: Node, operation: str, results: Dict[str, bool]) -> None:
        """
        Helper method to prepare an operation on a node and store the result.
        
        Args:
            node: The node to prepare the operation on.
            operation: The operation to prepare.
            results: Dictionary to store the result of the prepare operation.
        """
        try:
            success = node.prepare(operation)
            with self._lock:
                results[node.node_id] = success
        except Exception:
            # If any exception occurs during prepare, consider it a failure
            with self._lock:
                results[node.node_id] = False
    
    def _commit_operation(self, node: Node) -> None:
        """
        Helper method to commit an operation on a node.
        
        Args:
            node: The node to commit the operation on.
        """
        try:
            node.commit()
        except Exception:
            # In a real implementation, we would log the error
            # In a more sophisticated implementation, we might attempt to retry
            # the commit or handle this failure more gracefully
            pass
    
    def _rollback_operation(self, node: Node) -> None:
        """
        Helper method to rollback an operation on a node.
        
        Args:
            node: The node to rollback the operation on.
        """
        try:
            node.rollback()
        except Exception:
            # In a real implementation, we would log the error
            # Rollback failures are serious and might require manual intervention
            pass