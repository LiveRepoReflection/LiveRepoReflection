import sys
from itertools import combinations

def min_cost_accommodation(num_attendees, num_days, hotels):
    if num_attendees == 0:
        return 0.0
    if not hotels:
        return -1

    min_cost = float('inf')
    
    # Try all possible combinations of hotels (1 to all hotels)
    for r in range(1, len(hotels)+1):
        for hotel_combo in combinations(hotels, r):
            total_cost = 0.0
            remaining_attendees = num_attendees
            
            # Calculate fixed costs
            fixed_costs = sum(h['fixed_cost'] for h in hotel_combo)
            total_cost += fixed_costs
            
            # Check daily capacities
            for day in range(num_days):
                day_capacity = sum(h['daily_capacities'][day] for h in hotel_combo)
                if day_capacity < num_attendees:
                    break
            else:
                # All days have sufficient capacity
                # Find optimal distribution among hotels
                attendees_dist = distribute_attendees(num_attendees, hotel_combo, num_days)
                if attendees_dist is None:
                    continue
                
                # Calculate variable costs
                variable_cost = 0.0
                for h, count in zip(hotel_combo, attendees_dist):
                    if count > 0:
                        variable_cost += sum(h['daily_rates'][day] * count for day in range(num_days))
                total_cost += variable_cost
                
                if total_cost < min_cost:
                    min_cost = total_cost
    
    return min_cost if min_cost != float('inf') else -1

def distribute_attendees(total_attendees, hotels, num_days):
    # This helper function tries to distribute attendees optimally among selected hotels
    # Returns None if no valid distribution exists
    n = len(hotels)
    min_rates = [sum(h['daily_rates']) for h in hotels]
    sorted_hotels = sorted(zip(min_rates, hotels), key=lambda x: x[0])
    
    distribution = [0] * n
    remaining = total_attendees
    
    for i in range(n):
        _, hotel = sorted_hotels[i]
        max_possible = min(remaining, min(hotel['daily_capacities'][day] for day in range(num_days)))
        distribution[i] = max_possible
        remaining -= max_possible
    
    if remaining > 0:
        return None
    
    # Reconstruct original order distribution
    original_order = [0] * n
    for i in range(n):
        for j in range(n):
            if hotels[j]['id'] == sorted_hotels[i][1]['id']:
                original_order[j] = distribution[i]
                break
    
    return original_order