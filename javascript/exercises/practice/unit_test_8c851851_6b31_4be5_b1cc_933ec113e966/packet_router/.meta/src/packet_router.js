"use strict";

/*
  This implementation simulates packet routing through a directed network.
  Each packet request is processed in the given order. For each request, 
  we use a modified Dijkstra algorithm to find a path from the source router 
  to the destination router that satisfies capacity constraints for both the routers 
  and the links (edges). Once a valid path is found, we update the available capacities 
  to simulate resource reservation.
  
  Latency is computed as the sum of processing delays and transmission delays.
  The processing delay for a router is defined as: dataSize / routerCapacities[router],
  while the transmission delay for an edge is defined as: dataSize / (original bandwidth of the edge).
  Note that capacities are consumed on successful routes.
*/

class PriorityQueue {
  constructor() {
    this.elements = [];
  }

  enqueue(item, priority) {
    this.elements.push({ item, priority });
  }

  dequeue() {
    if (this.isEmpty()) return null;
    let minIndex = 0;
    for (let i = 1; i < this.elements.length; i++) {
      if (this.elements[i].priority < this.elements[minIndex].priority) {
        minIndex = i;
      }
    }
    return this.elements.splice(minIndex, 1)[0];
  }

  isEmpty() {
    return this.elements.length === 0;
  }
}

function routePackets(network, routerCapacities, requests) {
  // Clone the router capacities into mutable available capacities.
  const availableRouters = {};
  for (const router in routerCapacities) {
    availableRouters[router] = routerCapacities[router];
  }

  // Build availableEdges which is a deep copy with an "available" property.
  // The original bandwidth is kept in property "bandwidth".
  const availableEdges = {};
  for (const u in network) {
    availableEdges[u] = [];
    network[u].forEach(conn => {
      availableEdges[u].push({
        destination: conn.destination,
        available: conn.bandwidth,
        bandwidth: conn.bandwidth
      });
    });
  }

  const results = [];

  // Process each request sequentially.
  for (const req of requests) {
    const { source, destination, dataSize } = req;
    
    // Check if source router has sufficient capacity.
    if (!availableRouters.hasOwnProperty(source) || availableRouters[source] < dataSize) {
      results.push({
        source,
        destination,
        dataSize,
        success: false,
        latency: null
      });
      continue;
    }
    
    // Modified Dijkstra's algorithm to find the lowest latency path.
    // We'll compute cumulative cost (latency) for reaching each router.
    const dist = {};
    const prev = {};
    const visited = {};

    // Initialize distances
    for (const router in availableRouters) {
      dist[router] = Infinity;
      prev[router] = null;
      visited[router] = false;
    }
    // Starting cost: processing delay at source.
    dist[source] = dataSize / routerCapacities[source];

    const pq = new PriorityQueue();
    pq.enqueue(source, dist[source]);

    while (!pq.isEmpty()) {
      const { item: current } = pq.dequeue();
      if (visited[current]) continue;
      visited[current] = true;

      // If we reached our destination, break.
      if (parseInt(current) === parseInt(destination)) break;

      // For current node, explore outgoing edges
      if (availableEdges.hasOwnProperty(current)) {
        for (const edge of availableEdges[current]) {
          const next = edge.destination;
          // Check for router capacity at the destination node.
          if (!availableRouters.hasOwnProperty(next) || availableRouters[next] < dataSize) continue;
          // Check if the edge has enough available bandwidth.
          if (edge.available < dataSize) continue;
          // Compute cost to traverse the edge.
          // Transmission delay over edge plus processing delay at next router.
          const transmissionDelay = dataSize / edge.bandwidth;
          const processingDelay = dataSize / routerCapacities[next];
          const newCost = dist[current] + transmissionDelay + processingDelay;

          if (newCost < dist[next]) {
            dist[next] = newCost;
            prev[next] = current;
            pq.enqueue(next, newCost);
          }
        }
      }
    }

    // If destination is unreachable or cost is Infinity, request fails.
    if (dist[destination] === Infinity) {
      results.push({
        source,
        destination,
        dataSize,
        success: false,
        latency: null
      });
    } else {
      // Reconstruct path from source to destination.
      const path = [];
      let curr = destination;
      while (curr !== null) {
        path.push(curr);
        curr = prev[curr];
      }
      path.reverse();

      // Update available routers along the path.
      let capacitySufficient = true;
      for (const router of path) {
        if (availableRouters[router] < dataSize) {
          capacitySufficient = false;
          break;
        }
      }
      if (!capacitySufficient) {
        results.push({
          source,
          destination,
          dataSize,
          success: false,
          latency: null
        });
        continue;
      }

      // Check and update available edges along the path.
      let edgesSufficient = true;
      for (let i = 0; i < path.length - 1; i++) {
        const u = path[i];
        const v = path[i + 1];
        // Find the edge from u to v.
        const edgeObj = availableEdges[u].find(e => parseInt(e.destination) === parseInt(v));
        if (!edgeObj || edgeObj.available < dataSize) {
          edgesSufficient = false;
          break;
        }
      }
      if (!edgesSufficient) {
        results.push({
          source,
          destination,
          dataSize,
          success: false,
          latency: null
        });
        continue;
      }

      // Reserve capacity: deduct dataSize from each router along the path.
      for (const router of path) {
        availableRouters[router] -= dataSize;
      }
      // Reserve bandwidth on the edges along the path.
      for (let i = 0; i < path.length - 1; i++) {
        const u = path[i];
        const v = path[i + 1];
        const edgeObj = availableEdges[u].find(e => parseInt(e.destination) === parseInt(v));
        edgeObj.available -= dataSize;
      }

      results.push({
        source,
        destination,
        dataSize,
        success: true,
        latency: parseFloat(dist[destination].toFixed(3))
      });
    }
  }

  return results;
}

module.exports = { routePackets };