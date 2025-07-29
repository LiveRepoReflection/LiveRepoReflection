#include "tx_coordinator.h"
#include "catch.hpp"
#include <chrono>
#include <thread>
#include <functional>

// Helper function to create participant behaviors
std::function<std::string(const std::string&)> create_good_participant() {
    return [](const std::string& command) {
        if (command == "prepare") return "prepared";
        if (command == "commit") return "committed";
        return "rolled back";
    };
}

std::function<std::string(const std::string&)> create_failing_participant() {
    return [](const std::string& command) {
        if (command == "prepare") return "abort";
        return "rolled back";
    };
}

std::function<std::string(const std::string&)> create_slow_participant() {
    return [](const std::string& command) {
        std::this_thread::sleep_for(std::chrono::milliseconds(2000));
        if (command == "prepare") return "prepared";
        if (command == "commit") return "committed";
        return "rolled back";
    };
}

TEST_CASE("All participants succeed") {
    std::vector<std::string> addresses = {"service1", "service2", "service3"};
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    for (size_t i = 0; i < 3; ++i) {
        behaviors.push_back(create_good_participant());
    }
    
    REQUIRE(coordinate_transaction(3, addresses, behaviors, 1000, 2000) == true);
}

TEST_CASE("One participant fails") {
    std::vector<std::string> addresses = {"service1", "service2", "service3"};
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    behaviors.push_back(create_good_participant());
    behaviors.push_back(create_failing_participant());
    behaviors.push_back(create_good_participant());
    
    REQUIRE(coordinate_transaction(3, addresses, behaviors, 1000, 2000) == false);
}

TEST_CASE("Timeout during prepare phase") {
    std::vector<std::string> addresses = {"service1", "service2", "service3"};
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    behaviors.push_back(create_good_participant());
    behaviors.push_back(create_slow_participant());
    behaviors.push_back(create_good_participant());
    
    REQUIRE(coordinate_transaction(3, addresses, behaviors, 1000, 2000) == false);
}

TEST_CASE("Single participant success") {
    std::vector<std::string> addresses = {"service1"};
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    behaviors.push_back(create_good_participant());
    
    REQUIRE(coordinate_transaction(1, addresses, behaviors, 1000, 2000) == true);
}

TEST_CASE("Maximum number of participants") {
    std::vector<std::string> addresses;
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    for (int i = 0; i < 100; ++i) {
        addresses.push_back("service" + std::to_string(i));
        behaviors.push_back(create_good_participant());
    }
    
    REQUIRE(coordinate_transaction(100, addresses, behaviors, 1000, 2000) == true);
}

TEST_CASE("Concurrent transactions") {
    std::vector<std::string> addresses = {"service1", "service2", "service3"};
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    for (size_t i = 0; i < 3; ++i) {
        behaviors.push_back(create_good_participant());
    }
    
    std::vector<std::thread> threads;
    std::vector<bool> results(10);
    
    // Launch 10 concurrent transactions
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back([&addresses, &behaviors, i, &results]() {
            results[i] = coordinate_transaction(3, addresses, behaviors, 1000, 2000);
        });
    }
    
    // Wait for all threads to complete
    for (auto& thread : threads) {
        thread.join();
    }
    
    // Verify all transactions succeeded
    for (bool result : results) {
        REQUIRE(result == true);
    }
}

TEST_CASE("Invalid input parameters") {
    std::vector<std::string> addresses = {"service1"};
    std::vector<std::function<std::string(const std::string&)>> behaviors;
    behaviors.push_back(create_good_participant());
    
    // Test with N = 0
    REQUIRE_THROWS(coordinate_transaction(0, addresses, behaviors, 1000, 2000));
    
    // Test with N > 100
    REQUIRE_THROWS(coordinate_transaction(101, addresses, behaviors, 1000, 2000));
    
    // Test with timeout = 0
    REQUIRE_THROWS(coordinate_transaction(1, addresses, behaviors, 0, 2000));
    
    // Test with mismatched N and addresses size
    REQUIRE_THROWS(coordinate_transaction(2, addresses, behaviors, 1000, 2000));
}