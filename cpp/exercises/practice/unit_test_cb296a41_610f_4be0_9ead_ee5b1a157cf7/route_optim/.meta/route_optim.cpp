#include "route_optim.h"
#include <unordered_map>
#include <vector>
#include <queue>
#include <limits>
#include <algorithm>

namespace route_optim {

struct Edge {
    int to;
    double cost;
    int time;
};

struct SecurityZone {
    int start;
    int end;
    double penMonetary;
    int penTime;
};

struct NodeData {
    double lat;
    double lon;
};

namespace {
    std::unordered_map<int, NodeData> nodes;
    std::unordered_map<int, std::vector<Edge>> graph;
    std::unordered_map<int, std::vector<SecurityZone>> securityZones;
}

void reset() {
    nodes.clear();
    graph.clear();
    securityZones.clear();
}

void addNode(int id, double lat, double lon) {
    nodes[id] = {lat, lon};
    if (graph.find(id) == graph.end()) {
        graph[id] = std::vector<Edge>();
    }
}

void addEdge(int from, int to, double cost, int time) {
    if (nodes.find(from) == nodes.end()) {
        nodes[from] = {0.0, 0.0};
        graph[from] = std::vector<Edge>();
    }
    if (nodes.find(to) == nodes.end()) {
        nodes[to] = {0.0, 0.0};
        graph[to] = std::vector<Edge>();
    }
    graph[from].push_back({to, cost, time});
}

void addSecurityZone(int node, int start, int end, double penMonetary, int penTime) {
    securityZones[node].push_back({start, end, penMonetary, penTime});
}

void updateSecurityZone(int node, int start, int end, double penMonetary, int penTime) {
    bool updated = false;
    if (securityZones.find(node) != securityZones.end()) {
        for (auto &sz : securityZones[node]) {
            if (sz.start == start && sz.end == end) {
                sz.penMonetary = penMonetary;
                sz.penTime = penTime;
                updated = true;
            }
        }
    }
    if (!updated) {
        securityZones[node].push_back({start, end, penMonetary, penTime});
    }
}

double getSecurityMonetary(int node, int currentTime) {
    double penalty = 0.0;
    if (securityZones.find(node) != securityZones.end()) {
        for (const auto &sz : securityZones[node]) {
            if (currentTime >= sz.start && currentTime <= sz.end) {
                penalty += sz.penMonetary;
            }
        }
    }
    return penalty;
}

int getSecurityTime(int node, int currentTime) {
    int penalty = 0;
    if (securityZones.find(node) != securityZones.end()) {
        for (const auto &sz : securityZones[node]) {
            if (currentTime >= sz.start && currentTime <= sz.end) {
                penalty += sz.penTime;
            }
        }
    }
    return penalty;
}

struct CheapestState {
    int node;
    double totalCost;
    int totalTime;
};

struct FastestState {
    int node;
    int totalTime;
    double totalCost;
};

struct CheapestCompare {
    bool operator()(const CheapestState &a, const CheapestState &b) const {
        return a.totalCost > b.totalCost;
    }
};

struct FastestCompare {
    bool operator()(const FastestState &a, const FastestState &b) const {
        return a.totalTime > b.totalTime;
    }
};

Route findCheapestRoute(int source, int dest, int currentTime) {
    Route route;
    if (source == dest) {
        route.path.push_back(source);
        route.totalMonetaryCost = 0.0;
        route.totalTimeCost = 0;
        return route;
    }

    std::unordered_map<int, double> bestCost;
    std::unordered_map<int, int> bestTime;
    std::unordered_map<int, int> prev;

    std::priority_queue<CheapestState, std::vector<CheapestState>, CheapestCompare> pq;
    pq.push({source, 0.0, 0});
    bestCost[source] = 0.0;
    bestTime[source] = 0;

    while (!pq.empty()) {
        CheapestState cur = pq.top();
        pq.pop();
        if (cur.node == dest) {
            break;
        }
        if (cur.totalCost > bestCost[cur.node]) continue;
        for (const auto &edge : graph[cur.node]) {
            double secPenalty = getSecurityMonetary(edge.to, currentTime);
            int secTimePenalty = getSecurityTime(edge.to, currentTime);
            double newCost = cur.totalCost + edge.cost + secPenalty;
            int newTime = cur.totalTime + edge.time + secTimePenalty;
            if (bestCost.find(edge.to) == bestCost.end() || newCost < bestCost[edge.to]) {
                bestCost[edge.to] = newCost;
                bestTime[edge.to] = newTime;
                prev[edge.to] = cur.node;
                pq.push({edge.to, newCost, newTime});
            }
        }
    }
    if (bestCost.find(dest) == bestCost.end()) {
        route.totalMonetaryCost = 0.0;
        route.totalTimeCost = 0;
        return route;
    }
    std::vector<int> path;
    int cur = dest;
    while (cur != source) {
        path.push_back(cur);
        cur = prev[cur];
    }
    path.push_back(source);
    std::reverse(path.begin(), path.end());

    route.path = path;
    route.totalMonetaryCost = bestCost[dest];
    route.totalTimeCost = bestTime[dest];
    return route;
}

Route findFastestRoute(int source, int dest, int currentTime) {
    Route route;
    if (source == dest) {
        route.path.push_back(source);
        route.totalMonetaryCost = 0.0;
        route.totalTimeCost = 0;
        return route;
    }

    std::unordered_map<int, int> bestTime;
    std::unordered_map<int, double> bestCost;
    std::unordered_map<int, int> prev;

    std::priority_queue<FastestState, std::vector<FastestState>, FastestCompare> pq;
    pq.push({source, 0, 0.0});
    bestTime[source] = 0;
    bestCost[source] = 0.0;

    while (!pq.empty()) {
        FastestState cur = pq.top();
        pq.pop();
        if (cur.node == dest) {
            break;
        }
        if (cur.totalTime > bestTime[cur.node]) continue;
        for (const auto &edge : graph[cur.node]) {
            double secPenalty = getSecurityMonetary(edge.to, currentTime);
            int secTimePenalty = getSecurityTime(edge.to, currentTime);
            int newTime = cur.totalTime + edge.time + secTimePenalty;
            double newCost = cur.totalCost + edge.cost + secPenalty;
            if (bestTime.find(edge.to) == bestTime.end() || newTime < bestTime[edge.to]) {
                bestTime[edge.to] = newTime;
                bestCost[edge.to] = newCost;
                prev[edge.to] = cur.node;
                pq.push({edge.to, newTime, newCost});
            }
        }
    }
    if (bestTime.find(dest) == bestTime.end()) {
        route.totalMonetaryCost = 0.0;
        route.totalTimeCost = 0;
        return route;
    }
    std::vector<int> path;
    int cur = dest;
    while (cur != source) {
        path.push_back(cur);
        cur = prev[cur];
    }
    path.push_back(source);
    std::reverse(path.begin(), path.end());

    route.path = path;
    route.totalMonetaryCost = bestCost[dest];
    route.totalTimeCost = bestTime[dest];
    return route;
}

}  // namespace route_optim