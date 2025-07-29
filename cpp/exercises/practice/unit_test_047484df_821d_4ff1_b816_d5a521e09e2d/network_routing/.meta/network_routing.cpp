#include "network_routing.h"
#include <vector>
#include <queue>
#include <tuple>
#include <limits>
#include <cmath>

namespace network_routing {

struct Link {
    int u;
    int v;
    int capacity;
    int base_latency;
    int flow;
};

struct NodeState {
    int node;
    double dist;
    int hops;
    // Custom comparator for priority_queue: 
    // lower distance gets higher priority; if equal, fewer hops gets priority.
    bool operator>(const NodeState& other) const {
        if (std::abs(dist - other.dist) > 1e-9)
            return dist > other.dist;
        return hops > other.hops;
    }
};

std::vector<double> processRequests(
    int N,
    const std::vector<std::tuple<int, int, int, int>>& linksInput,
    const std::vector<std::tuple<int, int, int>>& requests
) {
    // Initialize links vector.
    std::vector<Link> links;
    links.reserve(linksInput.size());
    
    // Graph representation: for each node, store indices of links in the links vector.
    std::vector<std::vector<int>> graph(N);
    
    for (size_t i = 0; i < linksInput.size(); ++i) {
        int u, v, capacity, base_latency;
        std::tie(u, v, capacity, base_latency) = linksInput[i];
        Link link;
        link.u = u;
        link.v = v;
        link.capacity = capacity;
        link.base_latency = base_latency;
        link.flow = 0;
        links.push_back(link);
        // Since the links are bidirectional, add the index for both nodes.
        graph[u].push_back(i);
        graph[v].push_back(i);
    }
    
    std::vector<double> results;
    results.reserve(requests.size());
    
    const double INF = std::numeric_limits<double>::max();
    
    // Process each request in sequence.
    for (const auto& req : requests) {
        int src, dest, data;
        std::tie(src, dest, data) = req;
        
        // If source and destination are same, latency is 0.
        if (src == dest) {
            results.push_back(0.0);
            continue;
        }
        
        // Dijkstra initialization.
        std::vector<double> dist(N, INF);
        std::vector<int> hops(N, std::numeric_limits<int>::max());
        std::vector<int> parent(N, -1);
        std::vector<int> parentEdge(N, -1);
        
        std::priority_queue<NodeState, std::vector<NodeState>, std::greater<NodeState>> pq;
        
        dist[src] = 0.0;
        hops[src] = 0;
        pq.push({src, 0.0, 0});
        
        while (!pq.empty()) {
            NodeState cur = pq.top();
            pq.pop();
            
            if (cur.node == dest) {
                // Found the destination with possibly optimal cost
                break;
            }
            
            // If the popped state is outdated, continue.
            if (cur.dist > dist[cur.node] + 1e-9)
                continue;
            
            // Traverse adjacent edges.
            for (int edgeIdx : graph[cur.node]) {
                Link &edge = links[edgeIdx];
                // Determine neighbor.
                int neighbor = (cur.node == edge.u) ? edge.v : edge.u;
                // Check capacity constraint: available capacity must be >= data.
                if (edge.capacity - edge.flow < data)
                    continue;
                // Compute effective latency: using current congestion.
                double congestion = static_cast<double>(edge.flow) / edge.capacity;
                double effectiveLatency = edge.base_latency * (1.0 + congestion * congestion);
                double newDist = cur.dist + effectiveLatency;
                int newHops = cur.hops + 1;
                
                // Tie breaking: update if lower distance or equal distance with fewer hops.
                if (newDist < dist[neighbor] - 1e-9 || (std::abs(newDist - dist[neighbor]) < 1e-9 && newHops < hops[neighbor])) {
                    dist[neighbor] = newDist;
                    hops[neighbor] = newHops;
                    parent[neighbor] = cur.node;
                    parentEdge[neighbor] = edgeIdx;
                    pq.push({neighbor, newDist, newHops});
                }
            }
        }
        
        // If destination is unreachable, record -1.
        if (dist[dest] == INF) {
            results.push_back(-1.0);
            continue;
        }
        
        // Route data: update flow along the found path.
        int cur = dest;
        while (cur != src) {
            int edgeIdx = parentEdge[cur];
            if (edgeIdx != -1) {
                links[edgeIdx].flow += data;
            }
            cur = parent[cur];
        }
        
        // Append the computed latency.
        results.push_back(dist[dest]);
    }
    
    return results;
}

} // namespace network_routing