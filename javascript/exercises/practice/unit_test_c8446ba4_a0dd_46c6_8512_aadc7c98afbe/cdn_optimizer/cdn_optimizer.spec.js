const { optimizeNetworkDeployment } = require('./cdn_optimizer');

describe('optimizeNetworkDeployment', () => {
  const validateSolution = (input, solution) => {
    // Check for null solution possibility
    if (solution === null) {
      // Then the total available capacity must be insufficient
      const totalCapacity = input.servers.reduce((sum, s) => sum + s.capacity, 0);
      const totalDemand = input.clients.reduce((sum, c) => sum + c.demand, 0);
      expect(totalCapacity).toBeLessThan(totalDemand);
      return;
    }
    
    const { deployedServers, clientAssignments, totalCost } = solution;

    // Validate that each client has an assignment and total demand is met exactly.
    input.clients.forEach(client => {
      expect(clientAssignments).toHaveProperty(client.id);
      const assignments = clientAssignments[client.id];
      let totalAssigned = 0;
      Object.entries(assignments).forEach(([serverId, allocated]) => {
        // Check that this server is in the latency matrix for that client.
        expect(input.latencyMatrix[client.id]).toHaveProperty(serverId);
        // Assigned amount should be non-negative.
        expect(allocated).toBeGreaterThanOrEqual(0);
        totalAssigned += allocated;
      });
      // Allow floating point tolerance.
      expect(totalAssigned).toBeCloseTo(client.demand, 5);
    });

    // Validate capacity constraint for each deployed server.
    const serverUtilization = {};
    deployedServers.forEach(sid => { serverUtilization[sid] = 0; });
    input.clients.forEach(client => {
      for (const [serverId, allocated] of Object.entries(clientAssignments[client.id])) {
        if (deployedServers.includes(serverId)) {
          serverUtilization[serverId] += allocated;
        }
      }
    });
    input.servers.forEach(server => {
      if (deployedServers.includes(server.id)) {
        expect(serverUtilization[server.id]).toBeLessThanOrEqual(server.capacity + 1e-5);
      }
    });

    // Verify that each assignment is only made to allowed servers based on latency matrix.
    input.clients.forEach(client => {
      Object.keys(clientAssignments[client.id]).forEach(serverId => {
        expect(input.latencyMatrix[client.id]).toHaveProperty(serverId);
      });
    });

    // Calculate expected total cost from deployment and latency parts.
    let calcDeployCost = 0;
    deployedServers.forEach(serverId => {
      const server = input.servers.find(s => s.id === serverId);
      calcDeployCost += server.deployCost;
    });
    
    let calcLatencyCost = 0;
    input.clients.forEach(client => {
      const assignments = clientAssignments[client.id];
      Object.entries(assignments).forEach(([serverId, allocated]) => {
        const latency = input.latencyMatrix[client.id][serverId];
        calcLatencyCost += latency * allocated;
      });
    });
    const calcTotalCost = calcDeployCost + calcLatencyCost;
    expect(totalCost).toBeCloseTo(calcTotalCost, 5);
  };

  test('Simple feasible scenario with two servers and two clients', () => {
    const input = {
      servers: [
        { id: 'server1', capacity: 100, deployCost: 50, location: { x: 0, y: 0 } },
        { id: 'server2', capacity: 150, deployCost: 75, location: { x: 1, y: 1 } }
      ],
      clients: [
        { id: 'client1', demand: 80, location: { x: 0, y: 1 } },
        { id: 'client2', demand: 70, location: { x: 1, y: 0 } }
      ],
      latencyMatrix: {
        client1: { server1: 2, server2: 1 },
        client2: { server1: 1, server2: 3 }
      }
    };

    const solution = optimizeNetworkDeployment(input);
    validateSolution(input, solution);
  });

  test('Scenario requiring split assignments among multiple servers', () => {
    const input = {
      servers: [
        { id: 'A', capacity: 50, deployCost: 40, location: { x: 0, y: 0 } },
        { id: 'B', capacity: 70, deployCost: 60, location: { x: 2, y: 2 } },
        { id: 'C', capacity: 100, deployCost: 90, location: { x: 5, y: 5 } }
      ],
      clients: [
        { id: 'X', demand: 60, location: { x: 1, y: 1 } },
        { id: 'Y', demand: 80, location: { x: 3, y: 3 } }
      ],
      latencyMatrix: {
        X: { A: 3, B: 2, C: 5 },
        Y: { A: 6, B: 2, C: 1 }
      }
    };

    const solution = optimizeNetworkDeployment(input);
    validateSolution(input, solution);
  });

  test('Edge case: Insufficient server capacity returns null', () => {
    const input = {
      servers: [
        { id: 's1', capacity: 30, deployCost: 20, location: { x: 0, y: 0 } },
        { id: 's2', capacity: 40, deployCost: 30, location: { x: 1, y: 1 } }
      ],
      clients: [
        { id: 'c1', demand: 50, location: { x: 2, y: 2 } },
        { id: 'c2', demand: 40, location: { x: 3, y: 3 } }
      ],
      latencyMatrix: {
        c1: { s1: 1, s2: 2 },
        c2: { s1: 2, s2: 1 }
      }
    };

    const solution = optimizeNetworkDeployment(input);
    expect(solution).toBeNull();
  });

  test('Complex scenario with multiple servers and clients', () => {
    const input = {
      servers: [
        { id: 'S1', capacity: 120, deployCost: 100, location: { x: 0, y: 0 } },
        { id: 'S2', capacity: 80, deployCost: 70, location: { x: 4, y: 4 } },
        { id: 'S3', capacity: 150, deployCost: 90, location: { x: 8, y: 8 } },
        { id: 'S4', capacity: 90, deployCost: 60, location: { x: 2, y: 6 } }
      ],
      clients: [
        { id: 'C1', demand: 60, location: { x: 1, y: 1 } },
        { id: 'C2', demand: 90, location: { x: 3, y: 3 } },
        { id: 'C3', demand: 70, location: { x: 5, y: 5 } },
        { id: 'C4', demand: 80, location: { x: 7, y: 7 } }
      ],
      latencyMatrix: {
        C1: { S1: 2, S2: 4, S3: 7, S4: 3 },
        C2: { S1: 3, S2: 2, S3: 6, S4: 4 },
        C3: { S1: 5, S2: 3, S3: 2, S4: 3 },
        C4: { S1: 8, S2: 4, S3: 1, S4: 5 }
      }
    };

    const solution = optimizeNetworkDeployment(input);
    validateSolution(input, solution);
  });
});