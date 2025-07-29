#ifndef TRAFFIC_FLOW_H
#define TRAFFIC_FLOW_H

#include <vector>

namespace traffic_flow {
    bool is_flow_possible(int N, int M, int K,
                         const std::vector<int>& C,
                         const std::vector<int>& U,
                         const std::vector<int>& V,
                         const std::vector<int>& L,
                         const std::vector<int>& R,
                         const std::vector<int>& S,
                         const std::vector<int>& D,
                         const std::vector<int>& T,
                         const std::vector<int>& A);
}

#endif