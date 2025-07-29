#include "task_scheduler.h"
#include <algorithm>

bool TaskScheduler::hasCircularDependency(
    const std::string& task_id,
    const std::unordered_map<std::string, Task>& task_map,
    std::unordered_set<std::string>& visited,
    std::unordered_set<std::string>& recursion_stack) {
    
    if (visited.find(task_id) == visited.end()) {
        visited.insert(task_id);
        recursion_stack.insert(task_id);
        
        const auto& task = task_map.at(task_id);
        for (const auto& dep : task.dependencies) {
            if (visited.find(dep) == visited.end() &&
                hasCircularDependency(dep, task_map, visited, recursion_stack)) {
                return true;
            }
            else if (recursion_stack.find(dep) != recursion_stack.end()) {
                return true;
            }
        }
    }
    recursion_stack.erase(task_id);
    return false;
}

bool TaskScheduler::canTaskRun(
    const Task& task,
    const std::unordered_map<std::string, TaskStatus>& task_status) {
    
    for (const auto& dep : task.dependencies) {
        auto it = task_status.find(dep);
        if (it == task_status.end() || it->second != TaskStatus::COMPLETED) {
            return false;
        }
    }
    return true;
}

bool TaskScheduler::assignTaskToWorker(
    const Task& task,
    WorkerState& worker_state) {
    
    if (worker_state.available_cores >= task.cpu_cores_required &&
        worker_state.available_memory >= task.memory_required_mb) {
        worker_state.available_cores -= task.cpu_cores_required;
        worker_state.available_memory -= task.memory_required_mb;
        worker_state.running_tasks.insert(task.task_id);
        return true;
    }
    return false;
}

void TaskScheduler::releaseWorkerResources(
    const Task& task,
    WorkerState& worker_state) {
    
    worker_state.available_cores += task.cpu_cores_required;
    worker_state.available_memory += task.memory_required_mb;
    worker_state.running_tasks.erase(task.task_id);
}

std::unordered_map<std::string, TaskStatus> TaskScheduler::scheduleTasks(
    const std::vector<Task>& tasks,
    const std::vector<Worker>& workers) {
    
    std::unordered_map<std::string, TaskStatus> result;
    if (tasks.empty() || workers.empty()) {
        return result;
    }

    // Initialize task map and validate tasks
    std::unordered_map<std::string, Task> task_map;
    for (const auto& task : tasks) {
        task_map[task.task_id] = task;
        result[task.task_id] = TaskStatus::PENDING;
    }

    // Check for circular dependencies
    for (const auto& task : tasks) {
        std::unordered_set<std::string> visited, recursion_stack;
        if (hasCircularDependency(task.task_id, task_map, visited, recursion_stack)) {
            for (const auto& t : tasks) {
                result[t.task_id] = TaskStatus::FAILED;
            }
            return result;
        }
    }

    // Initialize worker states
    std::vector<WorkerState> worker_states;
    for (const auto& worker : workers) {
        worker_states.push_back({
            worker.cpu_cores_available,
            worker.memory_available_mb,
            {}
        });
    }

    // Process tasks
    std::unordered_set<std::string> completed_tasks;
    bool progress = true;
    
    while (progress && completed_tasks.size() < tasks.size()) {
        progress = false;
        
        for (const auto& task : tasks) {
            if (result[task.task_id] != TaskStatus::PENDING) {
                continue;
            }

            if (!canTaskRun(task, result)) {
                continue;
            }

            // Try to find a worker that can handle this task
            bool assigned = false;
            for (int retry = 0; retry < MAX_RETRIES && !assigned; ++retry) {
                for (auto& worker_state : worker_states) {
                    if (assignTaskToWorker(task, worker_state)) {
                        // Simulate task execution
                        if (task.cpu_cores_required <= 32 && task.memory_required_mb <= 65536) {
                            result[task.task_id] = TaskStatus::COMPLETED;
                            completed_tasks.insert(task.task_id);
                        } else {
                            result[task.task_id] = TaskStatus::FAILED;
                            // Mark dependent tasks as failed
                            for (const auto& other_task : tasks) {
                                if (other_task.dependencies.find(task.task_id) != other_task.dependencies.end()) {
                                    result[other_task.task_id] = TaskStatus::FAILED;
                                }
                            }
                        }
                        releaseWorkerResources(task, worker_state);
                        assigned = true;
                        progress = true;
                        break;
                    }
                }
            }

            if (!assigned) {
                result[task.task_id] = TaskStatus::FAILED;
                // Mark dependent tasks as failed
                for (const auto& other_task : tasks) {
                    if (other_task.dependencies.find(task.task_id) != other_task.dependencies.end()) {
                        result[other_task.task_id] = TaskStatus::FAILED;
                    }
                }
            }
        }
    }

    // Mark remaining pending tasks as failed
    for (auto& [task_id, status] : result) {
        if (status == TaskStatus::PENDING) {
            status = TaskStatus::FAILED;
        }
    }

    return result;
}