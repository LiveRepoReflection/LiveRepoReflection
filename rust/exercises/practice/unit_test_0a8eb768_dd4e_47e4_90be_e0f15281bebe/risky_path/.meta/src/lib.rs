use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap, HashSet};

#[derive(Copy, Clone, Eq, PartialEq, Debug, Hash)]
struct Pos {
    r: usize,
    c: usize,
}

#[derive(Copy, Clone, Eq, PartialEq)]
struct State {
    cost: i32,
    time: usize,
    pos: Pos,
}

// We want the BinaryHeap to be a min-heap based on cost.
impl Ord for State {
    fn cmp(&self, other: &Self) -> Ordering {
        // Notice the flip on cost for min-heap.
        other.cost.cmp(&self.cost)
            .then_with(|| self.time.cmp(&other.time))
    }
}

impl PartialOrd for State {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

// Public function as required.
pub fn find_optimal_path(
    grid: Vec<Vec<char>>,
    risk_grid: Vec<Vec<i32>>,
    obstacle_paths: Vec<Vec<(usize, usize)>>,
    start: (usize, usize),
    destination: (usize, usize),
    t_limit: usize,
) -> Option<Vec<(usize, usize)>> {
    let rows = grid.len();
    if rows == 0 {
        return None;
    }
    let cols = grid[0].len();

    // Pre-calculate static obstacles in a HashSet for quick lookup.
    let mut static_obstacles = HashSet::new();
    for r in 0..rows {
        for c in 0..cols {
            if grid[r][c] == '#' {
                static_obstacles.insert(Pos { r, c });
            }
        }
    }

    // Helper: get dynamic obstacles positions at a given time.
    fn get_dynamic_obstacles(
        obstacle_paths: &Vec<Vec<(usize, usize)>>,
        time: usize,
    ) -> HashSet<Pos> {
        let mut obs_set = HashSet::new();
        for path in obstacle_paths {
            if !path.is_empty() {
                let idx = time % path.len();
                let (r, c) = path[idx];
                obs_set.insert(Pos { r, c });
            }
        }
        obs_set
    }

    // Helper: check if position is within grid bounds.
    let in_bounds = |r: isize, c: isize| -> bool {
        r >= 0 && r < rows as isize && c >= 0 && c < cols as isize
    };

    // Helper: check if the cell at pos, at given dynamic obstacles positions, is adjacent to any obstacle.
    // A cell is "almost colliding" if any adjacent (up, down, left, right) cell contains a dynamic obstacle.
    fn risk_for_cell(pos: Pos, risk_grid: &Vec<Vec<i32>>, dynamic_obs: &HashSet<Pos>, rows: usize, cols: usize) -> i32 {
        let directions = [(-1, 0), (1, 0), (0, -1), (0, 1)];
        for (dr, dc) in directions.iter() {
            let nr = pos.r as isize + dr;
            let nc = pos.c as isize + dc;
            if nr >= 0 && nr < rows as isize && nc >= 0 && nc < cols as isize {
                if dynamic_obs.contains(&Pos { r: nr as usize, c: nc as usize }) {
                    return risk_grid[pos.r][pos.c];
                }
            }
        }
        0
    }

    // Check if start or destination is a static obstacle.
    let start_pos = Pos { r: start.0, c: start.1 };
    let dest_pos = Pos { r: destination.0, c: destination.1 };
    if static_obstacles.contains(&start_pos) || static_obstacles.contains(&dest_pos) {
        return None;
    }

    // Check collision at time 0 with dynamic obstacles.
    let dynamic_obs_t0 = get_dynamic_obstacles(&obstacle_paths, 0);
    if dynamic_obs_t0.contains(&start_pos) {
        return None;
    }

    // Dijkstra's algorithm: state is (r, c, time) with associated cost.
    let mut heap = BinaryHeap::new();
    // Map to store best cost for state key: (r, c, time)
    let mut best: HashMap<(usize, usize, usize), i32> = HashMap::new();
    // Predecessor map for path reconstruction: key: (r, c, time), value: predecessor (r, c, time)
    let mut prev: HashMap<(usize, usize, usize), (usize, usize, usize)> = HashMap::new();

    // Initial risk cost at time 0.
    let initial_cost = risk_for_cell(start_pos, &risk_grid, &dynamic_obs_t0, rows, cols);
    let initial_state = State {
        cost: initial_cost,
        time: 0,
        pos: start_pos,
    };
    heap.push(initial_state);
    best.insert((start_pos.r, start_pos.c, 0), initial_cost);

    let directions = [(0, 1), (1, 0), (0, -1), (-1, 0)];

    while let Some(State { cost, time, pos }) = heap.pop() {
        // If we reach the destination, reconstruct the path.
        if pos == dest_pos {
            // Reconstruct path from the state key (pos, time).
            let mut path: Vec<(usize, usize)> = Vec::new();
            let mut key = (pos.r, pos.c, time);
            path.push((key.0, key.1));
            while let Some(&p_key) = prev.get(&key) {
                path.push((p_key.0, p_key.1));
                key = p_key;
            }
            path.reverse();
            return Some(path);
        }
        // If we've used all allowed time steps, no further expansion.
        if time == t_limit {
            continue;
        }
        let next_time = time + 1;
        let dynamic_obs = get_dynamic_obstacles(&obstacle_paths, next_time);
        for (dr, dc) in directions.iter() {
            let nr = pos.r as isize + dr;
            let nc = pos.c as isize + dc;
            if !in_bounds(nr, nc) {
                continue;
            }
            let npos = Pos {
                r: nr as usize,
                c: nc as usize,
            };
            // Check static obstacle.
            if static_obstacles.contains(&npos) {
                continue;
            }
            // Check collision: robot must not land on a cell occupied by a dynamic obstacle.
            if dynamic_obs.contains(&npos) {
                continue;
            }
            // Calculate additional risk for new cell at next time step.
            let added_risk = risk_for_cell(npos, &risk_grid, &dynamic_obs, rows, cols);
            let new_cost = cost + added_risk;
            let key = (npos.r, npos.c, next_time);
            if new_cost < *best.get(&key).unwrap_or(&i32::MAX) {
                best.insert(key, new_cost);
                prev.insert(key, (pos.r, pos.c, time));
                heap.push(State {
                    cost: new_cost,
                    time: next_time,
                    pos: npos,
                });
            }
        }
    }
    None
}