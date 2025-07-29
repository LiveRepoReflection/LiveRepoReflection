import requests
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TransactionStep:
    """Represents a single step in a distributed transaction saga."""
    
    def __init__(self, service_name, commit_endpoint, compensate_endpoint, data):
        """
        Initialize a transaction step.
        
        Args:
            service_name (str): The name of the service.
            commit_endpoint (str): The URL for committing the transaction.
            compensate_endpoint (str): The URL for compensating the transaction.
            data (dict): The data required for this transaction step.
        """
        self.service_name = service_name
        self.commit_endpoint = commit_endpoint
        self.compensate_endpoint = compensate_endpoint
        self.data = data

def execute_saga(saga, transaction_id):
    """
    Execute a distributed transaction saga.
    
    Args:
        saga (list): A list of TransactionStep objects.
        transaction_id (str): A unique identifier for this saga.
        
    Returns:
        bool: True if the saga was completely successful, False otherwise.
    """
    logger.info(f"Starting saga execution for transaction {transaction_id}")
    
    # Track successfully committed steps for potential compensation
    committed_steps = []
    
    # Execute commit phase
    for step in saga:
        logger.info(f"Executing commit for service {step.service_name} in transaction {transaction_id}")
        
        try:
            # Attempt to commit the transaction
            response = requests.post(
                step.commit_endpoint,
                json={"transaction_id": transaction_id, "data": step.data}
            )
            
            # Check if the commit was successful
            result = response.json()
            if result is True:
                logger.info(f"Commit successful for service {step.service_name} in transaction {transaction_id}")
                committed_steps.append(step)
            else:
                logger.error(f"Commit failed for service {step.service_name} in transaction {transaction_id}")
                execute_compensation(committed_steps, transaction_id)
                return False
                
        except Exception as e:
            logger.error(f"Error during commit for service {step.service_name} in transaction {transaction_id}: {str(e)}")
            execute_compensation(committed_steps, transaction_id)
            return False
    
    logger.info(f"Saga completed successfully for transaction {transaction_id}")
    return True

def execute_compensation(committed_steps, transaction_id):
    """
    Execute compensation for all successfully committed steps in reverse order.
    
    Args:
        committed_steps (list): List of successfully committed TransactionStep objects.
        transaction_id (str): The transaction ID.
    """
    logger.info(f"Starting compensation for transaction {transaction_id}")
    
    # Process steps in reverse order
    for step in reversed(committed_steps):
        logger.info(f"Executing compensation for service {step.service_name} in transaction {transaction_id}")
        
        try:
            # Attempt to compensate the transaction
            response = requests.post(
                step.compensate_endpoint,
                json={"transaction_id": transaction_id, "data": step.data}
            )
            
            # Check if the compensation was successful
            result = response.json()
            if result is True:
                logger.info(f"Compensation successful for service {step.service_name} in transaction {transaction_id}")
            else:
                logger.error(f"Compensation failed for service {step.service_name} in transaction {transaction_id}")
                # Continue with compensation for other steps even if this one failed
                
        except Exception as e:
            logger.error(f"Failed to compensate service {step.service_name} in transaction {transaction_id}: {str(e)}")
            # Continue with compensation for other steps even if this one failed
    
    logger.info(f"Compensation completed for transaction {transaction_id}")