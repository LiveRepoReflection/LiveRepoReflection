#include "meeting_point.h"
#include <vector>
#include <algorithm>
#include <cstdlib>
using std::vector;
using std::abs;

namespace meeting_point {

int min_total_distance(const vector<vector<int>>& grid) {
    if (grid.empty() || grid[0].empty()) {
        return -1;
    }
    
    int m = grid.size();
    int n = grid[0].size();
    vector<int> rows;
    vector<int> cols;
    
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            if (grid[i][j] == 1) {
                rows.push_back(i);
            }
        }
    }
    
    if (rows.empty()) {
        return -1;
    }
    
    // For columns, iterate column-wise to get sorted order.
    for (int j = 0; j < n; j++) {
        for (int i = 0; i < m; i++) {
            if (grid[i][j] == 1) {
                cols.push_back(j);
            }
        }
    }
    
    int median_row = rows[rows.size() / 2];
    int median_col = cols[cols.size() / 2];
    
    long long total_distance = 0;
    for (int r : rows) {
        total_distance += abs(r - median_row);
    }
    for (int c : cols) {
        total_distance += abs(c - median_col);
    }
    
    return static_cast<int>(total_distance);
}

} // namespace meeting_point