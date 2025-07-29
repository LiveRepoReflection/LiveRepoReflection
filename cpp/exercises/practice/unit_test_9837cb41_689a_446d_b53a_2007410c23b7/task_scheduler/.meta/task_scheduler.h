#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>
using namespace std;

namespace task_scheduler {

struct Task {
    int id;
    int execution_time;
    int deadline;
    int priority;
    std::vector<int> dependencies;
};

/// scheduleTasks receives the total number of tasks n, the number of machines k,
/// and the list of tasks. It returns the minimum total weighted tardiness if scheduling is possible,
/// or -1 if there is a task with no dependencies that cannot possibly finish (i.e. unschedulable).
int scheduleTasks(int n, int k, const std::vector<Task>& tasks);

} // namespace task_scheduler

#endif  // TASK_SCHEDULER_H