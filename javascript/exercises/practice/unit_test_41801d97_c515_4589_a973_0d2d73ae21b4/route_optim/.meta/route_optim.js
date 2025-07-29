function computeRoutes(nodes, edges, orders) {
  const graph = buildGraph(nodes, edges);
  const routes = [];

  orders.forEach(order => {
    const { orderId, locationId, startTime, endTime } = order;
    // Compute shortest route from depot (0) to destination.
    const forward = dijkstra(graph, 0, locationId);
    // Compute shortest route from destination back to depot (0).
    const reverse = dijkstra(graph, locationId, 0);

    if (forward.cost === Infinity || reverse.cost === Infinity) {
      throw new Error(`Delivery order ${orderId} cannot be fulfilled`);
    }

    const totalCongestion = forward.cost + reverse.cost;
    // Check if the route can be completed within the delivery's endTime.
    if (totalCongestion > endTime) {
      throw new Error(`Delivery order ${orderId} cannot be fulfilled within its time window`);
    }

    // If the forward journey is completed earlier than startTime, we assume waiting is allowed without extra cost.
    // Construct the final route: combine forward route and reverse route without duplicating the destination.
    const route = forward.path.concat(reverse.path.slice(1));

    routes.push({
      orderId: orderId,
      route: route,
      totalCongestion: totalCongestion
    });
  });

  return routes;
}

function buildGraph(nodes, edges) {
  const graph = new Map();
  nodes.forEach(node => {
    graph.set(node, []);
  });
  edges.forEach(edge => {
    if (graph.has(edge.from)) {
      graph.get(edge.from).push({ to: edge.to, weight: edge.congestion });
    }
  });
  return graph;
}

function dijkstra(graph, start, target) {
  const distances = new Map();
  const previous = new Map();
  const remainingNodes = new Set();

  // Initialization: set all distances to Infinity.
  graph.forEach((_, node) => {
    distances.set(node, Infinity);
    remainingNodes.add(node);
  });
  distances.set(start, 0);

  while (remainingNodes.size > 0) {
    // Find the node in remainingNodes with the smallest distance.
    let minNode = null;
    remainingNodes.forEach(node => {
      if (minNode === null || distances.get(node) < distances.get(minNode)) {
        minNode = node;
      }
    });

    if (minNode === null || distances.get(minNode) === Infinity) {
      break;
    }

    remainingNodes.delete(minNode);

    // If we've reached the target, no need to continue.
    if (minNode === target) {
      break;
    }

    const neighbors = graph.get(minNode);
    neighbors.forEach(neighbor => {
      const alt = distances.get(minNode) + neighbor.weight;
      if (alt < distances.get(neighbor.to)) {
        distances.set(neighbor.to, alt);
        previous.set(neighbor.to, minNode);
      }
    });
  }

  // Reconstruct the path from start to target.
  const path = [];
  let current = target;
  if (distances.get(current) === Infinity) {
    return { cost: Infinity, path: [] };
  }
  while (current !== undefined) {
    path.unshift(current);
    current = previous.get(current);
  }
  return { cost: distances.get(target), path: path };
}

module.exports = { computeRoutes };