#include "social_influence.h"
#include <vector>
#include <queue>
#include <stdexcept>
#include <algorithm>
#include <random>
#include <limits>

namespace social_influence {

std::vector<int> find_top_influencers(int N, 
                                      const std::vector<std::pair<int, int>>& edges, 
                                      const std::vector<int>& activity_scores, 
                                      int K, 
                                      int max_steps) {
    if (activity_scores.size() != static_cast<size_t>(N)) {
        throw std::invalid_argument("Size of activity scores must be equal to N.");
    }
    if (K > N || K <= 0) {
        throw std::invalid_argument("K must be between 1 and N.");
    }
    if (max_steps <= 0) {
        throw std::invalid_argument("max_steps must be at least 1.");
    }
    
    // Build undirected graph
    std::vector<std::vector<int>> graph(N);
    for (const auto& edge : edges) {
        int u = edge.first;
        int v = edge.second;
        if(u < 0 || u >= N || v < 0 || v >= N) continue;
        graph[u].push_back(v);
        graph[v].push_back(u);
    }
    
    // Calculate max_activity from activity_scores
    int max_activity = std::numeric_limits<int>::min();
    for (int score : activity_scores) {
        if (score > max_activity) {
            max_activity = score;
        }
    }
    if (max_activity <= 0) {
        throw std::invalid_argument("Activity scores must be positive.");
    }
    
    // Function to compute Weighted Cascade Reach (WCR) for a given starting node
    auto compute_wcr = [&](int start) -> double {
        double wcr = static_cast<double>(activity_scores[start]); // step 1 contribution (t=1)
        std::vector<bool> infected(N, false);
        infected[start] = true;
        std::queue<std::pair<int, int>> q; // pair: (node, time step)
        q.push({start, 1});
        
        // Use a local random generator seeded deterministically per starting node.
        std::mt19937 rng(42 + start);
        std::uniform_real_distribution<double> dist(0.0, 1.0);
        
        while (!q.empty()) {
            auto [curr, t] = q.front();
            q.pop();
            if (t >= max_steps) {
                continue; // Do not propagate further if reached max steps.
            }
            int next_step = t + 1;
            for (int neighbor : graph[curr]) {
                if (!infected[neighbor]) {
                    double prob = (static_cast<double>(activity_scores[curr]) + activity_scores[neighbor]) / (2.0 * max_activity);
                    double r = dist(rng);
                    if (r < prob) {
                        infected[neighbor] = true;
                        wcr += static_cast<double>(activity_scores[neighbor]) / next_step;
                        q.push({neighbor, next_step});
                    }
                }
            }
        }
        return wcr;
    };
    
    // Compute WCR for each node.
    std::vector<std::pair<double, int>> influencer_scores;
    influencer_scores.reserve(N);
    for (int i = 0; i < N; ++i) {
        double score = compute_wcr(i);
        influencer_scores.push_back({score, i});
    }
    
    // Sort: descending order by score, tie-break using ascending order of node id.
    std::sort(influencer_scores.begin(), influencer_scores.end(), [&](const auto& a, const auto& b) {
        if (a.first == b.first) {
            return a.second < b.second;
        }
        return a.first > b.first;
    });
    
    // Prepare result vector with top K influencer ids.
    std::vector<int> result;
    result.reserve(K);
    for (int i = 0; i < K; ++i) {
        result.push_back(influencer_scores[i].second);
    }
    return result;
}

}  // namespace social_influence