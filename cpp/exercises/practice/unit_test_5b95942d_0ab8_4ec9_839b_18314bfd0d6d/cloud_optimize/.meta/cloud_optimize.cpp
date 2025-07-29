#include "cloud_optimize.h"
#include <vector>
#include <tuple>
#include <queue>
#include <algorithm>
#include <unordered_set>
#include <limits>
#include <unordered_map>

using namespace std;

namespace cloud_optimize {

    // Structure to represent state in the search space
    struct State {
        int node;               // Current data center
        int remaining_upgrades; // Remaining upgrades available
        int cost;               // Current accumulated cost
        vector<bool> upgraded;  // Which edges have been upgraded and how many times
        
        State(int n, int r, int c, vector<bool> u) : 
            node(n), remaining_upgrades(r), cost(c), upgraded(move(u)) {}
        
        // Operator for priority queue comparison
        bool operator>(const State& other) const {
            return cost > other.cost;
        }
    };

    // Structure to represent an edge with unique ID
    struct Edge {
        int from;
        int to;
        int weight;
        int id;  // Unique identifier for the edge
        
        Edge(int f, int t, int w, int i) : from(f), to(t), weight(w), id(i) {}
    };

    int min_latency(int num_data_centers, 
                   const vector<tuple<int, int, int>>& edges, 
                   int source_data_center, 
                   int destination_data_center, 
                   int max_upgrades, 
                   int upgrade_reduction, 
                   const vector<int>& critical_vms, 
                   const vector<int>& vm_data_center) {
        
        // Handle the case when source and destination are the same
        if (source_data_center == destination_data_center) {
            return 0;
        }
        
        // Create a set to quickly check if a data center hosts critical VMs
        unordered_set<int> critical_data_centers;
        for (int vm : critical_vms) {
            critical_data_centers.insert(vm_data_center[vm]);
        }
        
        // Build adjacency list representation of the graph
        vector<vector<Edge>> graph(num_data_centers);
        int edge_count = edges.size();
        
        for (int i = 0; i < edge_count; i++) {
            int u = get<0>(edges[i]);
            int v = get<1>(edges[i]);
            int w = get<2>(edges[i]);
            
            graph[u].emplace_back(u, v, w, i);
            graph[v].emplace_back(v, u, w, i); // undirected graph
        }
        
        // Create a map for memoization to avoid redundant computations
        // Key: (node, remaining_upgrades, edge_state)
        // Value: minimum cost to reach destination from this state
        unordered_map<string, int> memo;
        
        // Use Dijkstra's algorithm with a priority queue
        priority_queue<State, vector<State>, greater<State>> pq;
        vector<bool> initial_upgraded(edge_count, false);
        pq.push(State(source_data_center, max_upgrades, 0, initial_upgraded));
        
        // Keep track of the best cost for each state (node, remaining_upgrades, upgraded)
        unordered_map<string, int> best_cost;
        
        while (!pq.empty()) {
            State current = pq.top();
            pq.pop();
            
            // Generate a key for the current state
            string state_key = to_string(current.node) + "," + to_string(current.remaining_upgrades) + ",";
            for (int i = 0; i < edge_count; i++) {
                state_key += current.upgraded[i] ? "1" : "0";
            }
            
            // Check if we've seen this state with a better cost
            if (best_cost.find(state_key) != best_cost.end() && best_cost[state_key] <= current.cost) {
                continue;
            }
            
            // Update best cost for this state
            best_cost[state_key] = current.cost;
            
            // If we've reached the destination, return the cost
            if (current.node == destination_data_center) {
                return current.cost;
            }
            
            // Explore all neighbors
            for (const Edge& edge : graph[current.node]) {
                int next_node = edge.to;
                int weight = edge.weight;
                int edge_id = edge.id;
                
                // Calculate additional cost if next_node hosts critical VMs
                int additional_cost = 0;
                if (critical_data_centers.find(next_node) != critical_data_centers.end()) {
                    additional_cost = 10 * upgrade_reduction;
                }
                
                // Try all possible upgrade combinations for this edge (0 to remaining_upgrades)
                for (int upgrades = 0; upgrades <= current.remaining_upgrades; upgrades++) {
                    // Calculate the new weight after upgrades
                    int new_weight = max(0, weight - upgrades * upgrade_reduction);
                    
                    // Create a copy of the upgraded edges array and update it
                    vector<bool> new_upgraded = current.upgraded;
                    if (upgrades > 0) {
                        new_upgraded[edge_id] = true;
                    }
                    
                    // Calculate the new cost
                    int new_cost = current.cost + new_weight + additional_cost;
                    
                    // Add the new state to the priority queue
                    pq.push(State(next_node, current.remaining_upgrades - upgrades, new_cost, new_upgraded));
                }
            }
        }
        
        // If there's no path, return a large value
        return numeric_limits<int>::max();
    }
}