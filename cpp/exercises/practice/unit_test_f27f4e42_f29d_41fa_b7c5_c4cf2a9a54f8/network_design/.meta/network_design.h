#ifndef NETWORK_DESIGN_H
#define NETWORK_DESIGN_H

#include <vector>
#include <tuple>

int solve_network_design(int N, int M, const std::vector<int>& C,
                        const std::vector<std::tuple<int, int, int>>& connections,
                        int T);

#endif