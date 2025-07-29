class OptimalRoutePlanner {
  /**
   * Finds the optimal route for transporting a product between distribution centers.
   * @param {object} network The distribution center network.
   * @param {string} source The ID of the source distribution center.
   * @param {string} destination The ID of the destination distribution center.
   * @param {string} product The type of product to be transported.
   * @param {number} quantity The amount of the product to be transported.
   * @returns {object | null} An object containing the route and cost, or null if no route is found.
   */
  findOptimalRoute(network, source, destination, product, quantity) {
    // Validate that the source and destination centers exist.
    if (!network.centers[source] || !network.centers[destination]) {
      return null;
    }
    // Check if the source center supports the product.
    if (!network.centers[source].products.includes(product)) {
      return null;
    }
    // Check if the destination center supports the product.
    if (!network.centers[destination].products.includes(product)) {
      return null;
    }
    // Check that the source has enough inventory to send.
    const sourceInventory = network.initialInventory && network.initialInventory[source]
      ? network.initialInventory[source][product] || 0
      : 0;
    if (sourceInventory < quantity) {
      return null;
    }
    
    // Function to check if a center can receive the additional quantity while respecting its capacity.
    const canReceive = (centerId) => {
      // Source center will not receive additional product.
      if (centerId === source) return true;
      const center = network.centers[centerId];
      const inv = network.initialInventory && network.initialInventory[centerId]
        ? network.initialInventory[centerId][product] || 0
        : 0;
      return (inv + quantity) <= center.capacity;
    };

    // Initialize Dijkstra's algorithm structures.
    const dist = {};
    const prev = {};
    const centers = Object.keys(network.centers);
    for (const c of centers) {
      dist[c] = Infinity;
      prev[c] = null;
    }
    dist[source] = 0;
    
    const unvisited = new Set(centers);
    
    while (unvisited.size > 0) {
      // Select the unvisited node with the smallest distance.
      let current = null;
      let currentDist = Infinity;
      for (const node of unvisited) {
        if (dist[node] < currentDist) {
          current = node;
          currentDist = dist[node];
        }
      }
      if (current === null) {
        break;
      }
      unvisited.delete(current);
      
      // Early exit if destination is reached.
      if (current === destination) {
        break;
      }
      
      const currentCenter = network.centers[current];
      // Explore neighbors from the current center.
      for (const neighbor in currentCenter.transportCosts) {
        if (!network.centers[neighbor]) continue;
        // Ensure the neighbor supports the product.
        if (!network.centers[neighbor].products.includes(product)) continue;
        // Respect capacity constraints of the neighbor.
        if (!canReceive(neighbor)) continue;
        const costObj = currentCenter.transportCosts[neighbor];
        if (costObj === undefined || costObj[product] === undefined) continue;
        const edgeCost = costObj[product];
        const alt = dist[current] + edgeCost;
        if (alt < dist[neighbor]) {
          dist[neighbor] = alt;
          prev[neighbor] = current;
        }
      }
    }
    
    // If no route is found, return null.
    if (dist[destination] === Infinity) {
      return null;
    }
    
    // Reconstruct the optimal route.
    const path = [];
    let node = destination;
    while (node !== null) {
      path.unshift(node);
      node = prev[node];
    }
    
    return {
      route: path,
      cost: dist[destination]
    };
  }
}

module.exports = { OptimalRoutePlanner };