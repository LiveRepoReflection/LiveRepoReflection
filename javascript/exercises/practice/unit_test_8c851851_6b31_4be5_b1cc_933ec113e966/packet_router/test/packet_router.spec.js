const { routePackets } = require('../src/packet_router');

describe("Packet Router Routing", () => {
  test("should route packets successfully when valid paths exist", () => {
    const network = {
      1: [{ destination: 2, bandwidth: 10 }, { destination: 3, bandwidth: 5 }],
      2: [{ destination: 4, bandwidth: 8 }],
      3: [{ destination: 4, bandwidth: 12 }]
    };

    const routerCapacities = {
      1: 20,
      2: 15,
      3: 25,
      4: 30
    };

    const requests = [
      { source: 1, destination: 4, dataSize: 50 },
      { source: 2, destination: 4, dataSize: 30 },
      { source: 1, destination: 2, dataSize: 20 }
    ];

    const results = routePackets(network, routerCapacities, requests);

    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBe(requests.length);

    results.forEach((result, index) => {
      expect(result).toHaveProperty("source", requests[index].source);
      expect(result).toHaveProperty("destination", requests[index].destination);
      expect(result).toHaveProperty("dataSize", requests[index].dataSize);
      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("latency");
      if (result.success) {
        expect(typeof result.latency).toBe("number");
        expect(result.latency).toBeGreaterThan(0);
      } else {
        expect(result.latency).toBeNull();
      }
    });
  });

  test("should fail routing when no available path exists", () => {
    const network = {
      1: [{ destination: 2, bandwidth: 10 }],
      2: [] // No outgoing connection from node 2.
    };

    const routerCapacities = {
      1: 15,
      2: 10,
      3: 20
    };

    const requests = [
      { source: 1, destination: 3, dataSize: 10 }
    ];

    const results = routePackets(network, routerCapacities, requests);
    expect(results.length).toBe(1);
    const result = results[0];
    expect(result.source).toBe(1);
    expect(result.destination).toBe(3);
    expect(result.dataSize).toBe(10);
    expect(result.success).toBe(false);
    expect(result.latency).toBeNull();
  });

  test("should fail routing when router capacity is insufficient for the data size", () => {
    const network = {
      1: [{ destination: 2, bandwidth: 100 }],
      2: [{ destination: 3, bandwidth: 100 }]
    };

    const routerCapacities = {
      1: 10,  // Insufficient capacity
      2: 5,
      3: 20
    };

    const requests = [
      { source: 1, destination: 3, dataSize: 50 }
    ];

    const results = routePackets(network, routerCapacities, requests);
    expect(results.length).toBe(1);
    const result = results[0];
    expect(result.success).toBe(false);
    expect(result.latency).toBeNull();
  });

  test("should handle multiple concurrent requests respecting shared capacities", () => {
    const network = {
      1: [{ destination: 2, bandwidth: 50 }],
      2: [{ destination: 3, bandwidth: 50 }]
    };

    const routerCapacities = {
      1: 50,
      2: 50,
      3: 50
    };

    // Two requests from the same source to the same destination that together exceed capacity.
    const requests = [
      { source: 1, destination: 3, dataSize: 30 },
      { source: 1, destination: 3, dataSize: 30 }
    ];

    const results = routePackets(network, routerCapacities, requests);
    expect(results.length).toBe(2);

    // Expect one or both to fail as there is not enough capacity to handle both concurrently.
    const successCount = results.filter(r => r.success).length;
    // It is acceptable for one request to succeed and the other to fail,
    // or both to fail if capacity management chooses to not overcommit.
    expect(successCount).toBeLessThanOrEqual(1);

    results.forEach(result => {
      if (result.success) {
        expect(typeof result.latency).toBe("number");
        expect(result.latency).toBeGreaterThan(0);
      } else {
        expect(result.latency).toBeNull();
      }
    });
  });

  test("should return correct output format for mixed results", () => {
    const network = {
      1: [{ destination: 2, bandwidth: 20 }, { destination: 3, bandwidth: 15 }],
      2: [{ destination: 4, bandwidth: 10 }],
      3: [{ destination: 4, bandwidth: 15 }]
    };

    const routerCapacities = {
      1: 30,
      2: 20,
      3: 20,
      4: 25
    };

    const requests = [
      { source: 1, destination: 4, dataSize: 25 },
      { source: 1, destination: 4, dataSize: 40 }, // Possibly exceeds capacities.
      { source: 2, destination: 4, dataSize: 15 },
      { source: 3, destination: 1, dataSize: 10 }  // Likely no valid route.
    ];

    const results = routePackets(network, routerCapacities, requests);
    expect(results.length).toBe(4);
    results.forEach((result, idx) => {
      expect(result.source).toBe(requests[idx].source);
      expect(result.destination).toBe(requests[idx].destination);
      expect(result.dataSize).toBe(requests[idx].dataSize);
      expect(typeof result.success).toBe("boolean");
      if (result.success) {
        expect(typeof result.latency).toBe("number");
        expect(result.latency).toBeGreaterThan(0);
      } else {
        expect(result.latency).toBeNull();
      }
    });
  });
});