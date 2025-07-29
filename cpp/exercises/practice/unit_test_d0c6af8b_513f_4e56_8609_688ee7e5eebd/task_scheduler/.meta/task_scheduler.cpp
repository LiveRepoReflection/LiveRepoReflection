#include "task_scheduler.h"
#include <queue>
#include <vector>
#include <algorithm>

namespace task_scheduler {

struct Event {
    int finish_time;
    int task_id;
    // Comparator: smallest finish_time has highest priority.
    bool operator>(const Event& other) const {
        return finish_time > other.finish_time;
    }
};

int minimum_makespan(int N, int M, const std::vector<int>& duration,
                     const std::vector<std::vector<int>>& dependencies,
                     const std::vector<std::vector<int>>& resource_requirements,
                     const std::vector<int>& resource_capacities) {
    // Precompute each task's resource requirement counts.
    std::vector<std::vector<int>> req_count(N, std::vector<int>(M, 0));
    for (int i = 0; i < N; ++i) {
        for (int r : resource_requirements[i]) {
            if (r < 0 || r >= M) {
                return -1; // invalid resource id, though constraints guarantee validity.
            }
            req_count[i][r] += 1;
        }
    }
    // Check if any task requires more than available capacity.
    for (int i = 0; i < N; ++i) {
        for (int r = 0; r < M; ++r) {
            if (req_count[i][r] > resource_capacities[r]) {
                return -1;
            }
        }
    }
    
    // Build graph structure: indegree and out_edges.
    std::vector<int> indegree(N, 0);
    std::vector<std::vector<int>> out_edges(N);
    for (int i = 0; i < N; ++i) {
        for (int dep : dependencies[i]) {
            // Here, task i depends on 'dep'. So an edge from dep -> i.
            if (dep < 0 || dep >= N) {
                return -1;  // invalid dependency id (should never happen given constraints)
            }
            out_edges[dep].push_back(i);
            ++indegree[i];
        }
    }
    
    // Ready queue: tasks with no outstanding dependencies.
    std::queue<int> ready;
    for (int i = 0; i < N; ++i) {
        if (indegree[i] == 0) {
            ready.push(i);
        }
    }
    
    // Available resources.
    std::vector<int> available = resource_capacities;
    
    // Priority queue for events (finishing tasks).
    std::priority_queue<Event, std::vector<Event>, std::greater<Event>> event_queue;
    
    // To track scheduled tasks (not necessarily finished).
    std::vector<bool> scheduled(N, false);
    // Count finished tasks.
    int finished_count = 0;
    
    // Current simulation time.
    int current_time = 0;
    // Tracks the latest finish time.
    int makespan = 0;
    
    while (finished_count < N) {
        bool scheduled_in_this_round = false;
        // Try to schedule ready tasks if resources permit.
        int ready_size = ready.size();
        // Use a temporary queue for tasks that remain unscheduled.
        std::queue<int> tmp;
        for (int i = 0; i < ready_size; ++i) {
            int task = ready.front();
            ready.pop();
            // Check if resources are available for task.
            bool can_schedule = true;
            for (int r = 0; r < M; ++r) {
                if (req_count[task][r] > available[r]) {
                    can_schedule = false;
                    break;
                }
            }
            if (can_schedule) {
                // Allocate resources.
                for (int r = 0; r < M; ++r) {
                    available[r] -= req_count[task][r];
                }
                // Schedule task: finish_time = current_time + duration[task]
                Event ev;
                ev.finish_time = current_time + duration[task];
                ev.task_id = task;
                event_queue.push(ev);
                scheduled[task] = true;
                scheduled_in_this_round = true;
                makespan = std::max(makespan, ev.finish_time);
            } else {
                // Keep the task in the ready queue for later try.
                tmp.push(task);
            }
        }
        // Move unscheduled tasks back into ready.
        while (!tmp.empty()) {
            ready.push(tmp.front());
            tmp.pop();
        }
        // If no task was scheduled in this round, advance time.
        if (!scheduled_in_this_round) {
            if (event_queue.empty()) {
                // Deadlock: no tasks running and none can be scheduled; return -1.
                return -1;
            }
            // Advance time to the earliest finish event.
            int next_time = event_queue.top().finish_time;
            current_time = next_time;
            // Process all events that finish at current_time.
            while (!event_queue.empty() && event_queue.top().finish_time == current_time) {
                Event ev = event_queue.top();
                event_queue.pop();
                int finished_task = ev.task_id;
                // Release resources.
                for (int r = 0; r < M; ++r) {
                    available[r] += req_count[finished_task][r];
                }
                finished_count++;
                // Update dependents.
                for (int nxt : out_edges[finished_task]) {
                    indegree[nxt]--;
                    if (indegree[nxt] == 0) {
                        ready.push(nxt);
                    }
                }
            }
        }
    }
    
    return makespan;
}

}  // namespace task_scheduler