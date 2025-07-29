def optimal_relay_placement(data_centers, latency_matrix, max_relays, relay_efficiency):
    n = len(data_centers)

    def compute_average_latency(relays):
        total = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                direct = latency_matrix[i][j]
                if relays:
                    relay_latency = min([(latency_matrix[i][r] + latency_matrix[r][j]) / relay_efficiency for r in relays])
                    effective = min(direct, relay_latency)
                else:
                    effective = direct
                total += effective
                count += 1
        return total / count if count else 0

    # Start with no relay nodes: baseline average latency
    current_relays = []
    current_avg = compute_average_latency(current_relays)

    # Greedy approach: iteratively add the relay that gives maximum improvement,
    # if it improves the current average latency.
    available_nodes = set(data_centers)
    for _ in range(max_relays):
        best_candidate = None
        best_avg = current_avg
        for candidate in available_nodes:
            trial_relays = current_relays + [candidate]
            trial_avg = compute_average_latency(trial_relays)
            if trial_avg < best_avg:
                best_avg = trial_avg
                best_candidate = candidate
        if best_candidate is None:
            break
        current_relays.append(best_candidate)
        available_nodes.remove(best_candidate)
        current_avg = best_avg

    return current_relays