#pragma once

#include <vector>
#include <queue>
#include <limits>
#include <unordered_map>

struct Road {
    int to;
    double length;
    double congestion;
    
    Road(int _to, double _length, double _congestion) 
        : to(_to), length(_length), congestion(_congestion) {}
};

class Graph {
public:
    explicit Graph(int numNodes);
    void addRoad(int from, int to, double length, double congestion);
    void updateCongestion(int from, int to, double newCongestion);
    const std::vector<std::vector<Road>>& getRoads() const;

private:
    std::vector<std::vector<Road>> adjacencyList;
};

struct DeliveryRequest {
    int start;
    int destination;
    double deadline;
    
    DeliveryRequest(int _start, int _dest, double _deadline)
        : start(_start), destination(_dest), deadline(_deadline) {}
};

struct RouteResult {
    bool success;
    std::vector<int> route;
    double totalCost;
    double totalTime;
    
    RouteResult() : success(false), totalCost(0), totalTime(0) {}
};

class RoutePlanner {
public:
    RoutePlanner(const Graph& graph, double alpha, double beta);
    RouteResult planRoute(const DeliveryRequest& request);

private:
    const Graph& graph;
    double alpha;
    double beta;
    
    struct Node {
        int id;
        double cost;
        
        Node(int _id, double _cost) : id(_id), cost(_cost) {}
        
        bool operator>(const Node& other) const {
            return cost > other.cost;
        }
    };
    
    RouteResult findOptimalRoute(int start, int dest, double deadline);
};

class RouteWrapper {
public:
    RouteWrapper(const Graph& g, double alpha, double beta)
        : planner(g, alpha, beta) {}
        
    RouteResult planRoute(const DeliveryRequest& request) {
        return planner.planRoute(request);
    }
    
private:
    RoutePlanner planner;
};