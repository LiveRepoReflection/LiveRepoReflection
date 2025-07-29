#include "task_scheduler.h"
#include <algorithm>
#include <queue>
#include <set>
#include <map>
#include <limits>

namespace task_scheduler {

struct Task {
    int id;
    int duration;
    int resource;
    std::vector<int> deps;
    int earliest_start;
    
    Task(int i, int d, int r, const std::vector<int>& dep) 
        : id(i), duration(d), resource(r), deps(dep), earliest_start(0) {}
};

bool detectCycle(const std::vector<std::vector<int>>& graph, 
                std::vector<bool>& visited, 
                std::vector<bool>& recursionStack,
                int node) {
    if(!visited[node]) {
        visited[node] = true;
        recursionStack[node] = true;
        
        for(int neighbor : graph[node]) {
            if(!visited[neighbor] && detectCycle(graph, visited, recursionStack, neighbor))
                return true;
            else if(recursionStack[neighbor])
                return true;
        }
    }
    recursionStack[node] = false;
    return false;
}

bool hasCycle(int N, const std::vector<std::vector<int>>& dependencies) {
    std::vector<bool> visited(N, false);
    std::vector<bool> recursionStack(N, false);
    
    for(int i = 0; i < N; i++) {
        if(detectCycle(dependencies, visited, recursionStack, i))
            return true;
    }
    return false;
}

void calculateEarliestStart(std::vector<Task>& tasks) {
    std::vector<int> inDegree(tasks.size(), 0);
    std::vector<std::vector<int>> graph(tasks.size());
    
    // Build graph and calculate in-degrees
    for(size_t i = 0; i < tasks.size(); i++) {
        for(int dep : tasks[i].deps) {
            graph[dep].push_back(i);
            inDegree[i]++;
        }
    }
    
    // Topological sort using queue
    std::queue<int> q;
    for(size_t i = 0; i < tasks.size(); i++) {
        if(inDegree[i] == 0) {
            q.push(i);
        }
    }
    
    while(!q.empty()) {
        int current = q.front();
        q.pop();
        
        // Calculate earliest start time based on dependencies
        int maxDependencyEnd = 0;
        for(int dep : tasks[current].deps) {
            maxDependencyEnd = std::max(maxDependencyEnd, 
                                      tasks[dep].earliest_start + tasks[dep].duration);
        }
        tasks[current].earliest_start = maxDependencyEnd;
        
        // Process neighbors
        for(int neighbor : graph[current]) {
            inDegree[neighbor]--;
            if(inDegree[neighbor] == 0) {
                q.push(neighbor);
            }
        }
    }
}

bool isResourceAvailable(const std::vector<Task>& tasks,
                        const std::vector<int>& schedule,
                        int taskId,
                        int startTime,
                        int resourceLimit) {
    std::map<int, int> resourceUsage;
    
    // Check resource usage for all scheduled tasks
    for(size_t i = 0; i < schedule.size(); i++) {
        if(schedule[i] == -1) continue;
        
        int start = schedule[i];
        int end = start + tasks[i].duration;
        
        if(!(end <= startTime || start >= startTime + tasks[taskId].duration)) {
            // Tasks overlap
            for(int t = std::max(start, startTime); 
                t < std::min(end, startTime + tasks[taskId].duration); t++) {
                resourceUsage[t] += tasks[i].resource;
                if(resourceUsage[t] + tasks[taskId].resource > resourceLimit) {
                    return false;
                }
            }
        }
    }
    return true;
}

std::vector<int> schedule(int N,
                         const std::vector<int>& duration,
                         const std::vector<int>& resource_requirement,
                         const std::vector<std::vector<int>>& dependencies,
                         int resource_limit) {
    
    // Check for invalid input
    if(hasCycle(N, dependencies)) {
        return std::vector<int>();
    }
    
    // Create task objects
    std::vector<Task> tasks;
    for(int i = 0; i < N; i++) {
        if(resource_requirement[i] > resource_limit) {
            return std::vector<int>();
        }
        tasks.emplace_back(i, duration[i], resource_requirement[i], dependencies[i]);
    }
    
    // Calculate earliest possible start times
    calculateEarliestStart(tasks);
    
    // Priority queue to schedule tasks (earliest deadline first)
    auto comparator = [](const Task& a, const Task& b) {
        return a.earliest_start + a.duration < b.earliest_start + b.duration;
    };
    std::priority_queue<Task, std::vector<Task>, decltype(comparator)> pq(comparator);
    
    for(const Task& task : tasks) {
        pq.push(task);
    }
    
    std::vector<int> schedule(N, -1);
    
    // Schedule tasks
    while(!pq.empty()) {
        Task current = pq.top();
        pq.pop();
        
        int startTime = current.earliest_start;
        bool scheduled = false;
        
        while(!scheduled) {
            if(isResourceAvailable(tasks, schedule, current.id, startTime, resource_limit)) {
                schedule[current.id] = startTime;
                scheduled = true;
            } else {
                startTime++;
            }
            
            if(startTime > 10000) { // Practical limit to prevent infinite loops
                return std::vector<int>();
            }
        }
    }
    
    return schedule;
}

} // namespace task_scheduler