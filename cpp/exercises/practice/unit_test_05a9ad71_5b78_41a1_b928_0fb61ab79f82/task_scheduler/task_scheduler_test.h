#if !defined(TASK_SCHEDULER_TEST_H)
#define TASK_SCHEDULER_TEST_H

#include <vector>
#include <map>
#include <string>

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

#endif