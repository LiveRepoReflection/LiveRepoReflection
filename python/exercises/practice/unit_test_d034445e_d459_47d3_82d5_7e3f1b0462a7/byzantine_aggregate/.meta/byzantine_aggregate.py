import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import median_abs_deviation

def aggregate_updates(model_shape, updates, byzantine_fraction, epsilon=1e-6):
    """
    Byzantine-robust aggregation of model updates using coordinate-wise median with MAD filtering.
    
    Args:
        model_shape: Tuple representing the shape of model parameters
        updates: List of numpy arrays containing model updates from each device
        byzantine_fraction: Fraction of devices that may be Byzantine (0 <= f < 0.5)
        epsilon: Small value for numerical stability
    
    Returns:
        Aggregated model update that is resilient to Byzantine failures
    """
    # Input validation
    if not updates:
        raise ValueError("Updates list cannot be empty")
    if byzantine_fraction < 0 or byzantine_fraction >= 0.5:
        raise ValueError("Byzantine fraction must be 0 <= f < 0.5")
    if any(update.shape != model_shape for update in updates):
        raise ValueError("All updates must match the specified model shape")
    
    updates_array = np.array(updates)
    n_devices = len(updates)
    n_byzantine = int(byzantine_fraction * n_devices)
    
    # If no Byzantine nodes expected, return simple mean
    if n_byzantine == 0:
        return np.mean(updates_array, axis=0)
    
    # Reshape updates into 2D array (n_devices x n_parameters)
    flat_updates = updates_array.reshape(n_devices, -1)
    n_params = flat_updates.shape[1]
    
    # Step 1: Compute coordinate-wise median
    median_update = np.median(flat_updates, axis=0)
    
    # Step 2: Compute MAD (Median Absolute Deviation) for each parameter
    mad = median_abs_deviation(flat_updates, axis=0, scale='normal')
    mad = np.maximum(mad, epsilon)  # Ensure numerical stability
    
    # Step 3: Compute normalized distances from median
    distances = np.abs(flat_updates - median_update) / mad
    
    # Step 4: Compute overall device scores (sum of normalized distances)
    device_scores = np.sum(distances, axis=1)
    
    # Step 5: Select top (n_devices - n_byzantine) devices with lowest scores
    top_indices = np.argpartition(device_scores, n_devices - n_byzantine)[:n_devices - n_byzantine]
    filtered_updates = flat_updates[top_indices]
    
    # Step 6: Compute mean of filtered updates
    aggregated_flat = np.mean(filtered_updates, axis=0)
    
    # Reshape back to original model shape
    return aggregated_flat.reshape(model_shape)