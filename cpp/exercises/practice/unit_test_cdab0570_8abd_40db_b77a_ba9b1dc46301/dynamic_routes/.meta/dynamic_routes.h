#ifndef DYNAMIC_ROUTES_H
#define DYNAMIC_ROUTES_H

#include <vector>
#include <tuple>

class DynamicRoutes {
public:
    DynamicRoutes(int n, 
                  const std::vector<std::tuple<int, int, int>>& roads,
                  const std::vector<std::tuple<int, int, int, int>>& construction);
    
    int findOptimalRoute(int start, int destination, int deadline);

private:
    struct Edge {
        int to;
        int weight;
        std::vector<std::pair<int, int>> blocked_times;
    };

    int n_;
    std::vector<std::vector<Edge>> graph_;
    
    int findEarliestArrival(int start, int destination, int start_time);
    bool isBlocked(const Edge& edge, int time);
    int getNextAvailableTime(const Edge& edge, int current_time);
};

#endif