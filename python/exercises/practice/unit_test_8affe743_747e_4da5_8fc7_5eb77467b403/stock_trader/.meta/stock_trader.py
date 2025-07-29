def max_profit(K, prices, fee, C):
    if not prices or K == 0:
        return C

    neg_inf = -10**18
    not_hold = [neg_inf] * (K + 1)
    hold = [neg_inf] * (K + 1)
    not_hold[0] = C

    for price in prices:
        for t in range(K - 1, -1, -1):
            if hold[t] != neg_inf:
                candidate = hold[t] + price - fee
                if candidate > not_hold[t + 1]:
                    not_hold[t + 1] = candidate
        for t in range(K + 1):
            if not_hold[t] >= price:
                candidate = not_hold[t] - price
                if candidate > hold[t]:
                    hold[t] = candidate

    return max(not_hold)


if __name__ == "__main__":
    # Example usage:
    K = 2
    prices = [100, 180, 260, 310, 40, 535, 695]
    fee = 10
    C = 100
    print(max_profit(K, prices, fee, C))