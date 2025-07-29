#if !defined(TASK_SCHEDULER_TEST_H)
#define TASK_SCHEDULER_TEST_H

#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>

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
public:
    std::unordered_map<std::string, TaskStatus> scheduleTasks(
        const std::vector<Task>& tasks,
        const std::vector<Worker>& workers);
};

#endif // TASK_SCHEDULER_TEST_H