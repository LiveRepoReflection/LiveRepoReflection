const partitionNetwork = require('../network_partition.js');

describe('partitionNetwork', () => {
  test('should return null if no node meets the minimum security requirement', () => {
    const nodes = [
      { id: 1, securityLevel: 1 },
      { id: 2, securityLevel: 2 }
    ];
    const edges = [
      { source: 1, target: 2, bandwidth: 10 }
    ];
    const partitionSize = 2;
    const minSecurityLevel = 5;
    const result = partitionNetwork(nodes, edges, partitionSize, minSecurityLevel);
    expect(result).toBeNull();
  });

  test('should isolate nodes with securityLevel below minSecurityLevel', () => {
    const nodes = [
      { id: 1, securityLevel: 3 },
      { id: 2, securityLevel: 8 },
      { id: 3, securityLevel: 9 }
    ];
    const edges = [
      { source: 1, target: 2, bandwidth: 10 },
      { source: 2, target: 3, bandwidth: 5 }
    ];
    const partitionSize = 3;
    const minSecurityLevel = 5;
    const result = partitionNetwork(nodes, edges, partitionSize, minSecurityLevel);
    
    // Verify that node 1 is isolated because its security level is below minSecurityLevel.
    const insecurePartition = result.find(partition => partition.includes(1));
    expect(insecurePartition).toEqual([1]);

    // Check each partition does not exceed the partitionSize.
    result.forEach(partition => {
      expect(partition.length).toBeLessThanOrEqual(partitionSize);
    });
    
    // Verify that the union of partitions contains exactly all nodes.
    const combinedIds = result.flat().sort((a, b) => a - b);
    const expectedIds = nodes.map(n => n.id).sort((a, b) => a - b);
    expect(combinedIds).toEqual(expectedIds);
  });

  test('should partition nodes respecting the partition size constraint', () => {
    const nodes = [
      { id: 1, securityLevel: 5 },
      { id: 2, securityLevel: 7 },
      { id: 3, securityLevel: 8 },
      { id: 4, securityLevel: 9 },
      { id: 5, securityLevel: 10 }
    ];
    const edges = [
      { source: 1, target: 2, bandwidth: 10 },
      { source: 2, target: 3, bandwidth: 5 },
      { source: 3, target: 4, bandwidth: 7 },
      { source: 4, target: 5, bandwidth: 3 },
      { source: 1, target: 5, bandwidth: 4 }
    ];
    const partitionSize = 2;
    const minSecurityLevel = 5;
    const result = partitionNetwork(nodes, edges, partitionSize, minSecurityLevel);
    
    // Ensure each partition does not exceed the maximum size.
    result.forEach(partition => {
      expect(partition.length).toBeLessThanOrEqual(partitionSize);
    });
    
    // Verify that all nodes are included in the partitions.
    const combinedIds = result.flat().sort((a, b) => a - b);
    const expectedIds = nodes.map(n => n.id).sort((a, b) => a - b);
    expect(combinedIds).toEqual(expectedIds);
  });

  test('should correctly handle disconnected graphs', () => {
    const nodes = [
      { id: 1, securityLevel: 6 },
      { id: 2, securityLevel: 7 },
      { id: 3, securityLevel: 8 },
      { id: 4, securityLevel: 4 }, // Insecure node, should be isolated.
      { id: 5, securityLevel: 9 },
      { id: 6, securityLevel: 10 }
    ];
    const edges = [
      { source: 1, target: 2, bandwidth: 10 },
      { source: 2, target: 3, bandwidth: 5 },
      // node 4 is disconnected due to its security level.
      { source: 5, target: 6, bandwidth: 8 }
    ];
    const partitionSize = 3;
    const minSecurityLevel = 5;
    const result = partitionNetwork(nodes, edges, partitionSize, minSecurityLevel);
    
    // Verify that insecure node 4 is isolated.
    const partitionOf4 = result.find(partition => partition.includes(4));
    expect(partitionOf4).toEqual([4]);

    // Validate each partition's size.
    result.forEach(partition => {
      expect(partition.length).toBeLessThanOrEqual(partitionSize);
    });

    // Check overall node inclusion.
    const combinedIds = result.flat().sort((a, b) => a - b);
    const expectedIds = nodes.map(n => n.id).sort((a, b) => a - b);
    expect(combinedIds).toEqual(expectedIds);
  });

  test('should partition a complex network correctly', () => {
    const nodes = [];
    for (let i = 1; i <= 20; i++) {
      nodes.push({ id: i, securityLevel: (i % 10) + 1 });
    }
    const edges = [];
    // Build a chain for connectivity.
    for (let i = 1; i < 20; i++) {
      edges.push({ source: i, target: i + 1, bandwidth: (i % 5) + 1 });
    }
    // Add additional edges for complexity.
    edges.push({ source: 1, target: 10, bandwidth: 10 });
    edges.push({ source: 5, target: 15, bandwidth: 8 });
    
    const partitionSize = 5;
    const minSecurityLevel = 5;
    const result = partitionNetwork(nodes, edges, partitionSize, minSecurityLevel);
    
    // Validate partition size constraint.
    result.forEach(partition => {
      expect(partition.length).toBeLessThanOrEqual(partitionSize);
    });
    
    // Ensure that any node with security level lower than minSecurityLevel is isolated.
    nodes.forEach(node => {
      if (node.securityLevel < minSecurityLevel) {
        const partitionsContainingNode = result.filter(partition => partition.includes(node.id));
        expect(partitionsContainingNode.length).toBe(1);
        expect(partitionsContainingNode[0]).toEqual([node.id]);
      }
    });
    
    // Verify that all nodes appear in the final partitioning.
    const combinedIds = result.flat().sort((a, b) => a - b);
    const expectedIds = nodes.map(n => n.id).sort((a, b) => a - b);
    expect(combinedIds).toEqual(expectedIds);
  });
});