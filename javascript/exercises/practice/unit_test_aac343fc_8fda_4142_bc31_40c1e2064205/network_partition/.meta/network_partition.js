'use strict';

function networkPartition(n, edges, k) {
  if (k === n) return 0;

  // Build an adjacency matrix for direct edge latencies.
  const matrix = new Array(n);
  for (let i = 0; i < n; i++) {
    matrix[i] = new Array(n).fill(Infinity);
    matrix[i][i] = 0;
  }
  let maxEdge = 0;
  for (const [u, v, latency] of edges) {
    matrix[u][v] = latency;
    matrix[v][u] = latency;
    if (latency > maxEdge) maxEdge = latency;
  }

  // The check function: for a given threshold T, determine if it's possible
  // to partition the n nodes into at most k clusters where each cluster is a clique,
  // i.e. every pair of nodes in the cluster has an edge with latency <= T.
  //
  // We build the complement graph where an edge exists between i and j if
  // (i !== j) and (matrix[i][j] > T). Then, a valid clique in the original allowed graph
  // corresponds to an independent set in the complement graph.
  // Partitioning into cliques is equivalent to coloring the complement graph with k colors.
  function canPartition(T) {
    const compGraph = new Array(n);
    for (let i = 0; i < n; i++) {
      compGraph[i] = [];
    }
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        // If there is an allowed edge (latency <= T), then nodes i and j can be in the same clique.
        // Otherwise, add a connection in the complement graph.
        if (matrix[i][j] <= T) {
          // Allowed edge: do nothing.
        } else {
          compGraph[i].push(j);
          compGraph[j].push(i);
        }
      }
    }

    // Order nodes by descending degree in the complement graph for efficient backtracking.
    const order = [];
    for (let i = 0; i < n; i++) {
      order.push(i);
    }
    order.sort((a, b) => compGraph[b].length - compGraph[a].length);

    const colors = new Array(n).fill(-1);

    function backtrack(idx) {
      if (idx === order.length) return true;
      const node = order[idx];
      // Try all possible colors (clusters)
      for (let c = 0; c < k; c++) {
        let canUse = true;
        for (const neighbor of compGraph[node]) {
          if (colors[neighbor] === c) {
            canUse = false;
            break;
          }
        }
        if (canUse) {
          colors[node] = c;
          if (backtrack(idx + 1)) return true;
          colors[node] = -1;
        }
      }
      return false;
    }
    return backtrack(0);
  }

  // Use binary search on T to find the minimal maximum latency.
  let result = -1;
  let low = 0;
  let high = maxEdge;
  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (canPartition(mid)) {
      result = mid;
      high = mid - 1;
    } else {
      low = mid + 1;
    }
  }
  return result;
}

module.exports = { networkPartition };