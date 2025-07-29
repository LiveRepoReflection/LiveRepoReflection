#include "task_scheduler.h"
#include <vector>
#include <queue>
#include <unordered_map>
#include <algorithm>

namespace task_scheduler {

int schedule_tasks(int N, const std::vector<int>& id, const std::vector<int>& duration, const std::vector<int>& deadline, const std::vector<std::vector<int>>& dependencies) {
    // Map each task id to its index in the input arrays.
    std::unordered_map<int, int> id_to_index;
    for (int i = 0; i < N; ++i) {
        id_to_index[id[i]] = i;
    }
    
    // Build the dependency graph and compute the indegree for each task.
    std::vector<std::vector<int>> graph(N);
    std::vector<int> indegree(N, 0);
    for (int i = 0; i < N; ++i) {
        for (int dep_id : dependencies[i]) {
            int dep_index = id_to_index[dep_id];
            graph[dep_index].push_back(i);
            indegree[i]++;
        }
    }
    
    // Vector to store the earliest start time and finish time for each task.
    std::vector<int> earliest_start(N, 0);
    std::vector<int> finish_time(N, 0);
    
    // Initialize the queue with tasks that have no dependencies.
    std::queue<int> q;
    for (int i = 0; i < N; ++i) {
        if (indegree[i] == 0) {
            finish_time[i] = duration[i]; // Start at time 0.
            q.push(i);
        }
    }
    
    int processed = 0;
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        processed++;
        
        // Check if the current task u meets its deadline.
        if (finish_time[u] > deadline[u]) {
            return -1;
        }
        
        for (int v : graph[u]) {
            // Update the earliest start time for task v.
            earliest_start[v] = std::max(earliest_start[v], finish_time[u]);
            indegree[v]--;
            if (indegree[v] == 0) {
                finish_time[v] = earliest_start[v] + duration[v];
                q.push(v);
            }
        }
    }
    
    // If not all tasks are processed, then dependencies form a cycle (should not happen as input is a DAG).
    if (processed != N) {
        return -1;
    }
    
    // Calculate the overall makespan and check deadlines for all tasks.
    int makespan = 0;
    for (int i = 0; i < N; ++i) {
        if (finish_time[i] > deadline[i]) {
            return -1;
        }
        makespan = std::max(makespan, finish_time[i]);
    }
    
    return makespan;
}

}