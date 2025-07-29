#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>

struct Task {
    int id;
    int execution_time;
    int deadline;
    std::vector<int> dependencies;
};

int schedule_tasks(int n, int k, const std::vector<Task>& tasks);

#endif // TASK_SCHEDULER_H