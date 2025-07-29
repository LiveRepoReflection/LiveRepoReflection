#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>
#include <tuple>

namespace task_scheduler {

// Function to determine optimal schedule for tasks
// Input: Vector of tasks, each represented as a tuple (id, duration, deadline, dependencies)
// Output: Vector of task IDs in the order they should be executed
std::vector<int> schedule_tasks(const std::vector<std::tuple<int, int, int, std::vector<int>>>& tasks);

} // namespace task_scheduler

#endif // TASK_SCHEDULER_H