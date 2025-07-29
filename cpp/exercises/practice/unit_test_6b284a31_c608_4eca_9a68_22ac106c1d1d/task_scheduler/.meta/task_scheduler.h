#if !defined(TASK_SCHEDULER_H)
#define TASK_SCHEDULER_H

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <queue>

enum class TaskStatus {
    PENDING,
    RUNNING,
    COMPLETED,
    FAILED
};

struct Task {
    std::string task_id;
    std::string command;
    std::unordered_set<std::string> dependencies;
    int cpu_cores_required;
    int memory_required_mb;
    TaskStatus status;
};

struct Worker {
    int worker_id;
    int cpu_cores_available;
    int memory_available_mb;
};

class TaskScheduler {
private:
    static const int MAX_RETRIES = 3;
    
    struct WorkerState {
        int available_cores;
        int available_memory;
        std::unordered_set<std::string> running_tasks;
    };
    
    bool hasCircularDependency(const std::string& task_id,
                             const std::unordered_map<std::string, Task>& task_map,
                             std::unordered_set<std::string>& visited,
                             std::unordered_set<std::string>& recursion_stack);
                             
    bool canTaskRun(const Task& task,
                    const std::unordered_map<std::string, TaskStatus>& task_status);
                    
    bool assignTaskToWorker(const Task& task,
                           WorkerState& worker_state);
                           
    void releaseWorkerResources(const Task& task,
                               WorkerState& worker_state);

public:
    std::unordered_map<std::string, TaskStatus> scheduleTasks(
        const std::vector<Task>& tasks,
        const std::vector<Worker>& workers);
};

#endif