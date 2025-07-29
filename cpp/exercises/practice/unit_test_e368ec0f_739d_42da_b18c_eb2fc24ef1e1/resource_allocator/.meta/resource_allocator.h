#pragma once

#include <vector>
#include <tuple>

std::vector<int> allocateJobs(
    const std::vector<std::vector<double>>& nodes,
    const std::vector<std::tuple<std::vector<double>, int, int>>& requests,
    int currentTime);