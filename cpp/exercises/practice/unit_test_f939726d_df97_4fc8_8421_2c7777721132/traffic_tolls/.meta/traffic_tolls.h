#ifndef TRAFFIC_TOLLS_H
#define TRAFFIC_TOLLS_H

#include <vector>

struct Edge {
    int source;
    int destination;
    int base_travel_time;
    int capacity;
    int initial_vehicles;
};

std::vector<double> optimizeTolls(const std::vector<Edge>& edges, double tollSensitivity, double budget, int source, int destination);

#endif