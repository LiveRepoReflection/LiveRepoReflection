use std::collections::{HashMap, VecDeque};

#[derive(Clone)]
pub struct Link {
    pub src: String,
    pub dst: String,
    pub capacity: u64,
}

pub struct Network {
    pub routers: Vec<String>,
    pub links: Vec<Link>,
    // Adjacency list mapping router to vector of (neighbor, link index)
    pub adj: HashMap<String, Vec<(String, usize)>>,
}

impl Network {
    pub fn new() -> Self {
        Network {
            routers: Vec::new(),
            links: Vec::new(),
            adj: HashMap::new(),
        }
    }

    pub fn add_router(&mut self, router: &str) {
        if !self.routers.contains(&router.to_string()) {
            self.routers.push(router.to_string());
            self.adj.insert(router.to_string(), Vec::new());
        }
    }

    pub fn add_link(&mut self, src: &str, dst: &str, capacity: u64) {
        // Ensure routers exist
        self.add_router(src);
        self.add_router(dst);
        // Add link and update adjacency list
        let link = Link {
            src: src.to_string(),
            dst: dst.to_string(),
            capacity,
        };
        self.links.push(link);
        let link_index = self.links.len() - 1;
        if let Some(neighbors) = self.adj.get_mut(src) {
            neighbors.push((dst.to_string(), link_index));
        }
    }

    // Find shortest path (in terms of hops) from src to dst.
    // Returns a vector of link indices representing the path.
    pub fn find_path(&self, src: &str, dst: &str) -> Option<Vec<usize>> {
        let mut queue = VecDeque::new();
        let mut visited = HashMap::new();

        queue.push_back(src.to_string());
        visited.insert(src.to_string(), (None, None)); // (previous router, via link index)

        while let Some(current) = queue.pop_front() {
            if current == dst {
                // Reconstruct path from visited
                let mut path_rev = Vec::new();
                let mut cur = current;
                while let Some((prev, link_index)) = visited.get(&cur) {
                    if let Some(li) = link_index {
                        path_rev.push(*li);
                        cur = prev.clone().unwrap();
                    } else {
                        break;
                    }
                }
                path_rev.reverse();
                return Some(path_rev);
            }
            if let Some(neighbors) = self.adj.get(&current) {
                for (neighbor, li) in neighbors {
                    if !visited.contains_key(neighbor) {
                        visited.insert(neighbor.clone(), (Some(current.clone()), Some(*li)));
                        queue.push_back(neighbor.clone());
                    }
                }
            }
        }
        None
    }
}