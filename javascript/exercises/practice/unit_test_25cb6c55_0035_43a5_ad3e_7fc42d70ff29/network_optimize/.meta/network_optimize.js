function networkOptimize(network, demands, maxPaths) {
  const result = {};
  // For each branch office in demands, compute up to maxPaths shortest paths from "data_center"
  for (const branch of Object.keys(demands)) {
    const paths = yenKShortestPaths(network, "data_center", branch, maxPaths);
    result[branch] = paths;
  }
  return result;
}

// Helper: Compute cost of a given path based on the network graph
function computePathCost(path, network) {
  let totalCost = 0;
  for (let i = 0; i < path.length - 1; i++) {
    const from = path[i];
    const to = path[i + 1];
    // Find edge from 'from' to 'to'
    const edge = network[from].find(edge => edge.to === to);
    if (!edge) {
      throw new Error(`Edge not found between ${from} and ${to}`);
    }
    totalCost += edge.cost;
  }
  return totalCost;
}

// Dijkstra's algorithm with bannedEdges and bannedNodes support.
// bannedEdges: Set of strings "from->to" that must be skipped.
// bannedNodes: Set of node names that should not be visited (except for the source).
function dijkstra(network, source, target, bannedEdges = new Set(), bannedNodes = new Set()) {
  const distances = {};
  const previous = {};
  const visited = new Set();
  const queue = [];
  
  // Initialize distances
  for (const node in network) {
    distances[node] = Infinity;
  }
  distances[source] = 0;
  queue.push({ node: source, cost: 0 });
  
  while (queue.length > 0) {
    // Get the node in the queue with the minimal cost
    queue.sort((a, b) => a.cost - b.cost);
    const { node: current, cost: currentCost } = queue.shift();
    
    if (visited.has(current)) continue;
    visited.add(current);
    
    // If current is target, reconstruct path
    if (current === target) {
      const path = [];
      let temp = current;
      while (temp !== undefined) {
        path.unshift(temp);
        temp = previous[temp];
      }
      return { path, cost: distances[current] };
    }
    
    // Skip banned nodes (except source, and we allow spur node even if bannedNodes contains it since that is handled in yen algorithm)
    if (current !== source && bannedNodes.has(current)) {
      continue;
    }
    
    // Explore neighbors
    for (const edge of network[current]) {
      const neighbor = edge.to;
      // Check if this edge is banned
      if (bannedEdges.has(`${current}->${neighbor}`)) {
        continue;
      }
      // Check if neighbor is banned (skip neighbor if it is banned)
      if (bannedNodes.has(neighbor)) {
        continue;
      }
      const newCost = currentCost + edge.cost;
      if (newCost < distances[neighbor]) {
        distances[neighbor] = newCost;
        previous[neighbor] = current;
        queue.push({ node: neighbor, cost: newCost });
      }
    }
  }
  
  return null;
}

// Yen's algorithm for k-shortest simple paths
function yenKShortestPaths(network, source, target, K) {
  const A = [];
  const B = [];
  
  // Get the first shortest path
  const firstPathResult = dijkstra(network, source, target);
  if (!firstPathResult) {
    return A;
  }
  A.push(firstPathResult);
  
  for (let k = 1; k < K; k++) {
    const previousPath = A[k - 1].path;
    for (let i = 0; i < previousPath.length - 1; i++) {
      const spurNode = previousPath[i];
      const rootPath = previousPath.slice(0, i + 1);
      
      // Banned edges and nodes for this spur iteration
      const bannedEdges = new Set();
      const bannedNodes = new Set();
      
      // For each path in A, if its root path matches, ban the next edge
      for (const pathInfo of A) {
        const currPath = pathInfo.path;
        if (arraysEqual(rootPath, currPath.slice(0, i + 1)) && currPath.length > i + 1) {
          bannedEdges.add(`${currPath[i]}->${currPath[i + 1]}`);
        }
      }
      
      // All nodes in rootPath except spurNode are banned to avoid loops
      for (let j = 0; j < rootPath.length - 1; j++) {
        bannedNodes.add(rootPath[j]);
      }
      
      // Find the spur path from spurNode to target with the current restrictions
      const spurResult = dijkstra(network, spurNode, target, bannedEdges, bannedNodes);
      
      if (spurResult) {
        // Combine rootPath and spurResult, avoiding duplicate spurNode in spurResult
        const totalPath = rootPath.concat(spurResult.path.slice(1));
        const totalCost = computePathCost(totalPath, network);
        // Check if candidate already exists in B (by comparing path arrays)
        if (!B.some(candidate => arraysEqual(candidate.path, totalPath))) {
          B.push({ path: totalPath, cost: totalCost });
        }
      }
    }
    
    if (B.length === 0) {
      break;
    }
    
    // Sort B based on cost and add the candidate with smallest cost to A
    B.sort((a, b) => a.cost - b.cost);
    const bestCandidate = B.shift();
    A.push(bestCandidate);
  }
  
  // Return only the list of paths (sorted by cost)
  const resultPaths = A.map(item => item.path);
  return resultPaths;
}

// Helper: Check if two arrays of nodes are equal
function arraysEqual(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;
  for (let i = 0; i < arr1.length; i++) {
    if (arr1[i] !== arr2[i]) return false;
  }
  return true;
}

module.exports = { networkOptimize };