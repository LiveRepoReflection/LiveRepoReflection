#ifndef CLOUD_OPTIMIZE_H
#define CLOUD_OPTIMIZE_H

#include <vector>
#include <tuple>

namespace cloud_optimize {
    int min_latency(int num_data_centers, 
                    const std::vector<std::tuple<int, int, int>>& edges, 
                    int source_data_center, 
                    int destination_data_center, 
                    int max_upgrades, 
                    int upgrade_reduction, 
                    const std::vector<int>& critical_vms, 
                    const std::vector<int>& vm_data_center);
}

#endif // CLOUD_OPTIMIZE_H