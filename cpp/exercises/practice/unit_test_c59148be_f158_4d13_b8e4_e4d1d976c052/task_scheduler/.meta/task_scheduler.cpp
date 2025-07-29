#include "task_scheduler.h"
#include <vector>
#include <tuple>
#include <queue>
#include <algorithm>
#include <unordered_set>
#include <climits>

using namespace std;

struct Task {
    int id;
    int duration;
    int deadline;
    vector<int> dependencies;
    int earliest_start = 0;
    int latest_finish = INT_MAX;
};

struct Worker {
    int available_time = 0;
};

pair<int, int> schedule_tasks(int N, int K, const vector<tuple<int, int, int, vector<int>>>& input_tasks) {
    // Convert input to Task objects
    vector<Task> tasks(N);
    unordered_map<int, int> id_to_index;
    
    for (int i = 0; i < N; ++i) {
        const auto& [id, duration, deadline, deps] = input_tasks[i];
        tasks[i] = {id, duration, deadline, deps};
        id_to_index[id] = i;
    }

    // Check for circular dependencies
    for (const auto& task : tasks) {
        unordered_set<int> visited;
        queue<int> q;
        for (int dep : task.dependencies) {
            q.push(dep);
            visited.insert(dep);
        }
        
        while (!q.empty()) {
            int current = q.front();
            q.pop();
            
            if (current == task.id) {
                return {-1, -1}; // Circular dependency found
            }
            
            for (int dep : tasks[id_to_index[current]].dependencies) {
                if (!visited.count(dep)) {
                    visited.insert(dep);
                    q.push(dep);
                }
            }
        }
    }

    // Calculate earliest start times (topological sort)
    vector<int> in_degree(N, 0);
    vector<vector<int>> adj(N);
    
    for (int i = 0; i < N; ++i) {
        for (int dep : tasks[i].dependencies) {
            adj[id_to_index[dep]].push_back(i);
            in_degree[i]++;
        }
    }
    
    queue<int> q;
    for (int i = 0; i < N; ++i) {
        if (in_degree[i] == 0) {
            q.push(i);
        }
    }
    
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        
        for (int v : adj[u]) {
            tasks[v].earliest_start = max(tasks[v].earliest_start, 
                                        tasks[u].earliest_start + tasks[u].duration);
            if (--in_degree[v] == 0) {
                q.push(v);
            }
        }
    }

    // Schedule tasks using greedy approach
    vector<Worker> workers(K);
    vector<pair<int, int>> scheduled_tasks; // (finish_time, task_index)
    
    for (int i = 0; i < N; ++i) {
        scheduled_tasks.emplace_back(tasks[i].earliest_start + tasks[i].duration, i);
    }
    
    // Sort by earliest possible finish time
    sort(scheduled_tasks.begin(), scheduled_tasks.end());
    
    for (auto& [finish_time, task_idx] : scheduled_tasks) {
        // Find the worker that can start earliest
        int min_worker = 0;
        for (int i = 1; i < K; ++i) {
            if (workers[i].available_time < workers[min_worker].available_time) {
                min_worker = i;
            }
        }
        
        int start_time = max(workers[min_worker].available_time, tasks[task_idx].earliest_start);
        finish_time = start_time + tasks[task_idx].duration;
        workers[min_worker].available_time = finish_time;
    }

    // Calculate late tasks and total lateness
    int late_count = 0;
    int total_lateness = 0;
    
    for (int i = 0; i < N; ++i) {
        int finish_time = 0;
        for (const auto& worker : workers) {
            if (worker.available_time > finish_time) {
                finish_time = worker.available_time;
            }
        }
        
        for (const auto& [finish, idx] : scheduled_tasks) {
            if (tasks[idx].deadline < finish) {
                late_count++;
                total_lateness += (finish - tasks[idx].deadline);
            }
        }
        break; // Only need to check once
    }

    return {late_count, total_lateness};
}