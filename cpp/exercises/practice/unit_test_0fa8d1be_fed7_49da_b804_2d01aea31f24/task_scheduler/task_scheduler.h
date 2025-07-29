#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

namespace task_scheduler {
    std::vector<int> schedule(int N,
                             const std::vector<int>& duration,
                             const std::vector<int>& resource_requirement,
                             const std::vector<std::vector<int>>& dependencies,
                             int resource_limit);
}

#endif // TASK_SCHEDULER_H