const { networkOptimize } = require('../network_optimize');

// Helper function to compute the total cost of a path based on the network graph
function computePathCost(path, network) {
  let totalCost = 0;
  for (let i = 0; i < path.length - 1; i++) {
    const from = path[i];
    const to = path[i + 1];
    // Since the graph is undirected, check both directions
    let edge = network[from].find(edge => edge.to === to);
    if (!edge) {
      edge = network[to].find(edge => edge.to === from);
    }
    if (!edge) {
      throw new Error(`Edge not found between ${from} and ${to}`);
    }
    totalCost += edge.cost;
  }
  return totalCost;
}

describe('networkOptimize', () => {
  test('should return direct connections for simple network', () => {
    const network = {
      "data_center": [{ to: "branch1", cost: 5 }],
      "branch1": [{ to: "data_center", cost: 5 }]
    };
    const demands = {
      "branch1": 10
    };
    const maxPaths = 2;
    const result = networkOptimize(network, demands, maxPaths);
    
    expect(result).toHaveProperty("branch1");
    expect(Array.isArray(result.branch1)).toBe(true);
    expect(result.branch1.length).toBeLessThanOrEqual(maxPaths);
    result.branch1.forEach(path => {
      expect(Array.isArray(path)).toBe(true);
      expect(path[0]).toBe("data_center");
      expect(path[path.length - 1]).toBe("branch1");
      const cost = computePathCost(path, network);
      expect(cost).toBe(5);
    });
  });

  test('should handle multiple branch offices with valid paths and sorted costs', () => {
    const network = {
      "data_center": [
        { to: "A", cost: 2 },
        { to: "B", cost: 4 }
      ],
      "A": [
        { to: "data_center", cost: 2 },
        { to: "B", cost: 1 }
      ],
      "B": [
        { to: "data_center", cost: 4 },
        { to: "A", cost: 1 }
      ]
    };
    const demands = {
      "A": 5,
      "B": 7
    };
    const maxPaths = 2;
    const result = networkOptimize(network, demands, maxPaths);
    
    Object.keys(demands).forEach(branch => {
      expect(result).toHaveProperty(branch);
      expect(Array.isArray(result[branch])).toBe(true);
      expect(result[branch].length).toBeLessThanOrEqual(maxPaths);
      result[branch].forEach(path => {
        expect(path[0]).toBe("data_center");
        expect(path[path.length - 1]).toBe(branch);
        const cost = computePathCost(path, network);
        expect(typeof cost).toBe("number");
      });
      const costList = result[branch].map(path => computePathCost(path, network));
      for (let i = 1; i < costList.length; i++) {
        expect(costList[i - 1]).toBeLessThanOrEqual(costList[i]);
      }
    });
  });

  test('should return valid paths on a complex network with intermediate nodes', () => {
    const network = {
      "data_center": [
        { to: "X", cost: 3 },
        { to: "Y", cost: 5 }
      ],
      "X": [
        { to: "data_center", cost: 3 },
        { to: "A", cost: 4 },
        { to: "Y", cost: 2 }
      ],
      "Y": [
        { to: "data_center", cost: 5 },
        { to: "X", cost: 2 },
        { to: "A", cost: 6 }
      ],
      "A": [
        { to: "X", cost: 4 },
        { to: "Y", cost: 6 }
      ]
    };
    const demands = {
      "A": 8
    };
    const maxPaths = 3;
    const result = networkOptimize(network, demands, maxPaths);
    
    expect(result).toHaveProperty("A");
    expect(Array.isArray(result.A)).toBe(true);
    expect(result.A.length).toBeLessThanOrEqual(maxPaths);
    result.A.forEach(path => {
      expect(path[0]).toBe("data_center");
      expect(path[path.length - 1]).toBe("A");
      const cost = computePathCost(path, network);
      expect(cost).toBeGreaterThan(0);
    });
    const costs = result.A.map(path => computePathCost(path, network));
    for (let i = 1; i < costs.length; i++) {
      expect(costs[i - 1]).toBeLessThanOrEqual(costs[i]);
    }
  });

  test('should select multiple alternative paths and sort them by cost', () => {
    const network = {
      "data_center": [
        { to: "A", cost: 10 },
        { to: "B", cost: 3 }
      ],
      "A": [
        { to: "data_center", cost: 10 },
        { to: "B", cost: 1 },
        { to: "C", cost: 2 }
      ],
      "B": [
        { to: "data_center", cost: 3 },
        { to: "A", cost: 1 },
        { to: "C", cost: 4 }
      ],
      "C": [
        { to: "A", cost: 2 },
        { to: "B", cost: 4 },
        { to: "D", cost: 1 }
      ],
      "D": [
        { to: "C", cost: 1 }
      ]
    };
    const demands = {
      "D": 3
    };
    const maxPaths = 2;
    const result = networkOptimize(network, demands, maxPaths);
    
    expect(result).toHaveProperty("D");
    expect(Array.isArray(result.D)).toBe(true);
    expect(result.D.length).toBeLessThanOrEqual(maxPaths);
    result.D.forEach(path => {
      expect(path[0]).toBe("data_center");
      expect(path[path.length - 1]).toBe("D");
      const cost = computePathCost(path, network);
      expect(cost).toBeGreaterThan(0);
    });
    const costSequence = result.D.map(path => computePathCost(path, network));
    for (let i = 1; i < costSequence.length; i++) {
      expect(costSequence[i - 1]).toBeLessThanOrEqual(costSequence[i]);
    }
  });
});