#include "dynamic_routing.h"
#include <vector>
#include <queue>
#include <limits>
#include <algorithm>

namespace dynamic_routing {

using namespace std;
const int INF = std::numeric_limits<int>::max();

// Helper structure for state events per cell: pair of (time, state) where state==0 means open, 1 means blocked.
typedef pair<int, int> TimeState;

// Build cell event logs for each cell from the initial grid and events.
static vector<vector<vector<TimeState>>> build_cell_events(int n, int m, 
    const vector<vector<int>>& grid, const vector<Event>& events) {
    vector<vector<vector<TimeState>>> cellEvents(n, vector<vector<TimeState>>(m));
    
    // Initialize each cell with its initial state at time=0.
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < m; c++) {
            cellEvents[r][c].push_back({0, grid[r][c]});
        }
    }
    
    // Add events to corresponding cells.
    for (const auto& e : events) {
        // Ensure that event cell indices are within bounds.
        if (e.row >= 0 && e.row < n && e.col >= 0 && e.col < m) {
            cellEvents[e.row][e.col].push_back({e.time, e.type});
        }
    }
    
    // Sort the event list for each cell by time.
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < m; c++) {
            sort(cellEvents[r][c].begin(), cellEvents[r][c].end(), [](const TimeState &a, const TimeState &b){
                return a.first < b.first;
            });
        }
    }
    
    return cellEvents;
}

// Binary search utility: given sorted events for a cell, return the state at time t.
static int get_state_at_time(const vector<TimeState>& events, int t) {
    // We want the last event whose time is <= t.
    int lo = 0, hi = events.size()-1;
    int ans = events[0].second;  // initial state at time 0.
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (events[mid].first <= t) {
            ans = events[mid].second;
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return ans;
}

// Check if cell (r, c) is open at time t.
static bool is_open(int r, int c, int t, const vector<vector<vector<TimeState>>>& cellEvents) {
    return get_state_at_time(cellEvents[r][c], t) == 0;
}

// Dijkstra/BFS style search in time-space.
static int search_minimum_time(int n, int m, const vector<vector<int>>& grid,
    int start_row, int start_col, int end_row, int end_col, const vector<Event>& events) {
    
    // Build event logs per cell.
    auto cellEvents = build_cell_events(n, m, grid, events);
    
    // Check if starting cell is open at time 0.
    if (!is_open(start_row, start_col, 0, cellEvents)) {
        return -1;
    }
    
    // Directions: up, down, left, right.
    vector<pair<int,int>> directions = { { -1, 0 }, { 1, 0 }, { 0, -1 }, { 0, 1 } };
    
    // Priority queue: (time, row, col). Use time as priority.
    typedef tuple<int, int, int> State;
    priority_queue<State, vector<State>, greater<State>> pq;
    vector<vector<int>> best(n, vector<int>(m, INF));
    
    pq.push({0, start_row, start_col});
    best[start_row][start_col] = 0;
    
    while (!pq.empty()) {
        auto [t, r, c] = pq.top();
        pq.pop();
        
        // If we have reached destination and it is open at time t, return t.
        if (r == end_row && c == end_col && is_open(r, c, t, cellEvents)) {
            return t;
        }
        
        // If a better time is already recorded, skip.
        if (t > best[r][c]) continue;
        
        // Try waiting in current cell.
        int waitTime = t + 1;
        if (is_open(r, c, waitTime, cellEvents) && waitTime < best[r][c]) {
            best[r][c] = waitTime;
            pq.push({waitTime, r, c});
        }
        
        // Try moving to neighbors.
        for (auto &d : directions) {
            int nr = r + d.first;
            int nc = c + d.second;
            int nt = t + 1;
            if (nr < 0 || nr >= n || nc < 0 || nc >= m) continue;
            // Move to neighbor only if neighbor cell is open at time nt.
            if (is_open(nr, nc, nt, cellEvents)) {
                if (nt < best[nr][nc]) {
                    best[nr][nc] = nt;
                    pq.push({nt, nr, nc});
                }
            }
        }
    }
    
    return -1;
}

int minimum_time(int n, int m, const vector<vector<int>>& grid, int start_row, int start_col,
                 int end_row, int end_col, const vector<Event>& events) {
    return search_minimum_time(n, m, grid, start_row, start_col, end_row, end_col, events);
}

int minimum_time(int n, int m, int start_row, int start_col, int end_row, int end_col,
                 const vector<Event>& events, const vector<vector<int>>& grid) {
    return search_minimum_time(n, m, grid, start_row, start_col, end_row, end_col, events);
}

}  // namespace dynamic_routing