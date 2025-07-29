import random
import math


def optimize_bidding(n, budget, transaction_cost, rounds_data):
    """
    Optimizes real-time bidding strategy to maximize profit in an auction system.
    
    Args:
        n (int): Number of rounds in the auction.
        budget (float): Initial budget available for bidding.
        transaction_cost (float): Transaction cost as a percentage (e.g., 0.01 for 1%).
        rounds_data (list): List of tuples containing user value distribution and previous auction results.
                           Each tuple contains (user_value_distribution, winning_bid, second_highest_bid).
    
    Returns:
        float: Total profit earned across all rounds.
    """
    if n == 0 or budget == 0:
        return 0.0
    
    total_profit = 0.0
    remaining_budget = budget
    rounds_left = n
    
    # Parameters for bidding strategy
    exploration_factor = 0.2  # Balance between exploration and exploitation
    learning_rate = 0.1      # How quickly we adapt to new information
    min_bid_threshold = 0.1  # Minimum bid amount
    
    # Keep track of our bidding performance
    bid_history = []
    value_estimates = []
    competition_estimates = []
    
    for round_idx, round_data in enumerate(rounds_data):
        user_value_dist, prev_winning_bid, prev_second_bid = round_data
        
        # Calculate expected value of this user
        expected_value = sum(value * prob for value, prob in user_value_dist)
        
        # If we have no budget left, skip this round
        if remaining_budget <= 0:
            continue
        
        # Update our understanding of the competition based on previous rounds
        if round_idx > 0:
            # Use previous round data to update our competition model
            competition_estimates.append((prev_winning_bid, prev_second_bid))
        
        # Determine optimal bid for this round
        bid_amount = calculate_bid(
            user_value_dist, 
            competition_estimates,
            remaining_budget, 
            rounds_left,
            transaction_cost,
            exploration_factor,
            min_bid_threshold
        )
        
        # Apply transaction cost to our bid
        effective_bid = bid_amount * (1 + transaction_cost)
        
        # Ensure we don't exceed our remaining budget
        if effective_bid > remaining_budget:
            bid_amount = remaining_budget / (1 + transaction_cost)
            effective_bid = remaining_budget
        
        # Simulate the auction outcome
        # In a real implementation, this would be replaced by actual auction results
        auction_outcome = simulate_auction(
            bid_amount, 
            user_value_dist, 
            prev_winning_bid, 
            prev_second_bid
        )
        
        won_auction, actual_value, payment = auction_outcome
        
        # Update our budget and profit
        if won_auction:
            remaining_budget -= payment * (1 + transaction_cost)
            profit_this_round = actual_value - payment * (1 + transaction_cost)
            total_profit += profit_this_round
            
            # Record this successful bid
            bid_history.append((bid_amount, payment, actual_value))
            value_estimates.append((user_value_dist, actual_value))
        
        rounds_left -= 1
        
        # Adjust exploration factor as we learn more
        if round_idx > n // 3:
            exploration_factor = max(0.05, exploration_factor * 0.95)  # Reduce exploration over time
    
    return total_profit


def calculate_bid(user_value_dist, competition_estimates, budget, rounds_left, 
                 transaction_cost, exploration_factor, min_bid_threshold):
    """
    Calculate the optimal bid amount for the current round.
    
    Args:
        user_value_dist (list): Distribution of possible user values and their probabilities.
        competition_estimates (list): History of winning and second-highest bids.
        budget (float): Remaining budget.
        rounds_left (int): Number of rounds left.
        transaction_cost (float): Transaction cost percentage.
        exploration_factor (float): Factor to control exploration vs. exploitation.
        min_bid_threshold (float): Minimum bid threshold.
        
    Returns:
        float: The bid amount for this round.
    """
    # Calculate expected value for this user
    expected_value = sum(value * prob for value, prob in user_value_dist)
    
    # Estimate the competition's bidding behavior
    estimated_competition_bid = estimate_competition(competition_estimates)
    
    # Base bid on expected value, discounting for transaction costs
    base_bid = expected_value / (1 + transaction_cost) * 0.8  # Conservative base bid
    
    if not competition_estimates:
        # No competition data yet, start conservatively
        bid = min(base_bid * 0.5, budget * 0.1)  # Don't spend more than 10% of budget initially
    else:
        # Adjust bid based on competition estimates
        if estimated_competition_bid < base_bid:
            # Competition is bidding low, we can bid just above them
            bid = min(estimated_competition_bid * 1.1, base_bid)
        else:
            # Competition is bidding high, we need to be more careful
            optimal_ratio = calculate_optimal_bid_ratio(
                expected_value, estimated_competition_bid, transaction_cost
            )
            bid = expected_value * optimal_ratio
    
    # Reserve budget for future rounds
    budget_per_round = budget / max(1, rounds_left)
    bid = min(bid, budget_per_round * 2)  # Allow spending up to 2x the average budget per round
    
    # Add exploration component - occasionally bid higher or lower
    if random.random() < exploration_factor:
        exploration_adjustment = (random.random() - 0.5) * expected_value * 0.4
        bid += exploration_adjustment
    
    # Ensure bid is non-negative and respects minimum threshold
    bid = max(min_bid_threshold, bid)
    
    # Ensure we don't exceed budget
    max_affordable_bid = budget / (1 + transaction_cost)
    bid = min(bid, max_affordable_bid)
    
    return bid


def estimate_competition(competition_estimates):
    """
    Estimate the competitive landscape based on historical bidding data.
    
    Args:
        competition_estimates (list): History of winning and second-highest bids.
        
    Returns:
        float: Estimated bid needed to win.
    """
    if not competition_estimates:
        return 0.1  # Default low value when no data is available
    
    # Focus more on recent auctions
    recent_window = min(10, len(competition_estimates))
    recent_bids = competition_estimates[-recent_window:]
    
    # Extract winning bids and second prices
    winning_bids = [win for win, second in recent_bids if win > 0]
    second_prices = [second for win, second in recent_bids if second > 0]
    
    if not winning_bids:
        return 0.1
    
    # Analyze bidding patterns
    avg_winning_bid = sum(winning_bids) / len(winning_bids) if winning_bids else 0
    avg_second_price = sum(second_prices) / len(second_prices) if second_prices else 0
    
    # Look at trend - is competition increasing?
    if len(winning_bids) > 2:
        recent_trend = winning_bids[-1] - winning_bids[0]
        if recent_trend > 0:
            # Competition is increasing, be more aggressive
            return avg_winning_bid * 1.05
        else:
            # Competition is stable or decreasing
            return max(avg_second_price * 1.1, avg_winning_bid * 0.95)
    
    # Default strategy - bid slightly above the average second price
    return avg_second_price * 1.1


def calculate_optimal_bid_ratio(expected_value, competition_bid, transaction_cost):
    """
    Calculate the optimal ratio of expected value to bid, considering competition and costs.
    
    Args:
        expected_value (float): Expected value of winning the auction.
        competition_bid (float): Estimated competition bid.
        transaction_cost (float): Transaction cost percentage.
        
    Returns:
        float: Optimal bid as a ratio of the expected value.
    """
    # If expected value is too low compared to competition, don't bid aggressively
    if expected_value * 0.8 < competition_bid * (1 + transaction_cost):
        return 0.6  # Conservative bid ratio
    
    # If we can still profit after outbidding competition
    if expected_value > competition_bid * (1 + transaction_cost) * 1.2:
        return 0.85  # More aggressive bid ratio
    
    # Middle ground
    return 0.75


def simulate_auction(bid_amount, user_value_dist, prev_winning_bid, prev_second_bid):
    """
    Simulate the outcome of an auction based on our bid and historical data.
    
    Args:
        bid_amount (float): Our bid amount.
        user_value_dist (list): Distribution of possible user values and their probabilities.
        prev_winning_bid (float): Winning bid from previous round.
        prev_second_bid (float): Second-highest bid from previous round.
        
    Returns:
        tuple: (won_auction, actual_value, payment)
    """
    # Generate competition bids based on historical data
    competition_bid = generate_competition_bid(prev_winning_bid, prev_second_bid)
    
    # Determine if we won
    won_auction = bid_amount > competition_bid
    
    if won_auction:
        # If we won, we pay the second-highest bid (which is the competition bid)
        payment = competition_bid
        
        # Generate the actual value based on the distribution
        actual_value = generate_actual_value(user_value_dist)
        
        return (True, actual_value, payment)
    else:
        # We didn't win the auction
        return (False, 0.0, 0.0)


def generate_competition_bid(prev_winning_bid, prev_second_bid):
    """
    Generate a simulated competition bid based on historical data.
    
    Args:
        prev_winning_bid (float): Winning bid from previous round.
        prev_second_bid (float): Second-highest bid from previous round.
        
    Returns:
        float: Simulated competition bid.
    """
    if prev_winning_bid <= 0 or prev_second_bid <= 0:
        # No historical data, generate a random bid between 1 and 5
        return random.uniform(1.0, 5.0)
    
    # Use historical data with some randomness
    mean_bid = (prev_winning_bid + prev_second_bid) / 2
    std_dev = abs(prev_winning_bid - prev_second_bid) / 2
    
    # Generate bid with some randomness around historical values
    random_component = random.normalvariate(0, std_dev)
    competition_bid = mean_bid + random_component
    
    # Ensure bid is positive
    return max(0.1, competition_bid)


def generate_actual_value(user_value_dist):
    """
    Generate the actual value according to the user value distribution.
    
    Args:
        user_value_dist (list): Distribution of possible user values and their probabilities.
        
    Returns:
        float: Actual value generated.
    """
    # Validate the distribution sums to approximately 1
    total_prob = sum(prob for _, prob in user_value_dist)
    if abs(total_prob - 1.0) > 0.01:
        # If probabilities don't sum to 1, normalize them
        user_value_dist = [(val, prob/total_prob) for val, prob in user_value_dist]
    
    # Generate a random number between 0 and 1
    rand_val = random.random()
    
    # Find the corresponding value based on the cumulative probability
    cumulative_prob = 0.0
    for value, prob in user_value_dist:
        cumulative_prob += prob
        if rand_val <= cumulative_prob:
            return value
    
    # Fallback to the last value if there's some floating-point imprecision
    return user_value_dist[-1][0]