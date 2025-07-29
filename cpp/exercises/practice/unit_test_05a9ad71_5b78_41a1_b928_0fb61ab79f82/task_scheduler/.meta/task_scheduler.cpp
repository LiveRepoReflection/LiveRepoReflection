#include "task_scheduler.h"
#include <algorithm>
#include <set>

std::vector<ScheduleEntry> TaskScheduler::schedule(const std::vector<Machine>& machines,
                                                 const std::vector<Task>& tasks,
                                                 int horizon) {
    std::vector<ScheduleEntry> schedule;
    std::map<int, std::map<std::string, int>> available_resources;
    std::priority_queue<Event, std::vector<Event>, std::greater<Event>> events;
    std::set<int> unscheduled_tasks;

    // Initialize available resources for each machine
    for (const auto& machine : machines) {
        available_resources[machine.id] = machine.resources;
    }

    // Initialize unscheduled tasks
    for (size_t i = 0; i < tasks.size(); ++i) {
        unscheduled_tasks.insert(i);
    }

    for (int current_time = 0; current_time < horizon; ++current_time) {
        // Process completed tasks and release their resources
        while (!events.empty() && events.top().time == current_time) {
            const auto& event = events.top();
            updateAvailableResources(available_resources,
                                   event.machine_id,
                                   event.released_resources,
                                   true);
            events.pop();
        }

        // Try to schedule tasks
        bool scheduled_task = true;
        while (scheduled_task) {
            scheduled_task = false;
            
            for (auto task_idx_it = unscheduled_tasks.begin();
                 task_idx_it != unscheduled_tasks.end();
                 ) {
                const Task& task = tasks[*task_idx_it];
                
                // Skip if task hasn't arrived yet
                if (task.arrival_time > current_time) {
                    ++task_idx_it;
                    continue;
                }

                // Try to find a suitable machine
                bool task_scheduled = false;
                for (const auto& machine : machines) {
                    if (canScheduleTask(task,
                                      machine,
                                      available_resources[machine.id],
                                      current_time,
                                      horizon)) {
                        // Schedule the task
                        ScheduleEntry entry{
                            task.id,
                            machine.id,
                            current_time,
                            current_time + task.duration
                        };
                        schedule.push_back(entry);

                        // Update available resources
                        updateAvailableResources(available_resources,
                                               machine.id,
                                               task.resources,
                                               false);

                        // Add completion event
                        Event completion_event{
                            current_time + task.duration,
                            machine.id,
                            task.resources
                        };
                        events.push(completion_event);

                        task_scheduled = true;
                        scheduled_task = true;
                        break;
                    }
                }

                if (task_scheduled) {
                    task_idx_it = unscheduled_tasks.erase(task_idx_it);
                } else {
                    ++task_idx_it;
                }
            }
        }
    }

    return schedule;
}

bool TaskScheduler::canScheduleTask(const Task& task,
                                  const Machine& machine,
                                  const std::map<std::string, int>& available_resources,
                                  int current_time,
                                  int horizon) const {
    // Check if task can complete within horizon
    if (current_time + task.duration > horizon) {
        return false;
    }

    // Check if machine has all required resource types
    for (const auto& required : task.resources) {
        if (machine.resources.find(required.first) == machine.resources.end()) {
            return false;
        }
    }

    // Check if sufficient resources are available
    for (const auto& required : task.resources) {
        auto available_it = available_resources.find(required.first);
        if (available_it == available_resources.end() ||
            available_it->second < required.second) {
            return false;
        }
    }

    return true;
}

void TaskScheduler::updateAvailableResources(
    std::map<int, std::map<std::string, int>>& available_resources,
    int machine_id,
    const std::map<std::string, int>& resources,
    bool add) {
    for (const auto& resource : resources) {
        if (add) {
            available_resources[machine_id][resource.first] += resource.second;
        } else {
            available_resources[machine_id][resource.first] -= resource.second;
        }
    }
}