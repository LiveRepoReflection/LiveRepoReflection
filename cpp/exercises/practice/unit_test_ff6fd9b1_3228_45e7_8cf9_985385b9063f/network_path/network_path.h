#pragma once

#include <vector>
#include <tuple>

std::vector<int> find_optimal_path(
    int n,
    const std::vector<std::tuple<int, int, int, int>>& connections,
    int start_node,
    int end_node,
    int required_bandwidth
);