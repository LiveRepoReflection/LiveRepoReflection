def optimize_tolls(graph, source, destination, start_time, end_time, num_commuters, predict_traffic):
    """
    Determine the optimal toll for each road segment in the graph to minimize the total social cost.
    The social cost is defined as the sum of actual travel time (ideal travel time multiplied by a congestion factor)
    plus the toll revenue. Commuters choose the path with the lowest perceived cost, which is the sum of actual travel
    time (adjusted for traffic) and the toll on each segment.

    This implementation uses a heuristic approach by assigning a toll on each edge proportional to the expected
    increase in travel time due to congestion. We compute a representative time (midpoint of [start_time, end_time])
    at which we estimate the congestion factor for each edge and then set the toll to be a scaled integer value:
        toll = int( (congestion_factor - 1) * scale )
    where scale is chosen heuristically (here, 5 minutes per extra unit of congestion factor).
    
    This is a heuristic and does not guarantee global optimality.
    
    Parameters:
        graph (dict): A dictionary where keys are start nodes and values are dictionaries mapping end nodes to
                      ideal travel times (integers).
        source (str): The origin node.
        destination (str): The target node.
        start_time (int): Start time in minutes since the beginning of the day (0-1439).
        end_time (int): End time in minutes since the beginning of the day (0-1439).
        num_commuters (int): Number of commuters traveling from source to destination.
        predict_traffic (function): A function predict_traffic(start_node, end_node, current_time) that returns a float
                                    representing the congestion multiplier for the edge at the given time.
                                    
    Returns:
        dict: A dictionary where keys are tuples (start_node, end_node) representing road segments and values
              are the optimal toll amounts (non-negative integers).
    """
    # Calculate a representative time to evaluate traffic conditions.
    mid_time = (start_time + end_time) // 2
    tolls = {}

    # Heuristic parameter: scale factor for converting congestion difference into toll.
    scale = 5

    # For each edge in the graph, compute a toll based on congestion at the representative time.
    for start in graph:
        for end, ideal_time in graph[start].items():
            # Get the congestion multiplier.
            factor = predict_traffic(start, end, mid_time)
            # Calculate heuristic toll. If factor is 1, toll is 0; otherwise proportional to the extra travel time.
            toll = int(max(0, (factor - 1) * scale))
            tolls[(start, end)] = toll

    return tolls


# For direct module testing or ad-hoc runs.
if __name__ == '__main__':
    # Example test scenario.
    graph = {'A': {'B': 10, 'C': 15}, 'B': {'D': 12}, 'C': {'D': 8}}
    source = 'A'
    destination = 'D'
    start_time = 540  # 9:00 AM
    end_time = 600    # 10:00 AM
    num_commuters = 100

    def predict_traffic(start, end, time):
        if (start, end) == ('A', 'B'):
            return 1.5
        elif (start, end) == ('A', 'C'):
            return 2.0
        elif (start, end) == ('B', 'D'):
            return 1.0
        elif (start, end) == ('C', 'D'):
            return 1.2
        return 1.0

    tolls = optimize_tolls(graph, source, destination, start_time, end_time, num_commuters, predict_traffic)
    print(tolls)