#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>
#include <tuple>
#include <utility>

std::pair<int, int> schedule_tasks(int N, int K, const std::vector<std::tuple<int, int, int, std::vector<int>>>& tasks);

#endif // TASK_SCHEDULER_H