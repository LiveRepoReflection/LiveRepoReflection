#include "task_scheduler.h"
#include <algorithm>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <vector>

namespace task_scheduler {

struct Event {
    int time;
    int taskId;
    bool isStart;
    
    bool operator>(const Event& other) const {
        return time > other.time;
    }
};

class Scheduler {
private:
    int N, R;
    const std::vector<Task>& tasks;
    std::unordered_map<int, std::vector<int>> dependencyGraph;
    std::unordered_map<int, int> inDegree;
    std::unordered_map<int, Task> taskMap;
    
    void validateInput() {
        if (N <= 0 || R <= 0 || tasks.empty()) {
            throw std::invalid_argument("Invalid input parameters");
        }
        
        std::unordered_set<int> taskIds;
        for (const auto& task : tasks) {
            if (task.resource > R) {
                throw std::invalid_argument("Task resource exceeds limit");
            }
            if (task.duration <= 0) {
                throw std::invalid_argument("Invalid task duration");
            }
            if (taskIds.count(task.id)) {
                throw std::invalid_argument("Duplicate task ID");
            }
            taskIds.insert(task.id);
            taskMap[task.id] = task;
        }
        
        // Validate dependencies
        for (const auto& task : tasks) {
            for (int depId : task.dependencies) {
                if (!taskIds.count(depId)) {
                    throw std::invalid_argument("Invalid dependency");
                }
            }
        }
    }
    
    void buildDependencyGraph() {
        for (const auto& task : tasks) {
            inDegree[task.id] = task.dependencies.size();
            for (int depId : task.dependencies) {
                dependencyGraph[depId].push_back(task.id);
            }
        }
    }
    
    bool detectCycle() {
        std::unordered_map<int, bool> visited;
        std::unordered_map<int, bool> recStack;
        
        for (const auto& task : tasks) {
            if (dfsCheckCycle(task.id, visited, recStack)) {
                return true;
            }
        }
        return false;
    }
    
    bool dfsCheckCycle(int taskId, std::unordered_map<int, bool>& visited, 
                      std::unordered_map<int, bool>& recStack) {
        if (!visited[taskId]) {
            visited[taskId] = true;
            recStack[taskId] = true;
            
            for (int neighbor : dependencyGraph[taskId]) {
                if (!visited[neighbor] && dfsCheckCycle(neighbor, visited, recStack)) {
                    return true;
                } else if (recStack[neighbor]) {
                    return true;
                }
            }
        }
        recStack[taskId] = false;
        return false;
    }

public:
    Scheduler(int n, int r, const std::vector<Task>& t) 
        : N(n), R(r), tasks(t) {
        validateInput();
        buildDependencyGraph();
        if (detectCycle()) {
            throw std::invalid_argument("Circular dependency detected");
        }
    }
    
    int computeMinMakespan() {
        std::priority_queue<std::pair<int, int>, 
                          std::vector<std::pair<int, int>>, 
                          std::greater<>> readyTasks; // (earliest possible start time, taskId)
        
        std::unordered_map<int, int> earliestStart;
        for (const auto& task : tasks) {
            if (inDegree[task.id] == 0) {
                readyTasks.push({0, task.id});
            }
        }
        
        int currentTime = 0;
        int availableResource = R;
        std::priority_queue<Event, std::vector<Event>, std::greater<>> events;
        int completedTasks = 0;
        int makespan = 0;
        
        while (completedTasks < N) {
            // Process completed tasks
            while (!events.empty() && events.top().time <= currentTime) {
                Event event = events.top();
                events.pop();
                
                if (!event.isStart) {
                    availableResource += taskMap[event.taskId].resource;
                    completedTasks++;
                    
                    // Update dependent tasks
                    for (int dependentId : dependencyGraph[event.taskId]) {
                        inDegree[dependentId]--;
                        if (inDegree[dependentId] == 0) {
                            readyTasks.push({event.time, dependentId});
                        }
                    }
                }
            }
            
            // Try to schedule ready tasks
            while (!readyTasks.empty()) {
                auto [earliestTime, taskId] = readyTasks.top();
                
                if (earliestTime > currentTime) {
                    break;
                }
                
                const Task& task = taskMap[taskId];
                if (task.resource <= availableResource) {
                    readyTasks.pop();
                    availableResource -= task.resource;
                    
                    events.push({currentTime + task.duration, taskId, false});
                    makespan = std::max(makespan, currentTime + task.duration);
                } else {
                    break;
                }
            }
            
            // Move time forward
            if (!events.empty()) {
                currentTime = events.top().time;
            } else if (!readyTasks.empty()) {
                currentTime = readyTasks.top().first;
            }
        }
        
        return makespan;
    }
};

int schedule_tasks(int N, int R, const std::vector<Task>& tasks) {
    Scheduler scheduler(N, R, tasks);
    return scheduler.computeMinMakespan();
}

}  // namespace task_scheduler