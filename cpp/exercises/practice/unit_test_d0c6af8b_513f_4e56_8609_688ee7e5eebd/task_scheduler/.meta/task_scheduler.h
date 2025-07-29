#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

namespace task_scheduler {

int minimum_makespan(int N, int M, const std::vector<int>& duration,
                     const std::vector<std::vector<int>>& dependencies,
                     const std::vector<std::vector<int>>& resource_requirements,
                     const std::vector<int>& resource_capacities);

}  // namespace task_scheduler

#endif  // TASK_SCHEDULER_H