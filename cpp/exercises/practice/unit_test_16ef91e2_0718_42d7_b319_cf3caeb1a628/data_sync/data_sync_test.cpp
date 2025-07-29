#include "data_sync.h"
#include "catch.hpp"
#include <map>
#include <vector>
#include <set>
#include <algorithm>

TEST_CASE("Simple case with more remote updates", "[get_missing_updates][case1]") {
    std::map<int, int> local_version_vector = {{1, 5}, {2, 3}, {3, 1}};
    std::map<int, int> remote_version_vector = {{1, 5}, {2, 5}, {3, 2}, {4, 1}};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    // Convert to set for easier comparison regardless of order
    std::set<int> missing_updates_set(missing_updates.begin(), missing_updates.end());
    std::set<int> expected_set = {2, 3, 4};
    
    REQUIRE(missing_updates_set == expected_set);
}

TEST_CASE("No updates needed", "[get_missing_updates][case2]") {
    std::map<int, int> local_version_vector = {{1, 5}, {2, 3}, {3, 1}};
    std::map<int, int> remote_version_vector = {{1, 5}, {2, 3}, {3, 1}};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    REQUIRE(missing_updates.empty());
}

TEST_CASE("Local has more updates than remote", "[get_missing_updates][case3]") {
    std::map<int, int> local_version_vector = {{1, 5}, {2, 5}, {3, 2}, {4, 1}};
    std::map<int, int> remote_version_vector = {{1, 5}, {2, 3}, {3, 1}};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    REQUIRE(missing_updates.empty());
}

TEST_CASE("Mixed case with some updates needed", "[get_missing_updates][case4]") {
    std::map<int, int> local_version_vector = {{1, 10}, {2, 5}, {3, 7}, {4, 3}};
    std::map<int, int> remote_version_vector = {{1, 8}, {2, 8}, {3, 7}, {5, 1}};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    std::set<int> missing_updates_set(missing_updates.begin(), missing_updates.end());
    std::set<int> expected_set = {2, 5};
    
    REQUIRE(missing_updates_set == expected_set);
}

TEST_CASE("Empty local version vector", "[get_missing_updates][case5]") {
    std::map<int, int> local_version_vector = {};
    std::map<int, int> remote_version_vector = {{1, 5}, {2, 3}, {3, 1}};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    std::set<int> missing_updates_set(missing_updates.begin(), missing_updates.end());
    std::set<int> expected_set = {1, 2, 3};
    
    REQUIRE(missing_updates_set == expected_set);
}

TEST_CASE("Empty remote version vector", "[get_missing_updates][case6]") {
    std::map<int, int> local_version_vector = {{1, 5}, {2, 3}, {3, 1}};
    std::map<int, int> remote_version_vector = {};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    REQUIRE(missing_updates.empty());
}

TEST_CASE("Both version vectors are empty", "[get_missing_updates][case7]") {
    std::map<int, int> local_version_vector = {};
    std::map<int, int> remote_version_vector = {};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    REQUIRE(missing_updates.empty());
}

TEST_CASE("Large number of datacenter IDs", "[get_missing_updates][case8]") {
    std::map<int, int> local_version_vector;
    std::map<int, int> remote_version_vector;
    std::set<int> expected_set;
    
    // Generate large version vectors
    for (int i = 1; i <= 1000; i++) {
        local_version_vector[i] = i % 5;
        remote_version_vector[i] = i % 7;
        
        if (remote_version_vector[i] > local_version_vector[i]) {
            expected_set.insert(i);
        }
    }
    
    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    std::set<int> missing_updates_set(missing_updates.begin(), missing_updates.end());
    
    REQUIRE(missing_updates_set == expected_set);
}

TEST_CASE("Disjoint datacenter IDs", "[get_missing_updates][case9]") {
    std::map<int, int> local_version_vector = {{1, 5}, {2, 3}, {3, 1}};
    std::map<int, int> remote_version_vector = {{4, 1}, {5, 2}, {6, 3}};

    std::vector<int> missing_updates = data_sync::get_missing_updates(local_version_vector, remote_version_vector);
    
    std::set<int> missing_updates_set(missing_updates.begin(), missing_updates.end());
    std::set<int> expected_set = {4, 5, 6};
    
    REQUIRE(missing_updates_set == expected_set);
}

// Bonus challenge tests if implemented

#if defined(BONUS_CHALLENGE)

TEST_CASE("Merge version vectors", "[merge_version_vectors][bonus1]") {
    std::map<int, int> vector1 = {{1, 5}, {2, 3}, {3, 1}};
    std::map<int, int> vector2 = {{1, 3}, {2, 5}, {4, 2}};

    std::map<int, int> merged = data_sync::merge_version_vectors(vector1, vector2);
    
    std::map<int, int> expected = {{1, 5}, {2, 5}, {3, 1}, {4, 2}};
    
    REQUIRE(merged == expected);
}

TEST_CASE("Merge empty vectors", "[merge_version_vectors][bonus2]") {
    std::map<int, int> vector1 = {};
    std::map<int, int> vector2 = {{1, 3}, {2, 5}, {4, 2}};

    std::map<int, int> merged1 = data_sync::merge_version_vectors(vector1, vector2);
    std::map<int, int> merged2 = data_sync::merge_version_vectors(vector2, vector1);
    
    REQUIRE(merged1 == vector2);
    REQUIRE(merged2 == vector2);
}

TEST_CASE("Handle datacenter failure and reintegration", "[handle_datacenter_failure][bonus3]") {
    // Setup initial state
    std::map<int, int> datacenter_state = {{1, 5}, {2, 3}, {3, 7}, {4, 2}};
    
    // Simulate datacenter 3 failure
    std::map<int, int> after_failure = data_sync::handle_datacenter_failure(datacenter_state, 3);
    
    // Verify datacenter 3 is marked as failed but state is preserved
    REQUIRE(data_sync::is_datacenter_failed(after_failure, 3));
    REQUIRE(after_failure[3] == 7);  // Original value preserved
    
    // Simulate datacenter 3 reintegration with new updates
    std::map<int, int> reintegrated_state = data_sync::reintegrate_datacenter(after_failure, 3, 9);
    
    REQUIRE(!data_sync::is_datacenter_failed(reintegrated_state, 3));
    REQUIRE(reintegrated_state[3] == 9);  // New value updated
}

#endif