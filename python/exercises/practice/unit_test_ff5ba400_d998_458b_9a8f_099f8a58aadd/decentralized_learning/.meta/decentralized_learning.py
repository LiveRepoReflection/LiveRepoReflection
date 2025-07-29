def decentralized_learning(n, initial_weights, local_data, learning_rate, num_rounds, gradient, test_data, predict):
    """
    Simulates decentralized collaborative learning across n nodes.
    
    Args:
        n: Number of nodes in the network
        initial_weights: List of initial weight vectors for each node
        local_data: List of local datasets for each node
        learning_rate: Learning rate for local updates
        num_rounds: Number of collaborative learning rounds
        gradient: Function to compute gradients
        test_data: Dataset for evaluation
        predict: Function to make predictions
        
    Returns:
        Accuracy of the averaged model on test_data
    """
    # Make copies of initial weights to avoid modifying the input
    current_weights = [weights.copy() for weights in initial_weights]
    
    for _ in range(num_rounds):
        # Step 1: Model Aggregation - collect all weights
        all_weights = current_weights
        
        # Step 2: Weight Averaging
        avg_weights = [sum(w[i] for w in all_weights) / n for i in range(len(all_weights[0]))]
        
        # Step 3: Model Update - distribute averaged weights
        current_weights = [avg_weights.copy() for _ in range(n)]
        
        # Step 4: Local Training
        for i in range(n):
            grad = gradient(current_weights[i], local_data[i])
            current_weights[i] = [w - learning_rate * g for w, g in zip(current_weights[i], grad)]
    
    # After all rounds, compute final averaged weights
    final_avg_weights = [sum(w[i] for w in current_weights) / n for i in range(len(current_weights[0]))]
    
    # Evaluate on test data
    correct = 0
    for feature_vector, true_label in test_data:
        predicted_label = predict(final_avg_weights, feature_vector)
        if predicted_label == true_label:
            correct += 1
    
    accuracy = correct / len(test_data)
    return accuracy