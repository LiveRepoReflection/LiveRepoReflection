def find_optimal_meeting_point(cities, team_locations, get_travel_cost, K):
    """
    Determines the optimal meeting city that minimizes the total travel cost for K meetings.
    
    Parameters:
        cities (list of str): List of available city identifiers.
        team_locations (dict): Dictionary mapping team member IDs to their origin city (str).
        get_travel_cost (function): A function that takes two cities (str) and returns the travel cost (int).
        K (int): The number of meetings.
        
    Returns:
        str or None: The city identifier that minimizes the total travel cost, or None if team_locations is empty.
    """
    if not team_locations:
        return None

    # Aggregate the frequency of team members in each origin city.
    freq = {}
    for member, origin in team_locations.items():
        freq[origin] = freq.get(origin, 0) + 1

    best_city = None
    best_cost = None
    # Cache to avoid recomputing the same get_travel_cost calls.
    cost_cache = {}

    # Evaluate each candidate meeting city.
    for candidate in cities:
        total_cost = 0
        for origin, count in freq.items():
            key = (origin, candidate)
            if key not in cost_cache:
                cost_cache[key] = get_travel_cost(origin, candidate)
            total_cost += count * cost_cache[key]
        total_cost *= K
        
        if best_cost is None or total_cost < best_cost:
            best_cost = total_cost
            best_city = candidate

    return best_city