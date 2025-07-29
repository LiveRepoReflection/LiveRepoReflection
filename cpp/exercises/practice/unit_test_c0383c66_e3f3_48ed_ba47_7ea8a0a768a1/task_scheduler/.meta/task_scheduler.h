#ifndef TASK_SCHEDULER_H
#define TASK_SCHEDULER_H

#include <vector>
using namespace std;

struct Task {
    int id;
    int duration;
    int deadline;
    int profit;
    vector<int> dependencies;
};

int maxProfit(int N, int M, const vector<Task>& tasks);

#endif