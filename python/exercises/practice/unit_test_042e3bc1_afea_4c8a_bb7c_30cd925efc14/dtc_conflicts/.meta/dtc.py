import enum
import uuid
from typing import Dict, Optional, List, Set, Any, Tuple


class TransactionState(enum.Enum):
    """Enum representing the possible states of a transaction."""
    ACTIVE = 1
    COMMITTED = 2
    ABORTED = 3


class ConflictError(Exception):
    """Exception raised for transaction conflicts."""
    pass


class Service:
    """Represents a service in the distributed system."""

    def __init__(self, service_id: int):
        self.service_id = service_id
        self.data: Dict[str, Tuple[str, int]] = {}  # Mapping from data_item to (value, version)

    def read(self, data_item: str) -> Tuple[Optional[str], int]:
        """
        Read a data item from the service.
        
        Args:
            data_item: The item to read.
            
        Returns:
            A tuple containing the value and version of the data item.
        """
        if data_item not in self.data:
            return None, 0
        return self.data[data_item]

    def write(self, data_item: str, value: str, expected_version: int) -> bool:
        """
        Write a value to a data item in the service.
        
        Args:
            data_item: The item to write to.
            value: The value to write.
            expected_version: The expected current version of the data item.
            
        Returns:
            True if the write was successful, False if there was a version mismatch.
        """
        current_value, current_version = self.read(data_item)
        
        # Check if the versions match
        if current_version != expected_version:
            return False
        
        # Update the data item with the new value and incremented version
        self.data[data_item] = (value, current_version + 1)
        return True


class Transaction:
    """Represents a transaction in the distributed system."""

    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id
        self.state = TransactionState.ACTIVE
        self.reads: Dict[int, Dict[str, int]] = {}  # service_id -> {data_item -> version}
        self.writes: Dict[int, Dict[str, str]] = {}  # service_id -> {data_item -> new_value}
        self.read_values: Dict[int, Dict[str, str]] = {}  # service_id -> {data_item -> read_value}

    def add_read(self, service_id: int, data_item: str, value: Optional[str], version: int) -> None:
        """
        Record a read operation in this transaction.
        
        Args:
            service_id: The ID of the service being read from.
            data_item: The item being read.
            value: The value read.
            version: The version of the data item read.
        """
        if service_id not in self.reads:
            self.reads[service_id] = {}
        if service_id not in self.read_values:
            self.read_values[service_id] = {}
            
        self.reads[service_id][data_item] = version
        self.read_values[service_id][data_item] = value

    def add_write(self, service_id: int, data_item: str, value: str) -> None:
        """
        Record a write operation in this transaction.
        
        Args:
            service_id: The ID of the service being written to.
            data_item: The item being written to.
            value: The new value to write.
        """
        if service_id not in self.writes:
            self.writes[service_id] = {}
        self.writes[service_id][data_item] = value

    def get_modified_services(self) -> Set[int]:
        """
        Get the set of services that this transaction modifies.
        
        Returns:
            A set of service IDs.
        """
        return set(self.writes.keys())
    
    def is_active(self) -> bool:
        """Check if the transaction is in the active state."""
        return self.state == TransactionState.ACTIVE
    
    def is_committed(self) -> bool:
        """Check if the transaction is in the committed state."""
        return self.state == TransactionState.COMMITTED
    
    def is_aborted(self) -> bool:
        """Check if the transaction is in the aborted state."""
        return self.state == TransactionState.ABORTED


class DistributedTransactionCoordinator:
    """The main Distributed Transaction Coordinator class."""

    def __init__(self):
        self.services: Dict[int, Service] = {}
        self.transactions: Dict[str, Transaction] = {}

    def add_service(self, service_id: int) -> Service:
        """
        Add a new service to the DTC.
        
        Args:
            service_id: The ID of the new service.
            
        Returns:
            The newly created service.
        """
        service = Service(service_id)
        self.services[service_id] = service
        return service

    def begin(self, transaction_id: str) -> None:
        """
        Begin a new transaction.
        
        Args:
            transaction_id: The ID of the new transaction.
        """
        if transaction_id in self.transactions:
            raise ValueError(f"Transaction {transaction_id} already exists")
        self.transactions[transaction_id] = Transaction(transaction_id)

    def read(self, transaction_id: str, service_id: int, data_item: str) -> Optional[str]:
        """
        Read a data item from a service within a transaction.
        
        Args:
            transaction_id: The ID of the transaction.
            service_id: The ID of the service to read from.
            data_item: The item to read.
            
        Returns:
            The value of the data item, or None if it doesn't exist.
            
        Raises:
            ValueError: If the transaction or service doesn't exist or if the transaction is not active.
        """
        # Validate inputs
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} does not exist")
        
        if service_id not in self.services:
            raise ValueError(f"Service {service_id} does not exist")
        
        transaction = self.transactions[transaction_id]
        if not transaction.is_active():
            raise ValueError(f"Transaction {transaction_id} is not active")
        
        # Check if we've already read this item in this transaction
        if (service_id in transaction.read_values and 
            data_item in transaction.read_values[service_id]):
            return transaction.read_values[service_id][data_item]
        
        # Read from the service
        service = self.services[service_id]
        value, version = service.read(data_item)
        
        # Record the read operation
        transaction.add_read(service_id, data_item, value, version)
        
        return value

    def write(self, transaction_id: str, service_id: int, data_item: str, value: str) -> None:
        """
        Write a value to a data item in a service within a transaction.
        
        Args:
            transaction_id: The ID of the transaction.
            service_id: The ID of the service to write to.
            data_item: The item to write to.
            value: The value to write.
            
        Raises:
            ValueError: If the transaction or service doesn't exist or if the transaction is not active.
        """
        # Validate inputs
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} does not exist")
        
        if service_id not in self.services:
            raise ValueError(f"Service {service_id} does not exist")
        
        transaction = self.transactions[transaction_id]
        if not transaction.is_active():
            raise ValueError(f"Transaction {transaction_id} is not active")
        
        # First read the item to get its version
        if (service_id not in transaction.reads or 
            data_item not in transaction.reads[service_id]):
            self.read(transaction_id, service_id, data_item)
        
        # Record the write operation
        transaction.add_write(service_id, data_item, value)

    def commit(self, transaction_id: str) -> str:
        """
        Attempt to commit a transaction.
        
        Args:
            transaction_id: The ID of the transaction to commit.
            
        Returns:
            "SUCCESS" if the commit was successful, "ABORTED" if it was aborted.
            
        Raises:
            ValueError: If the transaction doesn't exist or if the transaction is not active.
        """
        # Validate inputs
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} does not exist")
        
        transaction = self.transactions[transaction_id]
        if not transaction.is_active():
            raise ValueError(f"Transaction {transaction_id} is not active")
        
        # Check for conflicts and perform the writes
        try:
            for service_id, data_items in transaction.writes.items():
                service = self.services[service_id]
                for data_item, new_value in data_items.items():
                    expected_version = transaction.reads[service_id][data_item]
                    success = service.write(data_item, new_value, expected_version)
                    if not success:
                        raise ConflictError(f"Conflict detected in transaction {transaction_id} for service {service_id}, data item {data_item}")
            
            # If we get here, all writes were successful
            transaction.state = TransactionState.COMMITTED
            return "SUCCESS"
            
        except ConflictError:
            # If there was a conflict, abort the transaction
            transaction.state = TransactionState.ABORTED
            return "ABORTED"

    def rollback(self, transaction_id: str) -> str:
        """
        Roll back a transaction.
        
        Args:
            transaction_id: The ID of the transaction to roll back.
            
        Returns:
            "SUCCESS" if the rollback was successful.
            
        Raises:
            ValueError: If the transaction doesn't exist or if the transaction is not active.
        """
        # Validate inputs
        if transaction_id not in self.transactions:
            raise ValueError(f"Transaction {transaction_id} does not exist")
        
        transaction = self.transactions[transaction_id]
        if not transaction.is_active():
            raise ValueError(f"Transaction {transaction_id} is not active")
        
        # Mark the transaction as aborted
        transaction.state = TransactionState.ABORTED
        return "SUCCESS"
    
    def process_command(self, command: str) -> Optional[str]:
        """
        Process a command string.
        
        Args:
            command: A string command in the format specified in the problem description.
            
        Returns:
            A string output message, if any.
            
        Raises:
            ValueError: If the command format is invalid.
        """
        parts = command.strip().split()
        
        if not parts:
            raise ValueError("Empty command")
        
        cmd_type = parts[0]
        
        if cmd_type == "BEGIN":
            if len(parts) != 2:
                raise ValueError(f"Invalid BEGIN command: {command}")
            self.begin(parts[1])
            return None
            
        elif cmd_type == "READ":
            if len(parts) != 4:
                raise ValueError(f"Invalid READ command: {command}")
            try:
                service_id = int(parts[2])
                value = self.read(parts[1], service_id, parts[3])
                return None
            except ValueError as e:
                return f"ERROR: {str(e)}"
                
        elif cmd_type == "WRITE":
            if len(parts) < 5:
                raise ValueError(f"Invalid WRITE command: {command}")
            try:
                service_id = int(parts[2])
                # Combine all parts after the fourth as the value in case it contains spaces
                value = " ".join(parts[4:])
                self.write(parts[1], service_id, parts[3], value)
                return None
            except ValueError as e:
                return f"ERROR: {str(e)}"
                
        elif cmd_type == "COMMIT":
            if len(parts) != 2:
                raise ValueError(f"Invalid COMMIT command: {command}")
            try:
                result = self.commit(parts[1])
                return f"COMMIT {parts[1]} {result}"
            except ValueError as e:
                return f"ERROR: {str(e)}"
                
        elif cmd_type == "ROLLBACK":
            if len(parts) != 2:
                raise ValueError(f"Invalid ROLLBACK command: {command}")
            try:
                result = self.rollback(parts[1])
                return f"ROLLBACK {parts[1]} {result}"
            except ValueError as e:
                return f"ERROR: {str(e)}"
                
        else:
            raise ValueError(f"Unknown command type: {cmd_type}")