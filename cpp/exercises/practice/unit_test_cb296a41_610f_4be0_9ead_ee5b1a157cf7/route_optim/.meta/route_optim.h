#ifndef ROUTE_OPTIM_H
#define ROUTE_OPTIM_H

#include <vector>

namespace route_optim {

struct Route {
    std::vector<int> path;
    double totalMonetaryCost;
    int totalTimeCost;
};

void reset();
void addNode(int id, double lat, double lon);
void addEdge(int from, int to, double cost, int time);
void addSecurityZone(int node, int start, int end, double penMonetary, int penTime);
void updateSecurityZone(int node, int start, int end, double penMonetary, int penTime);
Route findCheapestRoute(int source, int dest, int currentTime);
Route findFastestRoute(int source, int dest, int currentTime);

}  // namespace route_optim

#endif  // ROUTE_OPTIM_H