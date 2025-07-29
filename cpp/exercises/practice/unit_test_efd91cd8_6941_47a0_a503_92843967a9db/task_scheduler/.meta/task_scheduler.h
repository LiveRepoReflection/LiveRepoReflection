#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

namespace task_scheduler {
    int get_max_completed_tasks(int n, 
                              const std::vector<int>& id, 
                              const std::vector<int>& duration, 
                              const std::vector<int>& deadline, 
                              const std::vector<std::vector<int>>& dependencies);
}

#endif