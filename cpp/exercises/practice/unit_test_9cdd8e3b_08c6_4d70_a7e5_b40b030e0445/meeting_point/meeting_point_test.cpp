#include "catch.hpp"
#include "meeting_point.h"
#include <vector>

using std::vector;

TEST_CASE("Example grid test", "[meeting_point]") {
    // Grid description:
    // Row 0: 1 0 0 0 1
    // Row 1: 0 0 0 0 0
    // Row 2: 0 0 1 0 0
    // Buildings at: (0,0), (0,4), (2,2)
    vector<vector<int>> grid = {
        {1, 0, 0, 0, 1},
        {0, 0, 0, 0, 0},
        {0, 0, 1, 0, 0}
    };
    // The optimal meeting point is (0,2) or (2,2) or (0,2) depending on median selection,
    // but the minimal total Manhattan distance is 6.
    int expected = 6;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Grid with no buildings", "[meeting_point]") {
    // Grid with all zeros: should return -1 as no meeting point can be computed.
    vector<vector<int>> grid = {
        {0, 0, 0},
        {0, 0, 0},
        {0, 0, 0}
    };
    int expected = -1;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Grid with all buildings", "[meeting_point]") {
    // For a 3x3 grid with all ones, the optimal meeting point is the median cell (1,1).
    // Sum of Manhattan distances from (1,1) will be:
    // (0,0): 2, (0,1): 1, (0,2): 2, (1,0): 1, (1,1): 0, (1,2): 1,
    // (2,0): 2, (2,1): 1, (2,2): 2 -> total = 12.
    vector<vector<int>> grid = {
        {1, 1, 1},
        {1, 1, 1},
        {1, 1, 1}
    };
    int expected = 12;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Grid with single building", "[meeting_point]") {
    // Single building grid, the optimal meeting point is at the location of the building.
    vector<vector<int>> grid = {
        {0, 0, 0},
        {0, 1, 0},
        {0, 0, 0}
    };
    int expected = 0;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Single row grid", "[meeting_point]") {
    // Single row with buildings at various positions.
    // Optimal meeting point is the median index.
    vector<vector<int>> grid = {
        {1, 0, 1, 0, 1}
    };
    // Positions: 0,2,4 -> median is 2 -> total distance = |0-2|+|2-2|+|4-2| = 2+0+2 = 4.
    int expected = 4;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Single column grid", "[meeting_point]") {
    // Single column with buildings at various positions.
    vector<vector<int>> grid = {
        {1},
        {0},
        {1},
        {0},
        {1}
    };
    // Building rows: 0,2,4 -> median is 2 -> total distance = |0-2|+|2-2|+|4-2| = 2+0+2 = 4.
    int expected = 4;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Large sparse grid", "[meeting_point]") {
    // A sparse large grid where buildings are few.
    // 10x10 grid with buildings in some far apart positions.
    vector<vector<int>> grid(10, vector<int>(10, 0));
    grid[0][0] = 1;
    grid[0][9] = 1;
    grid[9][0] = 1;
    grid[9][9] = 1;
    // The median rows and columns are at 4 or 5.
    // Calculate expected manually:
    // Choosing median row = 4 and median col = 4.
    // Distance from (0,0) = 4+4 = 8
    // from (0,9) = 4+5 = 9
    // from (9,0) = 5+4 = 9
    // from (9,9) = 5+5 = 10
    // Total = 8+9+9+10 = 36.
    int expected = 36;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}

TEST_CASE("Grid with one row and one column", "[meeting_point]") {
    // Single cell grid that is a building.
    vector<vector<int>> grid = {
        {1}
    };
    int expected = 0;
    int result = meeting_point::min_total_distance(grid);
    REQUIRE(result == expected);
}