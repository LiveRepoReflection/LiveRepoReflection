#ifndef BOTTLENECK_PATHS_H
#define BOTTLENECK_PATHS_H

#include <vector>
#include <tuple>
using std::vector;
using std::tuple;

namespace bottleneck_paths {

struct Result {
    int destination;
    int max_bottleneck_capacity;
    std::vector<int> sources;
};

vector<Result> compute_bottleneck_paths(int N, const vector<tuple<int, int, int>>& edges, const vector<int>& sources);

}  // namespace bottleneck_paths

#endif  // BOTTLENECK_PATHS_H