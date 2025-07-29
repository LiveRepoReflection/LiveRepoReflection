#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <vector>
#include <tuple>

namespace distributed_tx {

double expected_transaction_cost(int N,
                                 const std::vector<std::tuple<int, int, int>>& edges,
                                 const std::vector<double>& failure_probability,
                                 const std::vector<int>& prep_cost,
                                 const std::vector<int>& commit_cost);

}

#endif