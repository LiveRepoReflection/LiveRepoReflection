#include "task_scheduler.h"
#include <algorithm>
#include <vector>

using namespace std;

static int N_global;
static int M_global;
static vector<Task> tasks_global;

// Recursive DFS exploring all valid scheduling orders using bitmask to represent scheduled tasks.
// machineAvail holds the next available time for each machine.
// completion holds the finish time of each task (if scheduled). For tasks not yet scheduled, the value is unused.
static int dfs(int mask, vector<int>& machineAvail, vector<int>& completion) {
    int best = 0;
    // Try to schedule any unscheduled task that is ready (all dependencies completed)
    for (int i = 0; i < N_global; i++) {
        if (!(mask & (1 << i))) {
            // Check if all dependencies of task i have been scheduled.
            bool ready = true;
            int dep_finish = 0;
            for (int dep : tasks_global[i].dependencies) {
                if (!(mask & (1 << dep))) {
                    ready = false;
                    break;
                }
                dep_finish = max(dep_finish, completion[dep]);
            }
            if (!ready)
                continue;
            // Attempt to schedule task i on each machine.
            for (int j = 0; j < M_global; j++) {
                // Earliest start time is the later of the machine's available time or when dependencies are finished.
                int start = max(machineAvail[j], dep_finish);
                int finish = start + tasks_global[i].duration;
                // If finishing time exceeds the deadline, skip scheduling on this machine.
                if (finish > tasks_global[i].deadline)
                    continue;
                // Save old state.
                int oldMachineTime = machineAvail[j];
                int oldCompletion = completion[i];
                // Schedule the task on machine j.
                machineAvail[j] = finish;
                completion[i] = finish;
                int newMask = mask | (1 << i);
                int currentProfit = tasks_global[i].profit + dfs(newMask, machineAvail, completion);
                best = max(best, currentProfit);
                // Backtrack.
                machineAvail[j] = oldMachineTime;
                completion[i] = oldCompletion;
            }
        }
    }
    return best;
}

int maxProfit(int N, int M, const vector<Task>& tasks) {
    N_global = N;
    M_global = M;
    tasks_global = tasks;
    // Initialize each machine availability time to 0.
    vector<int> machineAvail(M, 0);
    // Initialize completion times for tasks.
    vector<int> completion(N, 0);
    return dfs(0, machineAvail, completion);
}