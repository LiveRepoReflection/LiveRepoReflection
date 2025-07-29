#include "vehicle_routing.h"
#include <queue>
#include <tuple>
#include <string>
#include <vector>
#include <algorithm>

namespace vehicle_routing {

// Structure representing a state in BFS: position (r, c), current time, remaining fuel, and number of charging station visits so far.
struct State {
    int r;
    int c;
    int time;
    int fuel;
    int charge;
};

// Directions for movement: up, down, left, right.
static const int dr[4] = {-1, 1, 0, 0};
static const int dc[4] = {0, 0, -1, 1};

// Helper: Get the appropriate configuration index at a given time.
inline int getConfigIndex(int time, int M) {
    return (time < M) ? time : M - 1;
}

// Check if a cell is traversable based on the character.
inline bool isTraversable(char cell) {
    return (cell != '#');
}

// The solve function implements a breadth-first search (BFS) over the state space.
// N: grid size (NxN), F: maximum fuel, K: maximum allowed charging station visits,
// M: number of obstacle configurations, configurations: vector of grid configurations.
// The first configuration (index 0) contains the constant positions of 'S', 'D', and 'C'.
int solve(int N, int F, int K, int M, const std::vector<std::vector<std::string>>& configurations) {
    // Find the starting and destination positions from the first configuration.
    int start_r = -1, start_c = -1;
    int dest_r = -1, dest_c = -1;
    const std::vector<std::string>& initialGrid = configurations[0];
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            char ch = initialGrid[i][j];
            if (ch == 'S') {
                start_r = i;
                start_c = j;
            } else if (ch == 'D') {
                dest_r = i;
                dest_c = j;
            }
        }
    }
    if(start_r == -1 || dest_r == -1) {
        return -1; // Invalid grid as no starting or destination point.
    }
    
    // Use a 5D visited state: position (r, c), configuration index (for time), fuel level, and charge visits.
    // Since configurations become stable after time M-1, we use config index = M-1 for time steps >= M-1.
    // We'll encode state as tuple: (r, c, config_index, fuel, charge)
    // Use a vector of bool dimensions for visited states.
    // Dimensions: row: N, col: N, config index: M (since M configurations), fuel: F+1, charge: K+1.
    std::vector<std::vector<std::vector<std::vector<std::vector<bool>>>>> visited(
        N, std::vector<std::vector<std::vector<std::vector<bool>>>>(
            N, std::vector<std::vector<std::vector<bool>>>(
                M, std::vector<std::vector<bool>>(
                    F + 1, std::vector<bool>(K + 1, false)
                )
            )
        )
    );
    
    // Initialize BFS queue.
    std::queue<State> q;
    State startState = {start_r, start_c, 0, F, 0};
    int config_index = getConfigIndex(0, M);
    visited[start_r][start_c][config_index][F][0] = true;
    q.push(startState);

    while (!q.empty()) {
        State cur = q.front();
        q.pop();
        
        // Get current configuration index based on current time.
        int cur_conf = getConfigIndex(cur.time, M);
        char curCell = configurations[cur_conf][cur.r][cur.c];
        // Check if destination reached.
        if (cur.r == dest_r && cur.c == dest_c && isTraversable(curCell)) {
            return cur.time;
        }
        
        // If no fuel left, cannot move further.
        if (cur.fuel == 0) continue;
        
        // Explore neighbors.
        for (int i = 0; i < 4; i++) {
            int nr = cur.r + dr[i];
            int nc = cur.c + dc[i];
            int ntime = cur.time + 1;
            if (nr < 0 || nr >= N || nc < 0 || nc >= N) continue;
            
            int nconf = getConfigIndex(ntime, M);
            char nextCell = configurations[nconf][nr][nc];
            if (!isTraversable(nextCell)) continue;  // Blocked cell.
            
            int nfuel = cur.fuel - 1;
            int ncharge = cur.charge;
            // If the cell is a charging station 'C' and we have not exceeded the limit, recharge fuel.
            if (nextCell == 'C' && cur.charge < K) {
                nfuel = F;
                ncharge = cur.charge + 1;
            }
            
            // Check if the new state has been visited.
            if (nfuel < 0) continue; // Should not happen, but safe.
            if (!visited[nr][nc][nconf][nfuel][ncharge]) {
                visited[nr][nc][nconf][nfuel][ncharge] = true;
                State nextState = {nr, nc, ntime, nfuel, ncharge};
                q.push(nextState);
            }
        }
    }
    
    return -1;
}

}  // namespace vehicle_routing