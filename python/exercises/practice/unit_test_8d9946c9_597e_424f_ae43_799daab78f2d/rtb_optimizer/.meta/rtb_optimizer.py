import heapq
import time
from collections import deque
import math


def optimize_rtb(bid_requests, budget, time_limit, model, bidding_strategy):
    """
    Optimize real-time bidding (RTB) for an advertising campaign.
    
    Args:
        bid_requests: An iterable of bid request dictionaries, each with keys:
            'user_id', 'ad_slot', 'user_context', 'timestamp'.
        budget: The total budget for the campaign (float).
        time_limit: The total duration of the campaign (in seconds, float).
        model: A function that predicts the value of showing an ad to a specific user.
        bidding_strategy: A function that takes the predicted value and returns a bid price.
    
    Returns:
        A list of tuples, each representing a bid placed by the algorithm:
        (timestamp, bid_price, predicted_value, user_id, ad_slot).
    """
    if not bid_requests or budget <= 0 or time_limit <= 0:
        return []
    
    # Sort bid requests by timestamp if they're not already sorted
    # Using a priority queue to efficiently process requests in chronological order
    bid_queue = []
    for request in bid_requests:
        heapq.heappush(bid_queue, (request['timestamp'], request))
    
    if not bid_queue:
        return []
    
    # Get the start time of the campaign
    start_time = bid_queue[0][0]
    end_time = start_time + time_limit
    
    # Initialize variables to track budget, time, and bids
    remaining_budget = budget
    bids = []
    
    # Parameters for adaptive bidding
    spent_budget = 0
    processed_requests = 0
    value_threshold = 0.0  # Dynamic threshold for value
    
    # Window for tracking recent value/cost ratio
    recent_values = deque(maxlen=50)
    recent_costs = deque(maxlen=50)
    
    # Count high-value user segments to balance exploration/exploitation
    segment_counts = {}
    segment_values = {}
    
    # Process bid requests
    while bid_queue and remaining_budget > 0:
        current_time, request = heapq.heappop(bid_queue)
        
        # Skip if outside time window
        if current_time > end_time:
            continue
        
        user_id = request['user_id']
        ad_slot = request['ad_slot']
        user_context = request['user_context']
        
        # Define a simple user segment (could be more sophisticated)
        if 'interests' in user_context:
            segment = tuple(sorted(user_context['interests']))
        else:
            segment = 'unknown'
        
        # Update segment stats
        segment_counts[segment] = segment_counts.get(segment, 0) + 1
        
        # Calculate time progress and budget progress
        time_progress = min(1.0, (current_time - start_time) / time_limit)
        budget_progress = min(1.0, spent_budget / budget)
        
        # Predict value using the model
        predicted_value = model(user_id, ad_slot, user_context)
        
        # Exploration factor - explore less explored segments more
        exploration_factor = 1.0
        if segment in segment_counts and segment_counts[segment] > 10:
            exploration_factor = 0.9  # Reduce exploration for well-known segments
            
            # If we have value data for this segment, adjust based on performance
            if segment in segment_values:
                avg_value = segment_values[segment]
                if predicted_value > avg_value * 1.2:  # 20% better than average
                    exploration_factor = 1.1  # Explore more
        
        # Adjust bid price based on remaining budget and time
        # If spending too fast, reduce bid prices
        # If spending too slow, increase bid prices
        spending_ratio = budget_progress / max(0.001, time_progress)
        
        # Calculate the adjustment factor
        if spending_ratio > 1.2:  # Spending too fast
            adjustment = 0.8  # Reduce bids
        elif spending_ratio < 0.8:  # Spending too slow
            adjustment = 1.2  # Increase bids
        else:
            adjustment = 1.0  # On track
        
        # Calculate expected value/cost ratio
        avg_value_cost_ratio = 1.0
        if recent_values and recent_costs:
            avg_value = sum(recent_values) / len(recent_values)
            avg_cost = sum(recent_costs) / len(recent_costs)
            if avg_cost > 0:
                avg_value_cost_ratio = avg_value / avg_cost
        
        # Adjust value threshold dynamically
        remaining_time_ratio = (end_time - current_time) / time_limit
        budget_per_time = remaining_budget / max(0.001, remaining_time_ratio * time_limit)
        
        # Dynamic threshold that increases as we run out of budget
        dynamic_threshold = 0.1 + 0.5 * (1 - (remaining_budget / budget))
        
        # Apply all adjustment factors to the bidding strategy
        base_bid_price = bidding_strategy(predicted_value)
        adjusted_bid_price = base_bid_price * adjustment * exploration_factor
        
        # Calculate reserve price (minimum bid we're willing to make)
        reserve_price = base_bid_price * 0.5
        
        # Update segment value data
        if segment in segment_values:
            segment_values[segment] = (segment_values[segment] * 0.9 + predicted_value * 0.1)
        else:
            segment_values[segment] = predicted_value
        
        # Decide whether to bid
        should_bid = False
        
        # Always bid on high-value opportunities
        if predicted_value > 0.8:
            should_bid = True
        # For medium-value opportunities, bid if we have budget to spare
        elif predicted_value > dynamic_threshold and adjusted_bid_price <= remaining_budget:
            # Bid more selectively as we run out of budget
            if remaining_budget > budget * 0.5 or predicted_value > dynamic_threshold * 1.5:
                should_bid = True
        # Occasionally bid on lower-value opportunities for exploration
        elif random.random() < 0.05 * exploration_factor and remaining_budget > budget * 0.3:
            should_bid = True
        
        # Final check: don't bid if it would exceed our remaining budget
        if should_bid and adjusted_bid_price <= remaining_budget:
            # Place the bid
            final_bid_price = min(adjusted_bid_price, remaining_budget)
            bids.append((current_time, final_bid_price, predicted_value, user_id, ad_slot))
            
            # Update remaining budget
            remaining_budget -= final_bid_price
            spent_budget += final_bid_price
            
            # Update recent value/cost tracking
            recent_values.append(predicted_value)
            recent_costs.append(final_bid_price)
        
        processed_requests += 1
        
        # Periodically recalibrate bidding strategy
        if processed_requests % 100 == 0:
            # Adjust value threshold based on observed performance
            if recent_values and recent_costs:
                avg_value = sum(recent_values) / len(recent_values)
                avg_cost = sum(recent_costs) / len(recent_costs)
                
                # Update threshold based on recent performance
                if avg_value > 0 and avg_cost > 0:
                    value_threshold = 0.8 * value_threshold + 0.2 * (avg_cost / avg_value)
    
    return bids


# Enhanced bidding strategy
def enhanced_bidding_strategy(predicted_value, budget_remaining, total_budget, time_remaining, total_time):
    """
    An enhanced bidding strategy that takes into account remaining budget and time.
    
    Args:
        predicted_value: The predicted value from the model.
        budget_remaining: The remaining budget.
        total_budget: The total budget.
        time_remaining: The remaining time.
        total_time: The total time.
    
    Returns:
        A bid price.
    """
    # Base bid is proportional to predicted value
    base_bid = predicted_value * 2.0
    
    # Calculate budget and time progress
    budget_progress = 1 - (budget_remaining / total_budget)
    time_progress = 1 - (time_remaining / total_time)
    
    # Adjust bid based on spending pace
    if time_progress > 0:
        spending_pace = budget_progress / time_progress
        
        if spending_pace > 1.1:  # Spending too fast
            adjustment = 0.9
        elif spending_pace < 0.9:  # Spending too slow
            adjustment = 1.1
        else:  # On track
            adjustment = 1.0
            
        # Apply adjustment
        base_bid *= adjustment
    
    return base_bid


# Import for random used in the code
import random