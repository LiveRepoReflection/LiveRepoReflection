#include "network_routing.h"
#include <algorithm>
#include <stdexcept>

NetworkRouting::NetworkRouting(int N, const std::vector<int>& capacities) {
    if (capacities.size() != static_cast<size_t>(N)) {
        throw std::invalid_argument("Capacity size must match number of nodes");
    }
    for (int i = 0; i < N; ++i) {
        nodes.emplace_back(capacities[i]);
    }
}

void NetworkRouting::addEdge(int u, int v, int w, int t) {
    if (u < 0 || u >= static_cast<int>(nodes.size()) || v < 0 || v >= static_cast<int>(nodes.size())) {
        throw std::out_of_range("Node index out of range");
    }

    // Check if edge already exists at this time
    auto& edges_u = edge_timestamps[u][v];
    auto& edges_v = edge_timestamps[v][u];
    
    auto it_u = edges_u.lower_bound({t, 0});
    if (it_u != edges_u.end() && it_u->first == t) {
        // Update existing edge
        for (auto& edge : nodes[u].edges) {
            if (edge.to == v && edge.start_time == t) {
                edge.weight = w;
                break;
            }
        }
        for (auto& edge : nodes[v].edges) {
            if (edge.to == u && edge.start_time == t) {
                edge.weight = w;
                break;
            }
        }
        return;
    }

    // Add new edge with infinite end time (until removed)
    nodes[u].edges.emplace_back(v, w, t, std::numeric_limits<int>::max());
    nodes[v].edges.emplace_back(u, w, t, std::numeric_limits<int>::max());
    edges_u.insert({t, std::numeric_limits<int>::max()});
    edges_v.insert({t, std::numeric_limits<int>::max()});
}

void NetworkRouting::removeEdge(int u, int v, int t) {
    if (u < 0 || u >= static_cast<int>(nodes.size()) || v < 0 || v >= static_cast<int>(nodes.size())) {
        throw std::out_of_range("Node index out of range");
    }

    auto& edges_u = edge_timestamps[u][v];
    auto& edges_v = edge_timestamps[v][u];

    auto it_u = edges_u.lower_bound({t, 0});
    if (it_u != edges_u.begin()) {
        --it_u;
        if (it_u->second > t) {
            // Update end time in timestamp map
            int start_time = it_u->first;
            edges_u.erase(it_u);
            edges_u.insert({start_time, t});
            
            edges_v.erase({start_time, std::numeric_limits<int>::max()});
            edges_v.insert({start_time, t});

            // Update end time in edge list
            for (auto& edge : nodes[u].edges) {
                if (edge.to == v && edge.start_time == start_time) {
                    edge.end_time = t;
                    break;
                }
            }
            for (auto& edge : nodes[v].edges) {
                if (edge.to == u && edge.start_time == start_time) {
                    edge.end_time = t;
                    break;
                }
            }
        }
    }
}

bool NetworkRouting::isEdgeActive(int u, int v, int t) const {
    const auto& edges = edge_timestamps.at(u).at(v);
    auto it = edges.lower_bound({t, 0});
    if (it != edges.begin()) {
        --it;
        return t >= it->first && t <= it->second;
    }
    return false;
}

void NetworkRouting::updateNodeUsage(const std::vector<int>& path, bool increment) {
    for (int node : path) {
        if (increment) {
            nodes[node].used++;
        } else {
            nodes[node].used--;
        }
    }
}

std::vector<int> NetworkRouting::route(int src, int dest, int t) {
    if (src < 0 || src >= static_cast<int>(nodes.size()) || dest < 0 || dest >= static_cast<int>(nodes.size())) {
        throw std::out_of_range("Node index out of range");
    }

    std::vector<int> dist(nodes.size(), std::numeric_limits<int>::max());
    std::vector<std::vector<int>> paths(nodes.size());
    std::priority_queue<PathNode, std::vector<PathNode>, std::greater<>> pq;

    dist[src] = 0;
    paths[src] = {src};
    pq.emplace(src, 0, paths[src]);

    while (!pq.empty()) {
        PathNode current = pq.top();
        pq.pop();

        if (current.id == dest) {
            // Check if all nodes in path have capacity
            bool has_capacity = true;
            for (int node : current.path) {
                if (nodes[node].used >= nodes[node].capacity) {
                    has_capacity = false;
                    break;
                }
            }

            if (has_capacity) {
                updateNodeUsage(current.path, true);
                return current.path;
            } else {
                continue;
            }
        }

        if (current.dist > dist[current.id]) {
            continue;
        }

        for (const auto& edge : nodes[current.id].edges) {
            if (t >= edge.start_time && t <= edge.end_time) {
                int new_dist = current.dist + edge.weight;
                if (new_dist < dist[edge.to]) {
                    dist[edge.to] = new_dist;
                    std::vector<int> new_path = current.path;
                    new_path.push_back(edge.to);
                    paths[edge.to] = new_path;
                    pq.emplace(edge.to, new_dist, new_path);
                }
            }
        }
    }

    return {};
}