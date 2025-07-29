use std::cmp;
use std::rc::Rc;

#[derive(Debug)]
struct Node {
    sum: i32,
    min: i32,
    left: Option<Rc<Node>>,
    right: Option<Rc<Node>>,
}

fn build(arr: &[i32], l: usize, r: usize) -> Rc<Node> {
    if l == r {
        Rc::new(Node {
            sum: arr[l],
            min: arr[l],
            left: None,
            right: None,
        })
    } else {
        let mid = (l + r) / 2;
        let left_node = build(arr, l, mid);
        let right_node = build(arr, mid + 1, r);
        Rc::new(Node {
            sum: left_node.sum + right_node.sum,
            min: cmp::min(left_node.min, right_node.min),
            left: Some(left_node),
            right: Some(right_node),
        })
    }
}

fn update_tree(old: &Rc<Node>, l: usize, r: usize, pos: usize, value: i32) -> Rc<Node> {
    if l == r {
        Rc::new(Node {
            sum: value,
            min: value,
            left: None,
            right: None,
        })
    } else {
        let mid = (l + r) / 2;
        let (new_left, new_right);
        if pos <= mid {
            let left_child = old.left.as_ref().expect("Left child must exist");
            new_left = Some(update_tree(left_child, l, mid, pos, value));
            new_right = old.right.clone();
        } else {
            let right_child = old.right.as_ref().expect("Right child must exist");
            new_left = old.left.clone();
            new_right = Some(update_tree(right_child, mid + 1, r, pos, value));
        }
        let left_sum = new_left.as_ref().map_or(0, |node| node.sum);
        let right_sum = new_right.as_ref().map_or(0, |node| node.sum);
        let left_min = new_left.as_ref().map_or(i32::MAX, |node| node.min);
        let right_min = new_right.as_ref().map_or(i32::MAX, |node| node.min);
        Rc::new(Node {
            sum: left_sum + right_sum,
            min: cmp::min(left_min, right_min),
            left: new_left,
            right: new_right,
        })
    }
}

fn query_sum(node: &Rc<Node>, l: usize, r: usize, ql: usize, qr: usize) -> i32 {
    if ql > r || qr < l {
        0
    } else if ql <= l && r <= qr {
        node.sum
    } else {
        let mid = (l + r) / 2;
        let sum_left = if let Some(ref left_node) = node.left {
            query_sum(left_node, l, mid, ql, qr)
        } else {
            0
        };
        let sum_right = if let Some(ref right_node) = node.right {
            query_sum(right_node, mid + 1, r, ql, qr)
        } else {
            0
        };
        sum_left + sum_right
    }
}

fn query_min(node: &Rc<Node>, l: usize, r: usize, ql: usize, qr: usize) -> i32 {
    if ql > r || qr < l {
        i32::MAX
    } else if ql <= l && r <= qr {
        node.min
    } else {
        let mid = (l + r) / 2;
        let min_left = if let Some(ref left_node) = node.left {
            query_min(left_node, l, mid, ql, qr)
        } else {
            i32::MAX
        };
        let min_right = if let Some(ref right_node) = node.right {
            query_min(right_node, mid + 1, r, ql, qr)
        } else {
            i32::MAX
        };
        cmp::min(min_left, min_right)
    }
}

fn dump_tree(node: &Rc<Node>, l: usize, r: usize, arr: &mut Vec<i32>) {
    if l == r {
        arr.push(node.sum);
    } else {
        let mid = (l + r) / 2;
        if let Some(ref left_node) = node.left {
            dump_tree(left_node, l, mid, arr);
        }
        if let Some(ref right_node) = node.right {
            dump_tree(right_node, mid + 1, r, arr);
        }
    }
}

/// Persistent range query tree supporting range sum and range minimum queries.
/// The tree is persistent. Each update creates a new version.
pub struct RangeQueryTree {
    n: usize,
    versions: Vec<Rc<Node>>,
}

impl RangeQueryTree {
    /// Constructs a new RangeQueryTree from an initial array.
    /// Panics if the array is empty.
    pub fn new(arr: Vec<i32>) -> Self {
        if arr.is_empty() {
            panic!("Initial array cannot be empty");
        }
        let n = arr.len();
        let root = build(&arr, 0, n - 1);
        RangeQueryTree {
            n,
            versions: vec![root],
        }
    }

    /// Creates a new version of the tree by updating the element at 'index' to 'value'
    /// based on the provided version.
    /// Returns the new version number.
    pub fn update(&mut self, version: usize, index: usize, value: i32) -> usize {
        if version >= self.versions.len() || index >= self.n {
            panic!("Invalid version or index");
        }
        let old_root = &self.versions[version];
        let new_root = update_tree(old_root, 0, self.n - 1, index, value);
        self.versions.push(new_root);
        self.versions.len() - 1
    }

    /// Returns the sum of the elements in the range [left, right] in the given version.
    /// Returns None if the version is invalid.
    pub fn range_sum(&self, version: usize, left: usize, right: usize) -> Option<i32> {
        if version >= self.versions.len() || left > right || right >= self.n {
            return None;
        }
        let root = &self.versions[version];
        Some(query_sum(root, 0, self.n - 1, left, right))
    }

    /// Returns the minimum value among the elements in the range [left, right] in the given version.
    /// Returns None if the version is invalid.
    pub fn range_min(&self, version: usize, left: usize, right: usize) -> Option<i32> {
        if version >= self.versions.len() || left > right || right >= self.n {
            return None;
        }
        let root = &self.versions[version];
        Some(query_min(root, 0, self.n - 1, left, right))
    }

    /// Returns the array for the specified version.
    /// Returns None if the version is invalid.
    pub fn query_version(&self, version: usize) -> Option<Vec<i32>> {
        if version >= self.versions.len() {
            return None;
        }
        let root = &self.versions[version];
        let mut arr = Vec::with_capacity(self.n);
        dump_tree(root, 0, self.n - 1, &mut arr);
        Some(arr)
    }
}