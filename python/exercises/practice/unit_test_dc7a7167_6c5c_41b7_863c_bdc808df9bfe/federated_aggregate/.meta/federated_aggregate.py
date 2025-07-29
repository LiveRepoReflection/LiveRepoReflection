import numpy as np

def evaluate_model_accuracy(model_state, X_val, y_val):
    # Dummy evaluation function which returns a pseudo accuracy.
    # In practice, this would run the model on validation data.
    # Here, we simulate accuracy as the negative L2 norm of all weights (for heuristic purpose)
    acc = 0.0
    for layer in model_state:
        acc -= np.linalg.norm(model_state[layer])
    return acc

def aggregate_model_updates(clients, validation_data, server_aggregation_budget, initial_model):
    # If the server budget is zero or negative, return the initial model unchanged.
    if server_aggregation_budget <= 0:
        return initial_model

    # Collect updates from clients up to each client's max_updates.
    updates_selected = []  # list of tuples: (client priority, layer_name, weight_matrix)
    for client in clients:
        client_updates = client.get("updates", [])
        if not client_updates:
            continue
        n = min(client.get("max_updates", 0), len(client_updates))
        # For the purpose of the heuristic, we select the first n updates.
        selected = client_updates[:n]
        for update in selected:
            layer_name, weight_matrix = update
            # Append tuple (priority, layer_name, weight_matrix)
            updates_selected.append((client.get("priority", 1.0), layer_name, weight_matrix))

    # Sort the collected updates in descending order of priority.
    updates_selected.sort(key=lambda x: x[0], reverse=True)
    # Keep only up to server_aggregation_budget updates.
    updates_selected = updates_selected[:server_aggregation_budget]

    # Initialize aggregated model as a copy of the initial model.
    aggregated_model = {}
    for layer, weights in initial_model.items():
        aggregated_model[layer] = weights.copy()

    # Group updates by layer.
    layer_updates = {}
    for prio, layer, mat in updates_selected:
        if layer not in layer_updates:
            layer_updates[layer] = []
        layer_updates[layer].append((prio, mat))

    # For each layer, compute a weighted average update and combine it with the initial model.
    for layer, updates in layer_updates.items():
        total_weight = sum(prio for prio, _ in updates)
        if total_weight == 0:
            continue
        weighted_sum = np.zeros_like(aggregated_model[layer])
        for prio, mat in updates:
            weighted_sum += prio * mat
        avg_update = weighted_sum / total_weight
        # Incorporate the averaged update into that layer.
        aggregated_model[layer] = aggregated_model[layer] + avg_update

    # In a more advanced approach, the server would try different combinations
    # guided by evaluate_model_accuracy and select the best aggregated model.
    # For this heuristic, we return the aggregated model directly.
    return aggregated_model