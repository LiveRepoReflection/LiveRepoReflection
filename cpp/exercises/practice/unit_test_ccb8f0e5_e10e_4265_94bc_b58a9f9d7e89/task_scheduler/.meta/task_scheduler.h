#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

namespace task_scheduler {

int schedule_tasks(int N, const std::vector<int>& id, const std::vector<int>& duration, const std::vector<int>& deadline, const std::vector<std::vector<int>>& dependencies);

}

#endif // TASK_SCHEDULER_H