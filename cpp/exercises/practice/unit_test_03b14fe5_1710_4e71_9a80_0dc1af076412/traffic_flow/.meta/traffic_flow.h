#ifndef TRAFFIC_FLOW_H
#define TRAFFIC_FLOW_H

#include <vector>
#include <tuple>

namespace traffic_flow {

// Given a directed graph with n nodes (numbered 0 to n-1) represented as edges,
// where each edge is a tuple (u, v, c) with capacity c, along with a source, a destination,
// an integer k (the capacity cost multiplier for trucks), and available numbers of
// cars and trucks (numCars and numTrucks), this function returns the maximum total number 
// of vehicles (cars + trucks) that can be routed from source to destination such that 
// on every edge the cumulative capacity used (1 unit per car and k units per truck) does not exceed
// the street's capacity.
int maxVehicles(int n, int source, int destination, int k, int numCars, int numTrucks,
                const std::vector<std::tuple<int, int, int>>& edges);

}  // namespace traffic_flow

#endif