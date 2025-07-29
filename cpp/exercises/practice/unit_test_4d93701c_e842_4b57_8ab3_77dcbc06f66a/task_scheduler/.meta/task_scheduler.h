#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>
#include <string>

namespace task_scheduler {

struct Task {
    std::string task_id;
    int processing_time;
    int memory_required;
    std::vector<std::string> dependencies;
    int priority;
};

struct Event {
    int time;
    int worker_id;
    std::string task_id;
    std::string event_type; // "START", "END", "FAILED"
};

struct ScheduleResult {
    std::vector<Event> schedule;
    int makespan;
    bool circular_dependency;
    std::vector<std::string> unfulfillable_dependencies;
    std::vector<std::string> tasks_not_executed;
};

ScheduleResult schedule_tasks(int num_workers, int worker_memory,
                              const std::vector<Task>& tasks);

}  // namespace task_scheduler

#endif  // TASK_SCHEDULER_H