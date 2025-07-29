function optimizeNetworkDeployment(input) {
  const { servers, clients, latencyMatrix } = input;

  // Check if the total server capacity is sufficient to satisfy all client demands
  const totalServerCapacity = servers.reduce((sum, s) => sum + s.capacity, 0);
  const totalClientDemand = clients.reduce((sum, c) => sum + c.demand, 0);
  if (totalServerCapacity < totalClientDemand) {
    return null;
  }

  // Create a mapping for servers with their current available capacity and deployment flag
  const serverMap = {};
  servers.forEach(s => {
    serverMap[s.id] = {
      id: s.id,
      capacity: s.capacity,
      deployCost: s.deployCost,
      location: s.location,
      available: s.capacity,
      deployed: false
    };
  });

  // Prepare the clientAssignments object
  const clientAssignments = {};

  // For every client, assign its demand to available servers based on the lowest latency
  for (const client of clients) {
    // Check if the client has any candidate servers in the latency matrix
    const candidateLatencies = latencyMatrix[client.id];
    if (!candidateLatencies) {
      return null;
    }

    // Get a list of candidate server IDs that exist in our serverMap
    const candidateServers = Object.keys(candidateLatencies).filter(sid => serverMap[sid] !== undefined);
    if (candidateServers.length === 0) {
      return null;
    }

    // Sort candidate servers in ascending order based on latency for this client
    candidateServers.sort((a, b) => candidateLatencies[a] - candidateLatencies[b]);

    let remainingDemand = client.demand;
    clientAssignments[client.id] = {};

    for (const sid of candidateServers) {
      if (remainingDemand <= 0) break;
      const server = serverMap[sid];
      if (server.available <= 0) continue;
      const allocation = Math.min(remainingDemand, server.available);
      clientAssignments[client.id][sid] = allocation;
      server.available -= allocation;
      remainingDemand -= allocation;
      if (allocation > 0) {
        server.deployed = true;
      }
    }

    // If the client's demand cannot be fully satisfied, return null
    if (remainingDemand > 1e-5) {
      return null;
    }
  }

  // Collect the list of deployed servers (those that were used for any allocation)
  const deployedServers = [];
  servers.forEach(s => {
    if (serverMap[s.id].deployed) {
      deployedServers.push(s.id);
    }
  });

  // Calculate the total cost consisting of deployment cost and latency cost
  let totalDeployCost = 0;
  deployedServers.forEach(sid => {
    totalDeployCost += serverMap[sid].deployCost;
  });

  let totalLatencyCost = 0;
  clients.forEach(client => {
    const assignments = clientAssignments[client.id];
    for (const sid in assignments) {
      const latency = latencyMatrix[client.id][sid];
      totalLatencyCost += latency * assignments[sid];
    }
  });

  const totalCost = totalDeployCost + totalLatencyCost;

  return {
    deployedServers,
    clientAssignments,
    totalCost
  };
}

module.exports = { optimizeNetworkDeployment };