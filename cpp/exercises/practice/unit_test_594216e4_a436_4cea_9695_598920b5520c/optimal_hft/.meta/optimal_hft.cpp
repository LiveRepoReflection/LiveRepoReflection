#include "optimal_hft.h"
#include <algorithm>
#include <stdexcept>
#include <map>
#include <cmath>

namespace {
    constexpr int MAX_BATCH_SIZE = 100;
    constexpr int MAX_PRICE_LEVELS = 5;
    constexpr int MAX_INVENTORY = 1000;
    constexpr int TRADING_START = 0;
    constexpr int TRADING_END = 57600000;
    
    void validateUpdate(const OrderBookUpdate& update) {
        // Validate timestamp
        if (update.timestamp < TRADING_START || update.timestamp > TRADING_END) {
            throw std::invalid_argument("Invalid timestamp");
        }

        // Validate price levels
        if (update.bid_prices.size() > MAX_PRICE_LEVELS || 
            update.ask_prices.size() > MAX_PRICE_LEVELS ||
            update.bid_sizes.size() != update.bid_prices.size() ||
            update.ask_sizes.size() != update.ask_prices.size()) {
            throw std::invalid_argument("Invalid price levels");
        }

        // Validate sorting and negative values
        for (size_t i = 0; i < update.bid_prices.size(); ++i) {
            if (update.bid_prices[i] < 0 || update.bid_sizes[i] < 0) {
                throw std::invalid_argument("Negative values not allowed");
            }
            if (i > 0 && update.bid_prices[i] >= update.bid_prices[i-1]) {
                throw std::invalid_argument("Bid prices must be sorted highest to lowest");
            }
        }

        for (size_t i = 0; i < update.ask_prices.size(); ++i) {
            if (update.ask_prices[i] < 0 || update.ask_sizes[i] < 0) {
                throw std::invalid_argument("Negative values not allowed");
            }
            if (i > 0 && update.ask_prices[i] <= update.ask_prices[i-1]) {
                throw std::invalid_argument("Ask prices must be sorted lowest to highest");
            }
        }

        if (update.spread_cost < 0) {
            throw std::invalid_argument("Negative spread cost not allowed");
        }
    }

    struct MarketState {
        int inventory = 0;
        double total_profit = 0.0;
        std::map<double, int> buy_orders;
        std::map<double, int> sell_orders;
    };

    double calculateExpectedValue(double price, double volatility, int time_to_end) {
        // Simple expected value calculation based on historical volatility
        return price * (1 + volatility * std::sqrt(time_to_end / 57600000.0));
    }

    bool shouldTrade(const OrderBookUpdate& update, const MarketState& state, 
                    double expected_value, bool is_buy) {
        if (is_buy) {
            if (state.inventory >= MAX_INVENTORY) return false;
            return update.ask_prices[0] < expected_value - update.spread_cost;
        } else {
            if (state.inventory <= 0) return false;
            return update.bid_prices[0] > expected_value + update.spread_cost;
        }
    }
}

std::vector<TradingDecision> TradingStrategy::processUpdates(
    const std::vector<OrderBookUpdate>& updates) {
    
    if (updates.size() > MAX_BATCH_SIZE) {
        throw std::invalid_argument("Batch size exceeds limit");
    }

    std::vector<TradingDecision> decisions;
    MarketState state;
    
    // Historical volatility estimation (simplified)
    double volatility = 0.001;  // 0.1% assumed baseline volatility
    
    for (const auto& update : updates) {
        validateUpdate(update);
        
        // Calculate time remaining in trading day
        int time_to_end = TRADING_END - update.timestamp;
        
        // Calculate expected value based on current market conditions
        double mid_price = (update.bid_prices[0] + update.ask_prices[0]) / 2.0;
        double expected_value = calculateExpectedValue(mid_price, volatility, time_to_end);
        
        // Trading logic
        if (shouldTrade(update, state, expected_value, true)) {
            // Buy decision
            int available_capacity = MAX_INVENTORY - state.inventory;
            int trade_size = std::min(available_capacity, update.ask_sizes[0]);
            
            if (trade_size > 0) {
                TradingDecision decision{
                    update.timestamp,
                    "buy",
                    trade_size
                };
                decisions.push_back(decision);
                state.inventory += trade_size;
                state.total_profit -= (update.ask_prices[0] + update.spread_cost) * trade_size;
            }
        }
        
        if (shouldTrade(update, state, expected_value, false)) {
            // Sell decision
            int trade_size = std::min(state.inventory, update.bid_sizes[0]);
            
            if (trade_size > 0) {
                TradingDecision decision{
                    update.timestamp,
                    "sell",
                    trade_size
                };
                decisions.push_back(decision);
                state.inventory -= trade_size;
                state.total_profit += (update.bid_prices[0] - update.spread_cost) * trade_size;
            }
        }
        
        // Update volatility estimate based on price changes
        if (!decisions.empty()) {
            double price_change = std::abs(update.bid_prices[0] - mid_price) / mid_price;
            volatility = 0.95 * volatility + 0.05 * price_change;
        }
        
        // Liquidation strategy near end of day
        if (time_to_end < 300000 && state.inventory > 0) {  // Last 5 minutes
            int liquidation_size = state.inventory;
            TradingDecision decision{
                update.timestamp,
                "sell",
                liquidation_size
            };
            decisions.push_back(decision);
            state.inventory = 0;
            state.total_profit += (update.bid_prices[0] - update.spread_cost) * liquidation_size;
        }
    }
    
    return decisions;
}