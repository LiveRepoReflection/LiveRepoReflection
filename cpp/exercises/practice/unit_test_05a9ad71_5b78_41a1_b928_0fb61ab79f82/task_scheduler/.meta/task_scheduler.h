#if !defined(TASK_SCHEDULER_H)
#define TASK_SCHEDULER_H

#include <vector>
#include <map>
#include <string>
#include <queue>

struct Machine {
    int id;
    std::map<std::string, int> resources;
};

struct Task {
    int id;
    std::map<std::string, int> resources;
    int duration;
    int arrival_time;
};

struct ScheduleEntry {
    int task_id;
    int machine_id;
    int start_time;
    int end_time;
};

class TaskScheduler {
public:
    std::vector<ScheduleEntry> schedule(const std::vector<Machine>& machines,
                                      const std::vector<Task>& tasks,
                                      int horizon);

private:
    struct Event {
        int time;
        int machine_id;
        std::map<std::string, int> released_resources;
        bool operator>(const Event& other) const { return time > other.time; }
    };

    bool canScheduleTask(const Task& task,
                        const Machine& machine,
                        const std::map<std::string, int>& available_resources,
                        int current_time,
                        int horizon) const;

    void updateAvailableResources(std::map<int, std::map<std::string, int>>& available_resources,
                                int machine_id,
                                const std::map<std::string, int>& resources,
                                bool add);
};

#endif