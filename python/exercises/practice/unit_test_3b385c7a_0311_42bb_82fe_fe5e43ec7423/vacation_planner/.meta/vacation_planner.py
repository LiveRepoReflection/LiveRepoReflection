from collections import defaultdict
import heapq
from typing import List, Set, Tuple, Dict

def calculate_happiness_and_cost(
    actions: List[Tuple],
    flights: List[Tuple],
    hotels: List[Tuple],
    activities: List[Tuple]
) -> Tuple[int, int]:
    total_happiness = 0
    total_cost = 0
    
    flight_dict = {(f[0], f[1]): (f[2], f[3]) for f in flights}
    hotel_dict = {h[0]: (h[1], h[2]) for h in hotels}
    activity_dict = {(a[0], a[1]): (a[2], a[3]) for a in activities}
    
    for action in actions:
        if action[0] == "flight":
            cost, happiness = flight_dict[(action[1], action[2])]
            total_cost += cost
            total_happiness += happiness
        elif action[0] == "hotel":
            cost_per_night, happiness_per_night = hotel_dict[action[1]]
            nights = action[2]
            total_cost += cost_per_night * nights
            total_happiness += happiness_per_night * nights
        else:  # activity
            cost, happiness = activity_dict[(action[1], action[2])]
            total_cost += cost
            total_happiness += happiness
            
    return total_happiness, total_cost

def get_reachable_cities(N: int, flights: List[Tuple], start_city: int) -> Set[int]:
    graph = defaultdict(list)
    for f in flights:
        graph[f[0]].append(f[1])
    
    visited = set()
    stack = [start_city]
    
    while stack:
        city = stack.pop()
        if city not in visited:
            visited.add(city)
            stack.extend([c for c in graph[city] if c not in visited])
    
    return visited

def optimize_vacation_plan(
    N: int,
    flights: List[Tuple],
    hotels: List[Tuple],
    activities: List[Tuple],
    start_city: int,
    budget: int,
    duration: int,
    min_stay: int,
    happiness_threshold: int,
    cities_to_visit: Set[int]
) -> List[Tuple]:
    
    # Check if all required cities are reachable
    reachable_cities = get_reachable_cities(N, flights, start_city)
    if not all(city in reachable_cities for city in cities_to_visit):
        return []
    
    # Create adjacency lists and lookup dictionaries
    flight_graph = defaultdict(list)
    for f in flights:
        flight_graph[f[0]].append((f[1], f[2], f[3]))  # city, cost, happiness
    
    hotel_options = defaultdict(list)
    for h in hotels:
        hotel_options[h[0]].append((h[1], h[2]))  # cost_per_night, happiness_per_night
        
    activity_options = defaultdict(list)
    for a in activities:
        activity_options[a[0]].append((a[1], a[2], a[3]))  # name, cost, happiness
    
    # Priority queue entries: (negative_happiness, cost, current_city, days_spent, 
    #                         visited_cities, hotel_nights, actions, done_activities)
    pq = [(0, 0, start_city, 0, {start_city}, 0, [], set())]
    best_solution = []
    best_happiness = -float('inf')
    
    while pq:
        neg_happiness, cost, curr_city, days, visited, hotel_nights, actions, done_activities = heapq.heappop(pq)
        happiness = -neg_happiness
        
        # If we've found a better solution, update it
        if (days == duration and 
            hotel_nights >= min_stay and 
            happiness >= happiness_threshold and 
            cities_to_visit.issubset(visited) and 
            happiness > best_happiness):
            best_solution = actions.copy()
            best_happiness = happiness
            continue
            
        # If we've exceeded any constraints, skip this branch
        if (days > duration or 
            cost > budget or 
            (days == duration and hotel_nights < min_stay) or
            (days == duration and not cities_to_visit.issubset(visited))):
            continue
            
        # Try staying at a hotel
        if days < duration:
            for nights in range(1, duration - days + 1):
                if hotel_options[curr_city]:
                    hotel_cost, hotel_happiness = hotel_options[curr_city][0]
                    new_cost = cost + hotel_cost * nights
                    if new_cost <= budget:
                        new_actions = actions + [("hotel", curr_city, nights)]
                        new_happiness = happiness + hotel_happiness * nights
                        heapq.heappush(pq, 
                            (-new_happiness, new_cost, curr_city, days + nights,
                             visited.copy(), hotel_nights + nights, new_actions, done_activities))
        
        # Try activities
        for activity_name, activity_cost, activity_happiness in activity_options[curr_city]:
            if (curr_city, activity_name) not in done_activities:
                new_cost = cost + activity_cost
                if new_cost <= budget:
                    new_done_activities = done_activities | {(curr_city, activity_name)}
                    new_actions = actions + [("activity", curr_city, activity_name)]
                    new_happiness = happiness + activity_happiness
                    heapq.heappush(pq,
                        (-new_happiness, new_cost, curr_city, days,
                         visited.copy(), hotel_nights, new_actions, new_done_activities))
        
        # Try flights
        if days < duration:
            for next_city, flight_cost, flight_happiness in flight_graph[curr_city]:
                new_cost = cost + flight_cost
                if new_cost <= budget:
                    new_visited = visited | {next_city}
                    new_actions = actions + [("flight", curr_city, next_city)]
                    new_happiness = happiness + flight_happiness
                    heapq.heappush(pq,
                        (-new_happiness, new_cost, next_city, days + 1,
                         new_visited, hotel_nights, new_actions, done_activities))
    
    return best_solution