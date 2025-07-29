import random

class TransactionCoordinator:
    def __init__(self, num_services: int, commit_probability: float, timeout: int):
        """
        Initialize the transaction coordinator.
        
        Parameters:
        - num_services: The number of services participating in the transaction
        - commit_probability: The probability each service will vote 'commit'
        - timeout: The timeout value for the transaction
        """
        self.num_services = num_services
        self.commit_probability = commit_probability
        self.timeout = timeout
    
    def run_transaction(self) -> bool:
        """
        Runs a single transaction using the Probabilistic Commit Protocol.
        
        Returns:
        - True if the transaction commits (all services vote 'commit')
        - False if the transaction aborts (any service votes 'abort')
        """
        # Phase 1: Prepare (Simulation - in a real system, we would send prepare messages)
        # All services in our simulation will acknowledge the prepare message
        
        # Phase 2: Vote
        # Simulate each service voting based on the commit probability
        votes = self._collect_votes()
        
        # Phase 3: Commit/Abort decision
        # All services must vote commit for the transaction to succeed
        transaction_success = all(votes)
        
        # In a real implementation, we would send commit/abort messages to all services here
        return transaction_success
    
    def _collect_votes(self) -> list[bool]:
        """
        Simulates the voting phase where each service independently decides to commit or abort.
        
        Returns:
        - A list of booleans representing each service's vote (True for 'commit', False for 'abort')
        """
        votes = []
        
        # Each service independently decides to commit or abort
        for _ in range(self.num_services):
            # Generate a random number between 0 and 1
            # If it's less than the commit probability, the service votes to commit
            vote = random.random() < self.commit_probability
            votes.append(vote)
        
        return votes