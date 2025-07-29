import random
import math

def l2_norm(vector):
    return math.sqrt(sum(x * x for x in vector))

def clip_vector(vector, clipping_norm):
    norm = l2_norm(vector)
    if norm == 0:
        return vector
    scaling_factor = min(1.0, clipping_norm / norm)
    return [x * scaling_factor for x in vector]

def add_gaussian_noise(vector, noise_scale):
    return [x + random.gauss(0, noise_scale) for x in vector]

def simulate_local_update(global_weights, local_dataset_size, dimension, clipping_norm, dp_epsilon):
    # For simulation, generate a random gradient influenced by dataset size
    # Larger dataset sizes contribute less variance in their updates
    base_gradient = [random.uniform(-1, 1) for _ in range(dimension)]
    # Scale gradient by inverse square root of dataset size to simulate stability
    factor = 1.0 / math.sqrt(local_dataset_size)
    scaled_gradient = [g * factor for g in base_gradient]
    # Clip the gradient to the specified L2 norm
    clipped_gradient = clip_vector(scaled_gradient, clipping_norm)
    # Determine noise scale for differential privacy using Gaussian mechanism
    # Simple heuristic: noise_scale = clipping_norm / dp_epsilon
    noise_scale = clipping_norm / dp_epsilon
    noisy_gradient = add_gaussian_noise(clipped_gradient, noise_scale)
    return noisy_gradient

def run_dp_federated(n_participants, local_dataset_sizes, model_type, dp_epsilon, dp_delta, n_rounds, clipping_norm, learning_rate):
    # Validate input parameters
    if len(local_dataset_sizes) != n_participants:
        raise ValueError("Mismatch between number of participants and length of local_dataset_sizes")
    if dp_epsilon <= 0:
        raise ValueError("dp_epsilon must be positive")
    if dp_delta <= 0:
        raise ValueError("dp_delta must be positive")
    if n_rounds < 0:
        raise ValueError("n_rounds must be non-negative")
    if clipping_norm <= 0:
        raise ValueError("clipping_norm must be positive")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")

    # Select model dimension based on model_type
    if model_type in ("linear_regression", "logistic_regression"):
        dimension = 10
    elif model_type == "neural_network":
        dimension = 20
    else:
        # Default dimension if model type is unknown
        dimension = 10

    # Initialize the global model as a dictionary with a "weights" key
    global_model = {"weights": [0.0 for _ in range(dimension)]}

    total_communication_cost = 0
    # Run training rounds
    for round_idx in range(n_rounds):
        aggregated_update = [0.0 for _ in range(dimension)]
        # Each participant computes a local update
        for i in range(n_participants):
            local_update = simulate_local_update(
                global_model["weights"],
                local_dataset_sizes[i],
                dimension,
                clipping_norm,
                dp_epsilon
            )
            # Aggregate updates by summing
            for j in range(dimension):
                aggregated_update[j] += local_update[j]
            # Update communication cost: each participant sends a vector of size dimension
            total_communication_cost += dimension

        # Average the aggregated update
        averaged_update = [x / n_participants for x in aggregated_update]
        # Update the global model using the averaged update and learning rate
        for j in range(dimension):
            global_model["weights"][j] -= learning_rate * averaged_update[j]

    # Compute convergence metric as the L2 norm of the global model weights (loss proxy)
    convergence_metric = l2_norm(global_model["weights"])

    # Compute total privacy budget spent across all rounds
    total_privacy_budget = (n_rounds * dp_epsilon, n_rounds * dp_delta)

    return global_model, total_privacy_budget, convergence_metric, total_communication_cost