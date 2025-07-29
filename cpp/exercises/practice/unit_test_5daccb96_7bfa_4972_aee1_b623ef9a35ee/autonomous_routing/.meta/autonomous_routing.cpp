#include "autonomous_routing.h"
#include <algorithm>

Graph::Graph(int numNodes) : adjacencyList(numNodes) {}

void Graph::addRoad(int from, int to, double length, double congestion) {
    adjacencyList[from].emplace_back(to, length, congestion);
}

void Graph::updateCongestion(int from, int to, double newCongestion) {
    for (auto& road : adjacencyList[from]) {
        if (road.to == to) {
            road.congestion = newCongestion;
            break;
        }
    }
}

const std::vector<std::vector<Road>>& Graph::getRoads() const {
    return adjacencyList;
}

RoutePlanner::RoutePlanner(const Graph& g, double a, double b)
    : graph(g), alpha(a), beta(b) {}

RouteResult RoutePlanner::planRoute(const DeliveryRequest& request) {
    return findOptimalRoute(request.start, request.destination, request.deadline);
}

RouteResult RoutePlanner::findOptimalRoute(int start, int dest, double deadline) {
    const auto& roads = graph.getRoads();
    int n = roads.size();
    
    std::vector<double> costs(n, std::numeric_limits<double>::infinity());
    std::vector<double> times(n, std::numeric_limits<double>::infinity());
    std::vector<int> previous(n, -1);
    
    std::priority_queue<Node, std::vector<Node>, std::greater<Node>> pq;
    
    costs[start] = 0;
    times[start] = 0;
    pq.emplace(start, 0);
    
    while (!pq.empty()) {
        Node current = pq.top();
        pq.pop();
        
        int currentId = current.id;
        
        if (currentId == dest) {
            break;
        }
        
        if (current.cost > costs[currentId]) {
            continue;
        }
        
        for (const auto& road : roads[currentId]) {
            double newTime = times[currentId] + road.length;
            double newCost = costs[currentId] + 
                           alpha * road.length + 
                           beta * road.congestion;
            
            if (newCost < costs[road.to] && newTime <= deadline) {
                costs[road.to] = newCost;
                times[road.to] = newTime;
                previous[road.to] = currentId;
                pq.emplace(road.to, newCost);
            }
        }
    }
    
    RouteResult result;
    if (costs[dest] == std::numeric_limits<double>::infinity()) {
        return result;
    }
    
    // Reconstruct the path
    result.success = true;
    result.totalCost = costs[dest];
    result.totalTime = times[dest];
    
    int current = dest;
    while (current != -1) {
        result.route.push_back(current);
        current = previous[current];
    }
    std::reverse(result.route.begin(), result.route.end());
    
    return result;
}