#include "dynamic_routing.h"
#include "catch.hpp"
#include <vector>

using namespace std;
using namespace dynamic_routing;

TEST_CASE("start_equals_destination") {
    int n = 3, m = 3;
    vector<vector<int>> grid = {
        {0, 0, 0},
        {0, 0, 0},
        {0, 0, 0}
    };
    int start_row = 1, start_col = 1;
    int end_row = 1, end_col = 1;
    vector<Event> events; // No events.
    int result = minimum_time(n, m, grid, start_row, start_col, end_row, end_col, events);
    REQUIRE(result == 0);
}

TEST_CASE("basic_open_grid_no_events") {
    int n = 5, m = 5;
    vector<vector<int>> grid(n, vector<int>(m, 0)); // Entire grid is open.
    int start_row = 0, start_col = 0;
    int end_row = 4, end_col = 4;
    vector<Event> events; // No events.
    // Expected shortest path in open grid is Manhattan distance.
    int expected = 8;
    int result = minimum_time(n, m, grid, start_row, start_col, end_row, end_col, events);
    REQUIRE(result == expected);
}

TEST_CASE("delayed_path_opening") {
    // 3x3 grid where the only direct path is initially blocked.
    // Grid layout:
    // [0, 1, 0]
    // [1, 1, 0]
    // [0, 0, 0]
    // Start: (0,0), Destination: (2,0)
    // At time = 1, cell (1,0) becomes open.
    int n = 3, m = 3;
    vector<vector<int>> grid = {
        {0, 1, 0},
        {1, 1, 0},
        {0, 0, 0}
    };
    int start_row = 0, start_col = 0;
    int end_row = 2, end_col = 0;
    vector<Event> events;
    // Event: At time 1, the cell (1,0) becomes open.
    events.push_back({1, 1, 0, 0});
    // Expected path: wait at (0,0) until time 1, then move (0,0)->(1,0)->(2,0)
    // Total time = 2.
    int result = minimum_time(n, m, grid, start_row, start_col, end_row, end_col, events);
    REQUIRE(result == 2);
}

TEST_CASE("no_possible_path") {
    // 2x2 grid with no possible route:
    // [0, 1]
    // [1, 0]
    int n = 2, m = 2;
    vector<vector<int>> grid = {
        {0, 1},
        {1, 0}
    };
    int start_row = 0, start_col = 0;
    int end_row = 1, end_col = 1;
    vector<Event> events; // No events to change the grid.
    int result = minimum_time(n, m, grid, start_row, start_col, end_row, end_col, events);
    REQUIRE(result == -1);
}

TEST_CASE("unsorted_events_opening_diagonal_path") {
    // 4x4 grid: Initially all cells are blocked (1) except the start and destination.
    // Start: (0,0), Destination: (3,3)
    // A path will be created by a series of events that open a specific route.
    int n = 4, m = 4;
    vector<vector<int>> grid(n, vector<int>(m, 1));
    grid[0][0] = 0; // Start is open.
    grid[3][3] = 0; // Destination is open.
    int start_row = 0, start_col = 0;
    int end_row = 3, end_col = 3;
    vector<Event> events;
    // The intended path:
    // (0,0) -> (1,0) -> (1,1) -> (2,1) -> (2,2) -> (3,2) -> (3,3)
    // Events to open these cells (time, row, col, type=0 means open):
    // (1,0) open at time 1
    // (1,1) open at time 2
    // (2,1) open at time 3
    // (2,2) open at time 4
    // (3,2) open at time 5
    // Insert events in unsorted order.
    events.push_back({5, 3, 2, 0});
    events.push_back({1, 1, 0, 0});
    events.push_back({4, 2, 2, 0});
    events.push_back({2, 1, 1, 0});
    events.push_back({3, 2, 1, 0});
    // Expected route:
    // At time 0: at (0,0)
    // Time 1: (1,0) opens -> move to (1,0)
    // Time 2: (1,1) opens -> move to (1,1)
    // Time 3: (2,1) opens -> move to (2,1)
    // Time 4: (2,2) opens -> move to (2,2)
    // Time 5: (3,2) opens -> move to (3,2)
    // Time 6: move to destination (3,3)
    // Expected minimum time = 6.
    int result = minimum_time(n, m, start_row, start_col, end_row, end_col, events, grid);
    // Note: In this test, grid is provided as the initial state.
    REQUIRE(result == 6);
}