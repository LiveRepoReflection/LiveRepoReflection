#ifndef ROUTE_OPTIMIZER_H
#define ROUTE_OPTIMIZER_H

#include <string>
#include <vector>
#include <tuple>

namespace route_optimizer {
    double find_minimum_time(
        const std::vector<int>& locations,
        const std::vector<std::tuple<int, int, std::string, double, double>>& edges,
        const std::vector<std::tuple<int, std::string, std::string, double>>& transfers,
        int start,
        int destination
    );
}

#endif