#include "task_scheduler.h"
#include <queue>
#include <vector>
#include <algorithm>

struct RunningTask {
    int finish_time;
    int task_id;
    // For resource freeing, we store the resource requirements as is.
    std::vector<std::pair<int,int>> resource_requirements;
};

struct RunningTaskComparator {
    bool operator()(const RunningTask& a, const RunningTask& b) const {
        return a.finish_time > b.finish_time; // min-heap: the smallest finish_time has highest priority.
    }
};

int scheduleTasks(const std::vector<Task>& tasks, const std::vector<Resource>& resources) {
    int n = tasks.size();
    if(n == 0) return 0;

    // Build dependency graph and compute in-degree.
    std::vector<int> inDegree(n, 0);
    std::vector<std::vector<int>> dependents(n);
    for (int i = 0; i < n; ++i) {
        for (int dep : tasks[i].dependencies) {
            // task i depends on dep, so dep is prerequisite of i.
            dependents[dep].push_back(i);
            inDegree[i]++;
        }
    }

    // Ready task list: tasks with no remaining dependencies.
    std::vector<int> ready;
    for (int i = 0; i < n; ++i) {
        if (inDegree[i] == 0) {
            ready.push_back(i);
        }
    }
    // Sort ready tasks by id to ensure deterministic ordering.
    std::sort(ready.begin(), ready.end());

    // Available resources.
    std::vector<int> available;
    available.reserve(resources.size());
    for (const auto& res : resources) {
        available.push_back(res.capacity);
    }

    // Priority queue for running tasks.
    std::priority_queue<RunningTask, std::vector<RunningTask>, RunningTaskComparator> runningTasks;

    int current_time = 0;
    int finishedCount = 0;
    // To keep track if a task has been scheduled.
    std::vector<bool> scheduled(n, false);

    while (finishedCount < n) {
        bool scheduledSomething = false;
        std::vector<int> remainingReady;
        // Try to schedule tasks in ready if resources are available.
        // We process in order of increasing task id.
        for (int taskId : ready) {
            const Task& task = tasks[taskId];
            bool canSchedule = true;
            for (auto& req : task.resource_requirements) {
                int resId = req.first;
                int qty = req.second;
                if (resId >= static_cast<int>(available.size()) || available[resId] < qty) {
                    canSchedule = false;
                    break;
                }
            }
            if (canSchedule) {
                // Allocate resources.
                for (auto& req : task.resource_requirements) {
                    int resId = req.first;
                    int qty = req.second;
                    available[resId] -= qty;
                }
                // Schedule the task.
                RunningTask rt;
                rt.task_id = taskId;
                rt.finish_time = current_time + task.duration;
                rt.resource_requirements = task.resource_requirements;
                runningTasks.push(rt);
                scheduled[taskId] = true;
                scheduledSomething = true;
            } else {
                // Keep task in ready list if not scheduled.
                remainingReady.push_back(taskId);
            }
        }
        // Replace ready list with those not scheduled.
        ready = remainingReady;
        // Sort ready list to maintain ordering.
        std::sort(ready.begin(), ready.end());

        // If no tasks were scheduled now, then we need to advance time.
        if (!scheduledSomething) {
            // If there are running tasks, advance time to the earliest finish.
            if (!runningTasks.empty()) {
                RunningTask finishedTask = runningTasks.top();
                runningTasks.pop();
                // Advance current time to finish time.
                current_time = finishedTask.finish_time;
                finishedCount++;

                // Free resources allocated to this task.
                for (auto& req : finishedTask.resource_requirements) {
                    int resId = req.first;
                    int qty = req.second;
                    available[resId] += qty;
                }
                // Update dependents.
                for (int dependent : dependents[finishedTask.task_id]) {
                    inDegree[dependent]--;
                    if (inDegree[dependent] == 0 && !scheduled[dependent]) {
                        ready.push_back(dependent);
                    }
                }
                // Ensure deterministic order in ready list.
                std::sort(ready.begin(), ready.end());
            }
        }
        // Also, if there are still running tasks but available ready tasks are unschedulable, we should process next finish event.
        if (scheduledSomething == false && ready.empty() && !runningTasks.empty()) {
            RunningTask finishedTask = runningTasks.top();
            runningTasks.pop();
            current_time = finishedTask.finish_time;
            finishedCount++;
            for (auto& req : finishedTask.resource_requirements) {
                int resId = req.first;
                int qty = req.second;
                available[resId] += qty;
            }
            for (int dependent : dependents[finishedTask.task_id]) {
                inDegree[dependent]--;
                if (inDegree[dependent] == 0 && !scheduled[dependent]) {
                    ready.push_back(dependent);
                }
            }
            std::sort(ready.begin(), ready.end());
        }
        // If both ready and running tasks exist and you cannot schedule additional tasks due to resource constraints,
        // then process the next finish event.
        while (!ready.empty()) {
            bool anySchedulable = false;
            for (int taskId : ready) {
                const Task& task = tasks[taskId];
                bool canSched = true;
                for (auto& req : task.resource_requirements) {
                    int resId = req.first;
                    int qty = req.second;
                    if (available[resId] < qty) {
                        canSched = false;
                        break;
                    }
                }
                if (canSched) {
                    anySchedulable = true;
                    break;
                }
            }
            if (anySchedulable) break;
            if (!runningTasks.empty()) {
                RunningTask finishedTask = runningTasks.top();
                runningTasks.pop();
                current_time = finishedTask.finish_time;
                finishedCount++;
                for (auto& req : finishedTask.resource_requirements) {
                    int resId = req.first;
                    int qty = req.second;
                    available[resId] += qty;
                }
                for (int dependent : dependents[finishedTask.task_id]) {
                    inDegree[dependent]--;
                    if (inDegree[dependent] == 0 && !scheduled[dependent]) {
                        ready.push_back(dependent);
                    }
                }
                std::sort(ready.begin(), ready.end());
            } else {
                break;
            }
        }
    }

    // The last current_time corresponds to the finish time of the last completed task.
    return current_time;
}