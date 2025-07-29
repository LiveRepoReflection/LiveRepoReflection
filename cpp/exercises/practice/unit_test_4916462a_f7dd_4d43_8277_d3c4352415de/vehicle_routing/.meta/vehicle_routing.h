#ifndef VEHICLE_ROUTING_H
#define VEHICLE_ROUTING_H

#include <string>
#include <vector>

namespace vehicle_routing {

int solve(int N, int F, int K, int M, const std::vector<std::vector<std::string>>& configurations);

}  // namespace vehicle_routing

#endif