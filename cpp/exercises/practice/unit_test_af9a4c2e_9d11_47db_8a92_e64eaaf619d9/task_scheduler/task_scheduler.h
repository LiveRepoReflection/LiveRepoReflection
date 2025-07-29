#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

namespace task_scheduler {

struct Task {
    int id;
    int duration;
    int resource;
    std::vector<int> dependencies;
};

int schedule_tasks(int N, int R, const std::vector<Task>& tasks);

}  // namespace task_scheduler

#endif // TASK_SCHEDULER_H