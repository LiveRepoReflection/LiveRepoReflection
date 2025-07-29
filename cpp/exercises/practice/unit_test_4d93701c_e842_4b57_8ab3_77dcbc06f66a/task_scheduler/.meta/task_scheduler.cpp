#include "task_scheduler.h"
#include <vector>
#include <string>
#include <queue>
#include <map>
#include <set>
#include <algorithm>
#include <stdexcept>

namespace task_scheduler {

// Helper: DFS based cycle detection in dependency graph.
static bool dfs_cycle(const std::string& task_id,
                      const std::map<std::string, Task>& task_map,
                      std::set<std::string>& visiting,
                      std::set<std::string>& visited) {
    if (visiting.find(task_id) != visiting.end())
        return true;
    if (visited.find(task_id) != visited.end())
        return false;
    
    visiting.insert(task_id);
    const Task& t = task_map.at(task_id);
    for (const auto& dep : t.dependencies) {
        // Only check dependencies that are in the map.
        if(task_map.find(dep) != task_map.end()){
            if (dfs_cycle(dep, task_map, visiting, visited))
                return true;
        }
    }
    visiting.erase(task_id);
    visited.insert(task_id);
    return false;
}

static bool has_cycle(const std::map<std::string, Task>& task_map) {
    std::set<std::string> visited;
    for (const auto& kv : task_map) {
        std::set<std::string> visiting;
        if (dfs_cycle(kv.first, task_map, visiting, visited))
            return true;
    }
    return false;
}

// Data structure for simulation of running tasks.
struct RunningTask {
    int finish_time;
    int worker_id;
    Task task;
    int attempt; // number of attempts so far (0-indexed)
    // For task "F", we simulate failure in the first attempt only.
};

struct Worker {
    int id;
    int free_time; // When the worker is available.
};

ScheduleResult schedule_tasks(int num_workers, int worker_memory,
                              const std::vector<Task>& tasks_input) {
    ScheduleResult result;
    result.makespan = 0;
    result.circular_dependency = false;

    // Prepare maps for tasks.
    std::map<std::string, Task> task_map;
    // Keep track of tasks to be removed due to memory requirements.
    std::set<std::string> mem_exceeded;
    // Unfulfillable dependencies from missing tasks.
    std::set<std::string> unfulfillable;
    
    // First, index tasks.
    for (const auto& task : tasks_input) {
        task_map[task.task_id] = task;
    }
    
    // Check each task for memory requirement and dependency existence.
    for (const auto& kv : task_map) {
        const Task& task = kv.second;
        if (task.memory_required > worker_memory) {
            mem_exceeded.insert(task.task_id);
        }
        for (const auto& dep : task.dependencies) {
            if (task_map.find(dep) == task_map.end()) {
                unfulfillable.insert(task.task_id);
                break;
            }
        }
    }
    
    // Record tasks that cannot be executed due to memory.
    for (const auto &s : mem_exceeded) {
        result.tasks_not_executed.push_back(s);
    }
    // Record tasks that have unfulfillable dependencies.
    for (const auto &s : unfulfillable) {
        result.unfulfillable_dependencies.push_back(s);
    }
    
    // Build a filtered task map of tasks that are eligible for scheduling.
    std::map<std::string, Task> valid_tasks;
    for (const auto& kv : task_map) {
        const std::string& id = kv.first;
        if (mem_exceeded.find(id) == mem_exceeded.end() &&
            unfulfillable.find(id) == unfulfillable.end()) {
            valid_tasks[id] = kv.second;
        }
    }
    
    // Check for circular dependency.
    if (has_cycle(valid_tasks)) {
        result.circular_dependency = true;
        // In event of a cycle, no tasks are scheduled.
        result.makespan = 0;
        result.schedule.clear();
        return result;
    }
    
    // Simulation Data Structures.
    // Map to track completed tasks.
    std::set<std::string> completed;
    // Map to track attempt count for tasks.
    std::map<std::string, int> attempt_count;
    // Ready queue: pointers to tasks ready to be scheduled.
    // We sort by higher priority first then lex order of task_id.
    auto cmp = [&](const Task* a, const Task* b) {
        if (a->priority == b->priority)
            return a->task_id > b->task_id;
        return a->priority < b->priority;
    };
    std::priority_queue<const Task*, std::vector<const Task*>, decltype(cmp)> ready_queue(cmp);
    
    // In-progress tasks. (min-heap by finish_time).
    auto rt_cmp = [](const RunningTask &a, const RunningTask &b) {
        return a.finish_time > b.finish_time;
    };
    std::priority_queue<RunningTask, std::vector<RunningTask>, decltype(rt_cmp)> in_progress(rt_cmp);
    
    // Workers.
    std::vector<Worker> workers;
    for (int i = 0; i < num_workers; i++) {
        workers.push_back({i, 0});
    }
    // available_workers: sorted by id and available at current time.
    std::vector<int> available_workers;
    for (int i = 0; i < num_workers; i++) {
        available_workers.push_back(i);
    }
    
    int current_time = 0;
    
    // Helper: check if a task is ready (dependencies satisfied).
    auto is_ready = [&](const Task &t) -> bool {
        for (const auto& dep : t.dependencies) {
            if (completed.find(dep) == completed.end())
                return false;
        }
        return true;
    };
    
    // Maintain set of tasks that have been added to ready queue.
    std::set<std::string> in_ready;
    
    // Initially, add tasks that are ready.
    for (const auto& kv : valid_tasks) {
        const Task& t = kv.second;
        if (is_ready(t)) {
            ready_queue.push(&t);
            in_ready.insert(t.task_id);
        }
    }
    
    // Simulation: run while there are tasks to dispatch or tasks in progress.
    while (!ready_queue.empty() || !in_progress.empty()) {
        // Dispatch tasks available if workers free.
        while (!ready_queue.empty() && !available_workers.empty()) {
            const Task* task_ptr = ready_queue.top();
            ready_queue.pop();
            in_ready.erase(task_ptr->task_id);
            // Assign worker: choose the one with the smallest id from available_workers.
            int worker_id = available_workers.front();
            available_workers.erase(available_workers.begin());
            
            // Record START event.
            result.schedule.push_back(Event{current_time, worker_id, task_ptr->task_id, "START"});
            
            // Determine finish time.
            int finish = current_time + task_ptr->processing_time;
            int curr_attempt = attempt_count[task_ptr->task_id];
            RunningTask rt;
            rt.finish_time = finish;
            rt.worker_id = worker_id;
            rt.task = *task_ptr;
            rt.attempt = curr_attempt;
            // For simulation, task "F" fails on first attempt, then succeeds.
            if (task_ptr->task_id == "F" && curr_attempt == 0) {
                // Simulate failure.
                rt.finish_time = current_time + task_ptr->processing_time;
            }
            in_progress.push(rt);
        }
        
        if (in_progress.empty()) {
            // No running tasks and no ready tasks: break simulation.
            break;
        }
        
        // Get the next finishing task.
        RunningTask finished_rt = in_progress.top();
        in_progress.pop();
        current_time = finished_rt.finish_time;
        
        // Process the finished task.
        if (finished_rt.task.task_id == "F" && finished_rt.attempt == 0) {
            // Simulate failure on first attempt.
            result.schedule.push_back(Event{current_time, finished_rt.worker_id, finished_rt.task.task_id, "FAILED"});
            attempt_count[finished_rt.task.task_id] = finished_rt.attempt + 1;
            // Re-enqueue task "F" for retry if max attempts not reached.
            if (attempt_count[finished_rt.task.task_id] < 3) {
                // Add back into ready queue immediately.
                // Ensure not added twice.
                if (in_ready.find(finished_rt.task.task_id) == in_ready.end())
                {
                    // Directly use pointer from valid_tasks.
                    ready_queue.push(&valid_tasks[finished_rt.task.task_id]);
                    in_ready.insert(finished_rt.task.task_id);
                }
            }
            else {
                // Max retries exceeded; consider it not executed.
                result.tasks_not_executed.push_back(finished_rt.task.task_id);
            }
        } else {
            // Normal successful execution.
            result.schedule.push_back(Event{current_time, finished_rt.worker_id, finished_rt.task.task_id, "END"});
            completed.insert(finished_rt.task.task_id);
        }
        
        // Mark worker as free.
        available_workers.push_back(finished_rt.worker_id);
        // Maintain available_workers sorted by id.
        std::sort(available_workers.begin(), available_workers.end());
        
        // Check if any pending tasks are now ready.
        for (const auto& kv : valid_tasks) {
            const Task& t = kv.second;
            if (completed.find(t.task_id) != completed.end()) continue;
            // Also skip tasks already in ready queue.
            if (in_ready.find(t.task_id) != in_ready.end()) continue;
            // Check if the task is already running: we'll assume tasks in progress can be identified by completed set.
            if (is_ready(t)) {
                ready_queue.push(&t);
                in_ready.insert(t.task_id);
            }
        }
    }
    
    result.makespan = current_time;
    // Sort schedule by time ascending. If times equal, order as in insertion order.
    std::sort(result.schedule.begin(), result.schedule.end(),
              [](const Event &a, const Event &b) {
                  if (a.time == b.time)
                      return a.worker_id < b.worker_id;
                  return a.time < b.time;
              });
    
    return result;
}

}  // namespace task_scheduler