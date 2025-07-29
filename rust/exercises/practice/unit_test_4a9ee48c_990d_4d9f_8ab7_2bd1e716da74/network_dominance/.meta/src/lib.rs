use std::collections::{BTreeSet, HashMap, HashSet};

pub fn find_dominant_users(n: usize, edges: Vec<(usize, usize)>, k: usize) -> Vec<usize> {
    // Build graph as adjacency list, avoiding duplicate edges.
    let mut graph: Vec<Vec<usize>> = vec![Vec::new(); n];
    {
        let mut added = HashSet::new();
        for (u, v) in edges.into_iter() {
            if u < n && v < n && added.insert((u, v)) {
                graph[u].push(v);
            }
        }
    }

    // Tarjan's algorithm to find strongly connected components (SCCs).
    let mut index = 0;
    let mut indices = vec![None; n];
    let mut lowlink = vec![0; n];
    let mut on_stack = vec![false; n];
    let mut stack: Vec<usize> = Vec::new();
    let mut comp_id = vec![0; n]; // component id for each node
    let mut sccs: Vec<Vec<usize>> = Vec::new();

    fn strongconnect(
        v: usize,
        index: &mut usize,
        indices: &mut [Option<usize>],
        lowlink: &mut [usize],
        stack: &mut Vec<usize>,
        on_stack: &mut [bool],
        graph: &Vec<Vec<usize>>,
        sccs: &mut Vec<Vec<usize>>,
        comp_id: &mut [usize],
    ) {
        indices[v] = Some(*index);
        lowlink[v] = *index;
        *index += 1;
        stack.push(v);
        on_stack[v] = true;

        for &w in &graph[v] {
            if indices[w].is_none() {
                strongconnect(w, index, indices, lowlink, stack, on_stack, graph, sccs, comp_id);
                lowlink[v] = std::cmp::min(lowlink[v], lowlink[w]);
            } else if on_stack[w] {
                lowlink[v] = std::cmp::min(lowlink[v], indices[w].unwrap());
            }
        }

        if lowlink[v] == indices[v].unwrap() {
            let mut component = Vec::new();
            loop {
                let w = stack.pop().unwrap();
                on_stack[w] = false;
                component.push(w);
                comp_id[w] = sccs.len();
                if w == v {
                    break;
                }
            }
            sccs.push(component);
        }
    }

    for v in 0..n {
        if indices[v].is_none() {
            strongconnect(v, &mut index, &mut indices, &mut lowlink, &mut stack, &mut on_stack, &graph, &mut sccs, &mut comp_id);
        }
    }

    // Build size vector for each component.
    let num_comps = sccs.len();
    let mut comp_size = vec![0; num_comps];
    for (comp_idx, comp) in sccs.iter().enumerate() {
        comp_size[comp_idx] = comp.len();
    }

    // Build condensed graph for the SCCs.
    let mut condensed: Vec<BTreeSet<usize>> = vec![BTreeSet::new(); num_comps];
    for u in 0..n {
        for &v in &graph[u] {
            let cu = comp_id[u];
            let cv = comp_id[v];
            if cu != cv {
                condensed[cu].insert(cv);
            }
        }
    }

    // Compute for each component the union of reachable components (including itself) using memoization.
    let mut memo: Vec<Option<BTreeSet<usize>>> = vec![None; num_comps];
    fn get_reachable_set(
        comp: usize,
        condensed: &Vec<BTreeSet<usize>>,
        memo: &mut Vec<Option<BTreeSet<usize>>>,
    ) -> BTreeSet<usize> {
        if let Some(cached) = &memo[comp] {
            return cached.clone();
        }
        let mut reach = BTreeSet::new();
        reach.insert(comp);
        for &child in &condensed[comp] {
            let child_reach = get_reachable_set(child, condensed, memo);
            reach = reach.union(&child_reach).cloned().collect();
        }
        memo[comp] = Some(reach.clone());
        reach
    }

    // Compute reachable count for each component.
    let mut comp_reach_count = vec![0; num_comps];
    for comp in 0..num_comps {
        let reach_set = get_reachable_set(comp, &condensed, &mut memo);
        let mut count = 0;
        for &rcomp in reach_set.iter() {
            count += comp_size[rcomp];
        }
        comp_reach_count[comp] = count;
    }

    // For each node, check if its component's reachable count >= k.
    let mut result = Vec::new();
    for v in 0..n {
        if comp_reach_count[comp_id[v]] >= k {
            result.push(v);
        }
    }
    result.sort();
    result
}