use std::cmp::Reverse;
use std::collections::BinaryHeap;

const INF: i64 = i64::MAX / 2;

pub struct DynamicPaths {
    grid: Vec<Vec<u32>>,
    dist: Vec<Vec<i64>>,
    sources: Vec<(usize, usize)>,
    rows: usize,
    cols: usize,
}

impl DynamicPaths {
    pub fn new(grid: Vec<Vec<u32>>, sources: Vec<(usize, usize)>) -> Self {
        let rows = grid.len();
        let cols = if rows > 0 { grid[0].len() } else { 0 };
        let mut dp = DynamicPaths {
            grid,
            dist: vec![vec![INF; cols]; rows],
            sources,
            rows,
            cols,
        };
        dp.compute_all();
        dp
    }

    fn compute_all(&mut self) {
        // Recompute all distances using a multi-source Dijkstra.
        for r in 0..self.rows {
            for c in 0..self.cols {
                self.dist[r][c] = INF;
            }
        }
        let mut heap = BinaryHeap::new();
        
        // Initialize distances for all valid source cells.
        for &(r, c) in &self.sources {
            if r < self.rows && c < self.cols {
                if self.dist[r][c] > 0 {
                    self.dist[r][c] = 0;
                    heap.push(Reverse((0, r, c)));
                }
            }
        }
        
        // Directions for neighbors: down, up, right, left.
        while let Some(Reverse((current_dist, r, c))) = heap.pop() {
            if current_dist != self.dist[r][c] {
                continue;
            }
            let neighbors = [
                (r.wrapping_add(1), c),
                (r.wrapping_sub(1), c),
                (r, c.wrapping_add(1)),
                (r, c.wrapping_sub(1)),
            ];
            for &(nr, nc) in neighbors.iter() {
                if nr < self.rows && nc < self.cols {
                    let new_cost = current_dist + self.grid[nr][nc] as i64;
                    if new_cost < self.dist[nr][nc] {
                        self.dist[nr][nc] = new_cost;
                        heap.push(Reverse((new_cost, nr, nc)));
                    }
                }
            }
        }
    }

    // Returns the shortest path cost from any current source to the cell (row, col).
    // If the cell is out of bounds or unreachable, returns -1.
    pub fn get_shortest_path(&self, row: usize, col: usize) -> i64 {
        if row >= self.rows || col >= self.cols {
            return -1;
        }
        if self.dist[row][col] == INF {
            -1
        } else {
            self.dist[row][col]
        }
    }

    // Update the cost at (row, col) to new_cost and recompute the affected paths.
    pub fn update_cost(&mut self, row: usize, col: usize, new_cost: u32) {
        if row >= self.rows || col >= self.cols {
            return;
        }
        self.grid[row][col] = new_cost;
        self.compute_all();
    }

    // Update the set of source locations and recompute the shortest paths.
    pub fn update_sources(&mut self, new_sources: Vec<(usize, usize)>) {
        self.sources = new_sources;
        self.compute_all();
    }
}