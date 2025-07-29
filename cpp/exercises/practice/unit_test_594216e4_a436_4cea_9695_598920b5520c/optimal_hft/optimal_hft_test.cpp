#include "optimal_hft.h"
#include "catch.hpp"
#include <vector>
#include <map>

TEST_CASE("Basic single update test") {
    OrderBookUpdate update{
        36000000,  // 10:00 AM
        {100.0, 99.9},
        {10, 20},
        {100.1, 100.2},
        {15, 25},
        0.01
    };
    std::vector<OrderBookUpdate> batch = {update};
    
    TradingStrategy strategy;
    auto decisions = strategy.processUpdates(batch);
    
    REQUIRE(decisions.size() <= 1);
    if (!decisions.empty()) {
        REQUIRE(decisions[0].timestamp == 36000000);
        REQUIRE((decisions[0].action == "buy" || decisions[0].action == "sell"));
        REQUIRE(decisions[0].shares > 0);
        REQUIRE(decisions[0].shares <= 15);  // Cannot exceed available ask size
    }
}

TEST_CASE("Empty batch test") {
    std::vector<OrderBookUpdate> batch;
    TradingStrategy strategy;
    auto decisions = strategy.processUpdates(batch);
    REQUIRE(decisions.empty());
}

TEST_CASE("Maximum inventory constraint test") {
    std::vector<OrderBookUpdate> batch;
    // Create multiple favorable buying opportunities
    for (int i = 0; i < 10; i++) {
        OrderBookUpdate update{
            36000000 + i*1000,
            {100.0, 99.9},
            {1000, 1000},
            {100.1, 100.2},
            {1000, 1000},
            0.01
        };
        batch.push_back(update);
    }
    
    TradingStrategy strategy;
    auto decisions = strategy.processUpdates(batch);
    
    int total_bought = 0;
    for (const auto& decision : decisions) {
        if (decision.action == "buy") {
            total_bought += decision.shares;
        }
    }
    REQUIRE(total_bought <= 1000);  // Should not exceed inventory limit K
}

TEST_CASE("Price level limit test") {
    OrderBookUpdate update{
        36000000,
        {100.0, 99.9, 99.8, 99.7, 99.6, 99.5},  // More than L=5 levels
        {10, 20, 30, 40, 50, 60},
        {100.1, 100.2, 100.3, 100.4, 100.5, 100.6},
        {15, 25, 35, 45, 55, 65},
        0.01
    };
    std::vector<OrderBookUpdate> batch = {update};
    
    TradingStrategy strategy;
    REQUIRE_THROWS_AS(strategy.processUpdates(batch), std::invalid_argument);
}

TEST_CASE("Batch size limit test") {
    std::vector<OrderBookUpdate> batch;
    // Create batch larger than N=100
    for (int i = 0; i < 101; i++) {
        OrderBookUpdate update{
            36000000 + i*1000,
            {100.0, 99.9},
            {10, 20},
            {100.1, 100.2},
            {15, 25},
            0.01
        };
        batch.push_back(update);
    }
    
    TradingStrategy strategy;
    REQUIRE_THROWS_AS(strategy.processUpdates(batch), std::invalid_argument);
}

TEST_CASE("Trading hours test") {
    // Before trading hours
    OrderBookUpdate early_update{
        -1000,  // Before start of day
        {100.0, 99.9},
        {10, 20},
        {100.1, 100.2},
        {15, 25},
        0.01
    };
    
    // After trading hours
    OrderBookUpdate late_update{
        57600001,  // After 4 PM
        {100.0, 99.9},
        {10, 20},
        {100.1, 100.2},
        {15, 25},
        0.01
    };
    
    TradingStrategy strategy;
    REQUIRE_THROWS_AS(strategy.processUpdates({early_update}), std::invalid_argument);
    REQUIRE_THROWS_AS(strategy.processUpdates({late_update}), std::invalid_argument);
}

TEST_CASE("Negative values test") {
    OrderBookUpdate update{
        36000000,
        {100.0, -99.9},  // Negative price
        {10, 20},
        {100.1, 100.2},
        {-15, 25},  // Negative size
        0.01
    };
    std::vector<OrderBookUpdate> batch = {update};
    
    TradingStrategy strategy;
    REQUIRE_THROWS_AS(strategy.processUpdates(batch), std::invalid_argument);
}

TEST_CASE("Price sorting test") {
    OrderBookUpdate update{
        36000000,
        {99.9, 100.0},  // Bids not sorted highest to lowest
        {10, 20},
        {100.2, 100.1},  // Asks not sorted lowest to highest
        {15, 25},
        0.01
    };
    std::vector<OrderBookUpdate> batch = {update};
    
    TradingStrategy strategy;
    REQUIRE_THROWS_AS(strategy.processUpdates(batch), std::invalid_argument);
}

TEST_CASE("Complex trading scenario test") {
    std::vector<OrderBookUpdate> batch;
    
    // Rising market scenario
    for (int i = 0; i < 5; i++) {
        OrderBookUpdate update{
            36000000 + i*1000,
            {100.0 + i*0.1, 99.9 + i*0.1},
            {10, 20},
            {100.1 + i*0.1, 100.2 + i*0.1},
            {15, 25},
            0.01
        };
        batch.push_back(update);
    }
    
    // Falling market scenario
    for (int i = 0; i < 5; i++) {
        OrderBookUpdate update{
            36000000 + (i+5)*1000,
            {100.0 - i*0.1, 99.9 - i*0.1},
            {10, 20},
            {100.1 - i*0.1, 100.2 - i*0.1},
            {15, 25},
            0.01
        };
        batch.push_back(update);
    }
    
    TradingStrategy strategy;
    auto decisions = strategy.processUpdates(batch);
    
    // Verify decisions maintain inventory constraints
    int current_inventory = 0;
    for (const auto& decision : decisions) {
        if (decision.action == "buy") {
            current_inventory += decision.shares;
        } else {
            current_inventory -= decision.shares;
        }
        REQUIRE(current_inventory >= 0);
        REQUIRE(current_inventory <= 1000);
    }
}