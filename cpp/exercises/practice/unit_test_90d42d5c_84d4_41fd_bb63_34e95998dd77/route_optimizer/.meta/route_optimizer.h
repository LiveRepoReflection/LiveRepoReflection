#ifndef ROUTE_OPTIMIZER_H
#define ROUTE_OPTIMIZER_H

#include <vector>
#include <tuple>

namespace route_optimizer {
    double calculate_optimal_routes(
        const std::vector<std::pair<int, int>>& edges,
        const std::vector<int>& travel_times,
        const std::vector<double>& toll_costs,
        const std::vector<double>& reliabilities,
        const std::vector<std::pair<int, double>>& trucks,
        const std::vector<std::tuple<int, int, int, int, int>>& deliveries,
        double late_penalty,
        double early_penalty,
        double failure_penalty,
        double reliability_threshold
    );
}

#endif // ROUTE_OPTIMIZER_H