#include "task_scheduler.h"
#include <vector>
#include <queue>
#include <algorithm>

using std::vector;
using std::priority_queue;
using std::max;

struct AvailableTask {
    int deadline;
    int release_time;
    int execution_time;
    int id;
};

struct CompareAvailable {
    // Order by deadline, then by release_time
    bool operator()(const AvailableTask& a, const AvailableTask& b) const {
        if(a.deadline == b.deadline)
            return a.release_time > b.release_time;
        return a.deadline > b.deadline;
    }
};

int schedule_tasks(int n, int k, const vector<Task>& tasks_input) {
    // Build task lookup by id.
    vector<Task> tasks(n);
    for (const auto& t : tasks_input) {
        tasks[t.id] = t;
    }
    
    // Build graph and compute in-degrees.
    vector<vector<int>> children(n);
    vector<int> in_degree(n, 0);
    for (int i = 0; i < n; i++) {
        for (int dep : tasks[i].dependencies) {
            children[dep].push_back(i);
            in_degree[i]++;
        }
    }
    
    // Current release times for tasks: the earliest time after dependencies finish.
    vector<int> release_time(n, 0);
    
    // Priority queue for available tasks: tasks whose dependencies are all scheduled.
    priority_queue<AvailableTask, vector<AvailableTask>, CompareAvailable> available_tasks;
    
    // Initially, tasks with in_degree 0 are available with release time 0.
    for (int i = 0; i < n; i++) {
        if(in_degree[i] == 0) {
            AvailableTask av;
            av.deadline = tasks[i].deadline;
            av.release_time = 0;
            av.execution_time = tasks[i].execution_time;
            av.id = i;
            available_tasks.push(av);
        }
    }
    
    // Priority queue for machines' next available times.
    // Using a min-heap.
    priority_queue<int, vector<int>, std::greater<int>> machine_times;
    for (int i = 0; i < k; i++) {
        machine_times.push(0);
    }
    
    int scheduled_count = 0;
    
    while (!available_tasks.empty()) {
        // Get the machine that becomes free the earliest.
        int current_machine_time = machine_times.top();
        machine_times.pop();
        
        // Get the task with the earliest deadline.
        AvailableTask current_task = available_tasks.top();
        available_tasks.pop();
        
        // If the machine is free before the task is ready, wait until the task's release time.
        int start_time = max(current_machine_time, current_task.release_time);
        int finish_time = start_time + current_task.execution_time;
        
        // If finishing this task exceeds its deadline, scheduling is impossible.
        if (finish_time > current_task.deadline) {
            return -1;
        }
        
        scheduled_count++;
        
        // For each child, update its release time and in-degree.
        for (int child_id : children[current_task.id]) {
            // The child cannot start before this task finishes.
            release_time[child_id] = max(release_time[child_id], finish_time);
            in_degree[child_id]--;
            if (in_degree[child_id] == 0) {
                AvailableTask childTask;
                childTask.deadline = tasks[child_id].deadline;
                childTask.release_time = release_time[child_id];
                childTask.execution_time = tasks[child_id].execution_time;
                childTask.id = child_id;
                available_tasks.push(childTask);
            }
        }
        
        // Update the machine's availability time with the finish time.
        machine_times.push(finish_time);
    }
    
    // If not all tasks were scheduled, there is a cycle or dependency issue.
    if (scheduled_count != n) {
        return -1;
    }
    
    // The schedule is feasible with all tasks meeting their deadlines.
    return 0;
}