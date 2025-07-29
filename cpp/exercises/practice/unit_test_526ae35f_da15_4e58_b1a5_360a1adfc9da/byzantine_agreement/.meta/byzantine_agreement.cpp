#include "byzantine_agreement.h"
#include <vector>

namespace byzantine_agreement {

static inline int flip(int v) {
    return v == 0 ? 1 : 0;
}

int simulate_byzantine_agreement(int num_nodes, const std::set<int>& faulty_nodes, int leader_id, int proposed_value) {
    // If there are no lieutenants, return 0.
    if (num_nodes <= 1)
        return 0;
    
    // Determine the leader's transmitted message.
    int leader_message = (faulty_nodes.count(leader_id) > 0) ? flip(proposed_value) : proposed_value;
    
    // Each lieutenant receives the message from the leader.
    // In the relay phase, each lieutenant sends a message to all other lieutenants.
    // If a lieutenant is faulty, it flips the message it received.
    // We'll store the relay messages for all nodes (only computed for lieutenants).
    std::vector<int> relay(num_nodes, -1);
    for (int i = 0; i < num_nodes; i++) {
        if (i == leader_id)
            continue; // Leader does not relay in the lieutenant phase.
        relay[i] = (faulty_nodes.count(i) > 0) ? flip(leader_message) : leader_message;
    }
    
    // Now, each lieutenant collects a vote from:
    //  - The direct leader message.
    //  - The relay messages from every lieutenant (including itself).
    // They decide on 1 if the count of ones is strictly greater than zeros (if tie, decide 0).
    int count_decide_one = 0;
    for (int i = 0; i < num_nodes; i++) {
        if (i == leader_id)
            continue; // Only lieutenants decide.
        
        int count_one = 0;
        int count_zero = 0;
        
        // Vote from leader's direct message.
        if (leader_message == 1)
            count_one++;
        else
            count_zero++;
        
        // Votes from relay messages from each lieutenant.
        for (int j = 0; j < num_nodes; j++) {
            if (j == leader_id)
                continue;
            if (relay[j] == 1)
                count_one++;
            else
                count_zero++;
        }
        
        // Decide based on majority vote.
        if (count_one > count_zero)
            count_decide_one++;
    }
    
    return count_decide_one;
}

}  // namespace byzantine_agreement