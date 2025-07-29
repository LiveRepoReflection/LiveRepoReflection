#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>
#include <utility>

struct Task {
    int duration;
    std::vector<std::pair<int,int>> resource_requirements;
    std::vector<int> dependencies;
};

struct Resource {
    int capacity;
};

int scheduleTasks(const std::vector<Task>& tasks, const std::vector<Resource>& resources);

#endif // TASK_SCHEDULER_H