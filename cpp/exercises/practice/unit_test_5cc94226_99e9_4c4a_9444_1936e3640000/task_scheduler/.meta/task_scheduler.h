#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

namespace task_scheduler {

int min_total_penalty(const std::vector<int>& duration,
                      const std::vector<int>& deadline,
                      const std::vector<std::vector<int>>& dependencies);

}  // namespace task_scheduler

#endif  // TASK_SCHEDULER_H