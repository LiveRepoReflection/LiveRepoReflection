import statistics

def decentralized_auction(bids: list[int], k: int, f: int) -> int:
    """
    Determines the k-th highest bid from a list of bids,
    tolerant to up to f Byzantine faults.

    Args:
        bids: A list of integer bids.
        k: The rank of the desired bid (1 being the highest).
        f: The maximum number of Byzantine faults.

    Returns:
        The k-th highest bid from the list, after mitigating
        the influence of Byzantine nodes. Must be a value from the input bids list.
    """
    if not bids:
        raise ValueError("Bids list cannot be empty")
    
    n = len(bids)
    # Sort bids in descending order
    sorted_bids = sorted(bids, reverse=True)
    
    # Candidate assuming malicious bids are not affecting lower end.
    candidate_low = sorted_bids[k - 1] if k - 1 < n else sorted_bids[-1]
    
    # Candidate adjusted for potential high outliers.
    if k - 1 + f < n:
        candidate_high = sorted_bids[k - 1 + f]
    else:
        candidate_high = candidate_low

    # Compute median to gauge distribution centrality.
    med = statistics.median(bids)
    
    # Calculate deviations from the median at both extremes.
    # Ensure non-negative differences.
    delta_high = abs(sorted_bids[0] - med)
    delta_low = abs(med - sorted_bids[-1])
    
    # Decide which candidate to choose.
    # If the top extreme is far from the median compared to the bottom,
    # assume that high bids may be malicious and select candidate_high.
    if delta_high > delta_low:
        return candidate_high
    else:
        return candidate_low

if __name__ == '__main__':
    # Example usage
    bids = [100, 50, 75, 120, 90, 50, 110, 60, 80, 1000]
    k = 3
    f = 1
    result = decentralized_auction(bids, k, f)
    print(result)