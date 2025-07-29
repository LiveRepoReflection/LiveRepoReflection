#ifndef OPTIMAL_HFT_H
#define OPTIMAL_HFT_H

#include <string>
#include <vector>

struct OrderBookUpdate {
    int timestamp;
    std::vector<double> bid_prices;
    std::vector<int> bid_sizes;
    std::vector<double> ask_prices;
    std::vector<int> ask_sizes;
    double spread_cost;
};

struct TradingDecision {
    int timestamp;
    std::string action;  // "buy" or "sell"
    int shares;
};

class TradingStrategy {
public:
    std::vector<TradingDecision> processUpdates(const std::vector<OrderBookUpdate>& updates);
};

#endif