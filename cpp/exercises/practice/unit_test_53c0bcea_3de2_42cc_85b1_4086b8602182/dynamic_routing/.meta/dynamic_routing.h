#ifndef DYNAMIC_ROUTING_H
#define DYNAMIC_ROUTING_H

#include <vector>

namespace dynamic_routing {

struct Event {
    int time;
    int row;
    int col;
    int type;
};

int minimum_time(int n, int m, const std::vector<std::vector<int>>& grid, int start_row, int start_col,
                 int end_row, int end_col, const std::vector<Event>& events);

int minimum_time(int n, int m, int start_row, int start_col, int end_row, int end_col,
                 const std::vector<Event>& events, const std::vector<std::vector<int>>& grid);

}  // namespace dynamic_routing

#endif