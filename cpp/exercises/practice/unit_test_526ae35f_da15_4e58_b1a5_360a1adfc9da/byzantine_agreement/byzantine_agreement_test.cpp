#include "byzantine_agreement.h"
#include "catch.hpp"
#include <set>

using namespace byzantine_agreement;

TEST_CASE("minimal_nodes_non_faulty") {
    // Only one node (the leader). No lieutenant votes exist.
    int num_nodes = 1;
    std::set<int> faulty_nodes; // no faulty nodes
    int leader_id = 0;
    int proposed_value = 1;
    // Since there are no lieutenants, the result should be 0.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    REQUIRE(result == 0);
}

TEST_CASE("all_honest_leader_proposes_one") {
    // All nodes are honest.
    int num_nodes = 5;
    std::set<int> faulty_nodes; // no faulty nodes
    int leader_id = 0;
    int proposed_value = 1;
    // In a fully honest scenario, every lieutenant (all nodes except the leader)
    // should decide on the leader's proposal. Hence, expected count is num_nodes - 1.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    REQUIRE(result == num_nodes - 1);
}

TEST_CASE("all_honest_leader_proposes_zero") {
    // Test with all honest nodes where the proposed value is 0.
    int num_nodes = 6;
    std::set<int> faulty_nodes; // no faulty nodes
    int leader_id = 2;
    int proposed_value = 0;
    // All lieutenants decide 0. Thus, expected count for decision 1 is 0.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    REQUIRE(result == 0);
}

TEST_CASE("faulty_leader_flip_behavior") {
    // Leader is faulty and follows a deterministic strategy to flip the honest proposal.
    int num_nodes = 4;
    std::set<int> faulty_nodes = {0}; // leader (id 0) is faulty
    int leader_id = 0;
    int proposed_value = 1;
    // Deterministic behavior: a faulty leader sends the flipped bit.
    // Lieutenants are honest. Thus, each lieutenant receives 0 from the leader.
    // In the relay phase, they forward what they received (0). So every lieutenant votes 0.
    // Expected outcome: 0 lieutenants decide 1.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    REQUIRE(result == 0);
}

TEST_CASE("faulty_lieutenant_flip_behavior") {
    // Leader is honest but one of the lieutenants is faulty.
    // Faulty nodes always send the opposite of the value they receive.
    int num_nodes = 4;
    // Let lieutenant with id 1 be faulty.
    std::set<int> faulty_nodes = {1};
    int leader_id = 0;
    int proposed_value = 1;
    // Honest leader sends 1 to all lieutenants.
    // For each honest lieutenant (ids 2 and 3), they receive:
    //   - Direct leader value: 1
    //   - Relay from the other honest lieutenant: 1
    //   - Relay from faulty lieutenant: flipped to 0.
    // So the vote count for an honest lieutenant is {1, 1, 0} leading to a majority of 1.
    // Faulty lieutenant (id 1) does not affect the count since we consider every lieutenant’s decision.
    // Under the deterministic strategy (even faulty nodes follow the same relay rule but flip the received value),
    // faulty node 1 receives (from leader: 1, from other lieutenants: both 1) and possibly flips its behavior.
    // For consistency we assume that every lieutenant, faulty or not, ends up applying the majority rule on the set:
    //   For id 1, if it received the honest messages (1) from ids 2 and 3 and its own flipped message is not counted,
    //   then the majority vote is also 1.
    // Hence, all lieutenants decide on 1.
    // Expected outcome: 3 lieutenants decide 1.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    // Lieutenants count = num_nodes - 1 == 3.
    REQUIRE(result == num_nodes - 1);
}

TEST_CASE("all_nodes_faulty") {
    // All nodes (leader and lieutenants) are faulty.
    int num_nodes = 5;
    std::set<int> faulty_nodes = {0, 1, 2, 3, 4};
    int leader_id = 0;
    int proposed_value = 1;
    // Deterministic faulty strategy:
    // Leader (faulty) sends flipped value: 0.
    // Every faulty lieutenant, when receiving leader's value, flips and sends 1.
    // Thus, each lieutenant receives one 0 (from the leader) and (num_nodes - 2) ones (from other lieutenants).
    // Majority vote in each case yields 1.
    // Expected number of lieutenants deciding on 1 is num_nodes - 1.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    REQUIRE(result == num_nodes - 1);
}

TEST_CASE("mixed_faults") {
    // Mixed scenario: Some lieutenants and possibly the leader faulty.
    int num_nodes = 7;
    // Let's assume leader is honest, but a subset of lieutenants is faulty.
    std::set<int> faulty_nodes = {3, 5};
    int leader_id = 1; // leader is honest
    int proposed_value = 0;
    // Honest leader sends 0.
    // Honest lieutenants forward 0.
    // Faulty lieutenants flip, sending 1.
    // For each lieutenant, the set they receive is:
    // - Leader's value: 0.
    // - From each of the other lieutenants:
    //   There are 5 other lieutenants, among which two (3 and 5) send 1, and three send 0.
    // So each lieutenant's vote count becomes: one 0 from leader + (from lieutenants: three 0's and two 1's) = 4 zeros, 2 ones.
    // Thus, majority vote is 0.
    // Expected outcome: All lieutenants decide 0, so the count of 1's is 0.
    int result = simulate_byzantine_agreement(num_nodes, faulty_nodes, leader_id, proposed_value);
    REQUIRE(result == 0);
}