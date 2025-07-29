/**
 * Partition a network into sub-networks, minimizing the cut bandwidth.
 * 
 * @param {Array<{id: number, securityLevel: number}>} nodes - The nodes of the network.
 * @param {Array<{source: number, target: number, bandwidth: number}>} edges - The edges of the network.
 * @param {number} partitionSize - The maximum size of each sub-network.
 * @param {number} minSecurityLevel - The minimum acceptable security level.
 * @returns {Array<Array<number>> | null} - An array of sub-networks (each sub-network is an array of node ids)
 *                                          or null if it's impossible to satisfy the security constraint.
 */
function partitionNetwork(nodes, edges, partitionSize, minSecurityLevel) {
  // Separate nodes by security level: secure nodes and insecure nodes.
  const secureNodes = nodes.filter(node => node.securityLevel >= minSecurityLevel);
  const insecureNodes = nodes.filter(node => node.securityLevel < minSecurityLevel);

  // Error handling: if no node meets the security requirement, return null.
  if (secureNodes.length === 0) {
    return null;
  }

  // Union-Find (Disjoint Set) implementation.
  const parent = {};
  const size = {};

  // Initialize each secure node as its own group.
  secureNodes.forEach(node => {
    parent[node.id] = node.id;
    size[node.id] = 1;
  });

  function find(x) {
    if (parent[x] !== x) {
      parent[x] = find(parent[x]);
    }
    return parent[x];
  }

  function union(x, y) {
    const rootX = find(x);
    const rootY = find(y);
    if (rootX === rootY) return false;

    // Check if merging groups will exceed partitionSize.
    if (size[rootX] + size[rootY] > partitionSize) {
      return false;
    }
    
    // Union by size.
    if (size[rootX] < size[rootY]) {
      parent[rootX] = rootY;
      size[rootY] += size[rootX];
    } else {
      parent[rootY] = rootX;
      size[rootX] += size[rootY];
    }
    return true;
  }

  // Process edges connecting secure nodes only.
  // Use edges with both endpoints secure.
  const secureEdges = edges.filter(edge => {
    return secureNodes.find(node => node.id === edge.source) &&
           secureNodes.find(node => node.id === edge.target);
  });

  // Sort edges in descending order of bandwidth to preserve high-bandwidth connections.
  secureEdges.sort((a, b) => b.bandwidth - a.bandwidth);

  for (const edge of secureEdges) {
    // Attempt to merge the groups of the two nodes if possible.
    union(edge.source, edge.target);
  }

  // Build groups from the union-find structure for secure nodes.
  const groupsMap = {};
  secureNodes.forEach(node => {
    const root = find(node.id);
    if (!groupsMap[root]) {
      groupsMap[root] = [];
    }
    groupsMap[root].push(node.id);
  });

  // Prepare the result array.
  let result = [];

  // Add secure node groups.
  Object.values(groupsMap).forEach(group => {
    // Sort each group order.
    group.sort((a, b) => a - b);
    result.push(group);
  });

  // Add each insecure node as isolated partition.
  insecureNodes.forEach(node => {
    result.push([node.id]);
  });

  // Sort the overall result by the smallest id in each partition.
  result.sort((a, b) => {
    return Math.min(...a) - Math.min(...b);
  });

  return result;
}

module.exports = partitionNetwork;