"""
Example usage of the TransactionCoordinator.
"""
from txn_coordinator import Node, TransactionCoordinator

def main():
    # Create nodes for our services
    payment_node = Node("payment_service")
    inventory_node = Node("inventory_service")
    email_node = Node("email_service")
    
    # Create a transaction coordinator with a 5-second timeout
    coordinator = TransactionCoordinator(timeout=5)
    
    # Register the nodes with the coordinator
    coordinator.register_node(payment_node)
    coordinator.register_node(inventory_node)
    coordinator.register_node(email_node)
    
    # Define a transaction that involves multiple services
    operations = [
        ("payment_service", "deduct $10 from customer account"),
        ("inventory_service", "reduce stock of item X by 1"),
        ("email_service", "send order confirmation email")
    ]
    
    print("Executing transaction...")
    
    # Execute the transaction
    success = coordinator.execute_transaction(operations)
    
    if success:
        print("Transaction committed successfully!")
    else:
        print("Transaction rolled back.")
    
    # Try another transaction with a non-existent node
    try:
        invalid_operations = [
            ("payment_service", "deduct $20 from customer account"),
            ("shipping_service", "schedule package delivery")  # This node doesn't exist
        ]
        coordinator.execute_transaction(invalid_operations)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()