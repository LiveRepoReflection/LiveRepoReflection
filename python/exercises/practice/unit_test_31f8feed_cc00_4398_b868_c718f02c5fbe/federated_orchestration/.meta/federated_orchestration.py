import numpy as np
import random
from typing import List, Tuple, Optional

class Device:
    """
    Represents a device participating in federated learning.
    """
    def __init__(self, device_id: int, model_size: int, noise_stddev: float, failure_rate: float):
        self.device_id = device_id
        self.model_size = model_size
        self.noise_stddev = noise_stddev
        self.failure_rate = failure_rate
        # Simulated device capacity (speed factor)
        self.capacity = random.uniform(0.5, 1.5)
    
    def train_local_model(self, global_model: List[float], local_training_steps: int) -> Optional[List[float]]:
        """
        Simulates training a model on local data and returns model updates.
        
        Args:
            global_model: The global model weights
            local_training_steps: Number of training steps
            
        Returns:
            Model updates or None if device fails
        """
        # Simulate device failure
        if random.random() < self.failure_rate:
            return None
        
        # Simulate model updates based on local training
        # For simulation, we generate random updates with magnitude proportional to
        # the number of local training steps and device capacity
        update_magnitude = 0.01 * local_training_steps * self.capacity
        model_updates = [update_magnitude * (random.random() - 0.5) for _ in range(self.model_size)]
        
        # Apply differential privacy (add noise)
        if self.noise_stddev > 0:
            noise = np.random.normal(0, self.noise_stddev, self.model_size)
            model_updates = [update + noise[i] for i, update in enumerate(model_updates)]
            
        # Return model updates
        return model_updates


class FederatedLearningServer:
    """
    Central server that orchestrates the federated learning process.
    """
    def __init__(self, num_devices: int, model_size: int, selection_size: int, 
                 noise_stddev: float, failure_rate: float):
        self.model_size = model_size
        self.selection_size = selection_size
        self.devices = [Device(i, model_size, noise_stddev, failure_rate) 
                        for i in range(num_devices)]
        # Initialize global model with zeros
        self.global_model = [0.0] * model_size
    
    def select_devices(self) -> List[Device]:
        """
        Selects a subset of devices for the current round.
        
        Returns:
            List of selected devices
        """
        return random.sample(self.devices, self.selection_size)
    
    def aggregate_updates(self, updates: List[List[float]]) -> List[float]:
        """
        Aggregates model updates from devices.
        
        Args:
            updates: List of model updates from devices
            
        Returns:
            Aggregated model updates
        """
        if not updates:
            # If no updates were received, return zeros
            return [0.0] * self.model_size
        
        # Simple averaging of updates
        num_updates = len(updates)
        aggregated = [0.0] * self.model_size
        
        for update in updates:
            for i, value in enumerate(update):
                aggregated[i] += value / num_updates
                
        return aggregated
    
    def update_global_model(self, updates: List[float]) -> None:
        """
        Updates the global model with aggregated updates.
        
        Args:
            updates: Aggregated model updates
        """
        for i in range(self.model_size):
            self.global_model[i] += updates[i]
    
    def run_round(self, local_training_steps: int) -> List[float]:
        """
        Runs a single round of federated learning.
        
        Args:
            local_training_steps: Number of local training steps
            
        Returns:
            Updated global model
        """
        # Select devices for this round
        selected_devices = self.select_devices()
        
        # Collect updates from selected devices
        updates = []
        for device in selected_devices:
            device_update = device.train_local_model(
                self.global_model, local_training_steps)
            if device_update is not None:
                updates.append(device_update)
        
        # Aggregate updates
        aggregated_updates = self.aggregate_updates(updates)
        
        # Update global model
        self.update_global_model(aggregated_updates)
        
        # Return a copy of the global model
        return self.global_model.copy()


def validate_input_parameters(num_devices: int, model_size: int, selection_size: int, 
                              noise_stddev: float, failure_rate: float, num_rounds: int, 
                              local_training_steps: int) -> None:
    """
    Validates input parameters for the federated learning simulation.
    
    Args:
        num_devices: Number of devices in the network
        model_size: Size of the model (number of weights)
        selection_size: Number of devices to select per round
        noise_stddev: Standard deviation of noise for differential privacy
        failure_rate: Probability of device failure
        num_rounds: Number of federated learning rounds
        local_training_steps: Number of local training steps per device
        
    Raises:
        ValueError: If any parameter is invalid
    """
    if num_devices < 1:
        raise ValueError("Number of devices must be at least 1")
    if model_size < 1:
        raise ValueError("Model size must be at least 1")
    if selection_size < 1 or selection_size > num_devices:
        raise ValueError("Selection size must be between 1 and the number of devices")
    if noise_stddev < 0.0 or noise_stddev > 1.0:
        raise ValueError("Noise standard deviation must be between 0.0 and 1.0")
    if failure_rate < 0.0 or failure_rate > 1.0:
        raise ValueError("Failure rate must be between 0.0 and 1.0")
    if num_rounds < 1:
        raise ValueError("Number of rounds must be at least 1")
    if local_training_steps < 1:
        raise ValueError("Number of local training steps must be at least 1")


def simulate_federated_learning(num_devices: int, model_size: int, selection_size: int, 
                                noise_stddev: float, failure_rate: float, num_rounds: int, 
                                local_training_steps: int) -> List[List[float]]:
    """
    Simulates the federated learning process.
    
    Args:
        num_devices: Number of devices in the network
        model_size: Size of the model (number of weights)
        selection_size: Number of devices to select per round
        noise_stddev: Standard deviation of noise for differential privacy
        failure_rate: Probability of device failure
        num_rounds: Number of federated learning rounds
        local_training_steps: Number of local training steps per device
        
    Returns:
        List of global models after each round
    """
    # Validate input parameters
    validate_input_parameters(num_devices, model_size, selection_size, 
                             noise_stddev, failure_rate, num_rounds, 
                             local_training_steps)
    
    # Initialize server
    server = FederatedLearningServer(num_devices, model_size, selection_size, 
                                    noise_stddev, failure_rate)
    
    # Run federated learning for specified number of rounds
    results = []
    for _ in range(num_rounds):
        # Run a round and get the updated model
        model = server.run_round(local_training_steps)
        results.append(model)
        
    return results