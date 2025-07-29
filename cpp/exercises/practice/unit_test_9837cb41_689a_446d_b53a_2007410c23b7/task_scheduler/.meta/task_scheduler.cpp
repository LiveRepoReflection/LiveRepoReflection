#include "task_scheduler.h"
#include <queue>
#include <vector>
#include <algorithm>

namespace task_scheduler {

struct TaskInternal {
    int id;
    int execution_time;
    int deadline;
    int priority;
    // For scheduling: list of successor task indices (using id as key)
    std::vector<int> children;
    // Count of unresolved dependencies
    int indegree;
};

struct AvailableTask {
    // pointer/index to task in tasksInternal, but we can store id
    int id;
    int execution_time;
    int deadline;
    int priority;
};

// Comparator for available tasks: primary by deadline (earlier deadline first).
// If deadlines tie, schedule the task with higher priority penalty (i.e. greater priority) first.
struct AvailableComparator {
    bool operator()(const AvailableTask& a, const AvailableTask& b) const {
        if (a.deadline != b.deadline) {
            return a.deadline > b.deadline; // min-heap: earlier deadline has higher priority.
        }
        return a.priority < b.priority;
    }
};

// Event structure representing a running task finishing at a given time.
struct Event {
    int finish_time;
    int task_id; // id of the finished task.
};

struct EventComparator {
    bool operator()(const Event& a, const Event& b) const {
        return a.finish_time > b.finish_time; // min-heap: earliest finish time first.
    }
};

int scheduleTasks(int n, int k, const std::vector<Task>& tasks) {
    // Build an internal representation indexed by id.
    // Since task ids are unique but may not be sorted, we map id -> TaskInternal.
    std::vector<TaskInternal> tasksInternal(n + 1);
    // Use idToIndex such that tasksInternal[task.id] is filled.
    // Initialize indegree to number of dependencies.
    for (int i = 0; i < n; i++) {
        int id = tasks[i].id;
        tasksInternal[id].id = id;
        tasksInternal[id].execution_time = tasks[i].execution_time;
        tasksInternal[id].deadline = tasks[i].deadline;
        tasksInternal[id].priority = tasks[i].priority;
        tasksInternal[id].indegree = static_cast<int>(tasks[i].dependencies.size());
        // children list will be filled next.
    }
    // Build children list.
    for (int i = 0; i < n; i++) {
        int id = tasks[i].id;
        for (int dep : tasks[i].dependencies) {
            // Task with id 'dep' must finish before current task.
            // So current task is a child of task with id 'dep'.
            tasksInternal[dep].children.push_back(id);
        }
    }
    
    // Preliminary unschedulable check:
    // For any task that has no dependencies, if its execution_time is greater than its deadline,
    // then even if scheduled at time 0 it cannot meet its deadline -> unschedulable -> return -1.
    for (int id = 1; id <= n; id++) {
        if (tasksInternal[id].indegree == 0) {
            if (tasksInternal[id].execution_time > tasksInternal[id].deadline) {
                return -1;
            }
        }
    }
    
    // We'll simulate scheduling.
    // Priority queue for tasks ready to be scheduled.
    std::priority_queue<AvailableTask, std::vector<AvailableTask>, AvailableComparator> availablePQ;
    // Priority queue for events (running tasks finishing).
    std::priority_queue<Event, std::vector<Event>, EventComparator> eventPQ;
    
    // Completion times for tasks, index by id.
    std::vector<int> completion_time(n + 1, 0);
    
    // Initially, add tasks with indegree zero.
    for (int id = 1; id <= n; id++) {
        if (tasksInternal[id].indegree == 0) {
            AvailableTask at;
            at.id = id;
            at.execution_time = tasksInternal[id].execution_time;
            at.deadline = tasksInternal[id].deadline;
            at.priority = tasksInternal[id].priority;
            availablePQ.push(at);
        }
    }
    
    int current_time = 0;
    int scheduled_tasks = 0;
    int running_tasks = 0;  // count of tasks currently running.
    
    // Main simulation loop.
    while (scheduled_tasks < n) {
        // Assign tasks to idle machines if available.
        while (running_tasks < k && !availablePQ.empty()) {
            AvailableTask taskAvail = availablePQ.top();
            availablePQ.pop();
            // The task will start at current_time.
            int start_time = current_time;
            int finish_time = start_time + taskAvail.execution_time;
            // Record completion time.
            completion_time[taskAvail.id] = finish_time;
            // Push event.
            Event ev;
            ev.finish_time = finish_time;
            ev.task_id = taskAvail.id;
            eventPQ.push(ev);
            running_tasks++;
        }
        
        // If no tasks are currently running, then the next available task hasn't arrived: advance time.
        if (eventPQ.empty()) {
            // This should not happen unless there is a gap in schedule.
            // In that case, if availablePQ is empty but not all tasks scheduled, we advance current_time arbitrarily.
            if (!availablePQ.empty()) {
                // Should not happen as we enter while above.
                current_time++;
            } else {
                // No event and no available task, break out.
                break;
            }
        } else {
            // Get the next event.
            Event nextEv = eventPQ.top();
            eventPQ.pop();
            // Advance current time to the finish time of the event.
            current_time = nextEv.finish_time;
            running_tasks--;
            scheduled_tasks++;
            // Process children of the finished task.
            int finishedTaskId = nextEv.task_id;
            for (int childId : tasksInternal[finishedTaskId].children) {
                tasksInternal[childId].indegree--;
                if (tasksInternal[childId].indegree == 0) {
                    AvailableTask at;
                    at.id = childId;
                    at.execution_time = tasksInternal[childId].execution_time;
                    at.deadline = tasksInternal[childId].deadline;
                    at.priority = tasksInternal[childId].priority;
                    availablePQ.push(at);
                }
            }
        }
    }
    
    // After simulation, check if all tasks scheduled.
    if (scheduled_tasks < n) {
        return -1;
    }
    
    // Compute total weighted tardiness.
    long long total_tardiness = 0;
    for (int id = 1; id <= n; id++) {
        int tardiness = (completion_time[id] > tasksInternal[id].deadline) ? (completion_time[id] - tasksInternal[id].deadline) : 0;
        total_tardiness += static_cast<long long>(tasksInternal[id].priority) * tardiness;
    }
    
    return static_cast<int>(total_tardiness);
}

} // namespace task_scheduler