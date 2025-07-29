#pragma once
#include <vector>

namespace load_balancer {
    /**
     * Distributes incoming requests among backend servers
     * @param server_capacities A vector of server capacities, where server_capacities[i] represents 
     *                           the capacity of the i-th server
     * @param requests A vector of requests, where each element represents the priority of a request
     * @return A vector where result[i] is the number of requests assigned to the i-th server
     */
    std::vector<int> distribute_load(const std::vector<int>& server_capacities, 
                                     const std::vector<int>& requests);
}