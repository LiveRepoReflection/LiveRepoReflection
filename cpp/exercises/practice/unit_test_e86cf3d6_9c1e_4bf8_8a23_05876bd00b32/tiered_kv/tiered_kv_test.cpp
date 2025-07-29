#include "tiered_kv.h"
#include "catch.hpp"
#include <thread>
#include <vector>
#include <optional>
#include <string>
#include <atomic>

using namespace std;

TEST_CASE("get non-existent key returns nullopt", "[tiered_kv]") {
    auto value = tiered_kv::get("nonexistent");
    REQUIRE(!value.has_value());
}

TEST_CASE("put then get returns correct value", "[tiered_kv]") {
    string key = "testKey";
    string value = "testValue";
    bool putResult = tiered_kv::put(key, value);
    REQUIRE(putResult == true);
    auto retValue = tiered_kv::get(key);
    REQUIRE(retValue.has_value());
    REQUIRE(retValue.value() == value);
}

TEST_CASE("delete key removes key from store", "[tiered_kv]") {
    string key = "deleteTest";
    string value = "toBeDeleted";
    REQUIRE(tiered_kv::put(key, value));
    auto retValue = tiered_kv::get(key);
    REQUIRE(retValue.has_value());
    REQUIRE(retValue.value() == value);
    bool deleteResult = tiered_kv::deleteKey(key);
    REQUIRE(deleteResult == true);
    auto postDelete = tiered_kv::get(key);
    REQUIRE(!postDelete.has_value());
}

TEST_CASE("update key returns new value", "[tiered_kv]") {
    string key = "updateTest";
    string initial = "firstValue";
    string updated = "secondValue";
    REQUIRE(tiered_kv::put(key, initial));
    auto retInitial = tiered_kv::get(key);
    REQUIRE(retInitial.has_value());
    REQUIRE(retInitial.value() == initial);
    REQUIRE(tiered_kv::put(key, updated));
    auto retUpdated = tiered_kv::get(key);
    REQUIRE(retUpdated.has_value());
    REQUIRE(retUpdated.value() == updated);
}

TEST_CASE("concurrent put and get operations", "[tiered_kv]") {
    const int numThreads = 10;
    const int opsPerThread = 100;
    vector<thread> putThreads;
    atomic<int> successfulPuts{0};

    // Concurrent put operations
    for (int i = 0; i < numThreads; ++i) {
        putThreads.emplace_back([i, opsPerThread, &successfulPuts]() {
            for (int j = 0; j < opsPerThread; ++j) {
                string key = "concurrent_" + to_string(i) + "_" + to_string(j);
                string value = "value_" + to_string(i) + "_" + to_string(j);
                if (tiered_kv::put(key, value)) {
                    ++successfulPuts;
                }
            }
        });
    }

    for (auto& th : putThreads) {
        th.join();
    }
    REQUIRE(successfulPuts == numThreads * opsPerThread);

    // Concurrent get operations
    vector<thread> getThreads;
    atomic<int> successfulGets{0};
    for (int i = 0; i < numThreads; ++i) {
        getThreads.emplace_back([i, opsPerThread, &successfulGets]() {
            for (int j = 0; j < opsPerThread; ++j) {
                string key = "concurrent_" + to_string(i) + "_" + to_string(j);
                auto retValue = tiered_kv::get(key);
                if (retValue.has_value()) {
                    string expected = "value_" + to_string(i) + "_" + to_string(j);
                    if (retValue.value() == expected) {
                        ++successfulGets;
                    }
                }
            }
        });
    }

    for (auto& th : getThreads) {
        th.join();
    }
    REQUIRE(successfulGets == numThreads * opsPerThread);
}

TEST_CASE("handling empty key and value", "[tiered_kv]") {
    string emptyKey = "";
    string emptyValue = "";
    REQUIRE(tiered_kv::put(emptyKey, emptyValue));
    auto retValue = tiered_kv::get(emptyKey);
    REQUIRE(retValue.has_value());
    REQUIRE(retValue.value() == emptyValue);
    REQUIRE(tiered_kv::deleteKey(emptyKey));
    auto afterDelete = tiered_kv::get(emptyKey);
    REQUIRE(!afterDelete.has_value());
}