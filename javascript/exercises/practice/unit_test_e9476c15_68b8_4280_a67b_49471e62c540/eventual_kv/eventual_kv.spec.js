const { Node } = require('./eventual_kv');

describe('Eventual KV Distributed Store - Unit Tests', () => {
  test('Local read and write operations', () => {
    const node = new Node('node1');
    node.put("testKey", "testValue");
    expect(node.get("testKey")).toBe("testValue");
  });

  test('Synchronization propagates writes across nodes', () => {
    const nodeA = new Node('A');
    const nodeB = new Node('B');
    const nodeC = new Node('C');

    // Write on nodeA only.
    nodeA.put("syncKey", "syncValue");

    // Simulate a synchronization round
    nodeA.synchronize([nodeB, nodeC]);
    nodeB.synchronize([nodeA, nodeC]);
    nodeC.synchronize([nodeA, nodeB]);

    expect(nodeB.get("syncKey")).toBe("syncValue");
    expect(nodeC.get("syncKey")).toBe("syncValue");
  });

  test('Conflict resolution using LWW works correctly', () => {
    const nodeA = new Node('A');
    const nodeB = new Node('B');
    
    // Simulate two conflicting writes with explicit timestamps.
    // Lower timestamp on nodeA.
    nodeA.put("conflictKey", "valueA", 100);
    // Higher timestamp on nodeB.
    nodeB.put("conflictKey", "valueB", 101);
    
    // Synchronize nodes in both directions.
    nodeA.synchronize([nodeB]);
    nodeB.synchronize([nodeA]);
    
    expect(nodeA.get("conflictKey")).toBe("valueB");
    expect(nodeB.get("conflictKey")).toBe("valueB");
  });

  test('System handles node failure and recovery', () => {
    const nodeA = new Node('A');
    const nodeB = new Node('B');
    const nodeC = new Node('C');
    
    // Initial write and synchronization.
    nodeA.put("failureKey", "initial");
    nodeA.synchronize([nodeB, nodeC]);
    nodeB.synchronize([nodeA, nodeC]);
    nodeC.synchronize([nodeA, nodeB]);
    
    // Simulate failure: nodeC goes offline.
    nodeC.setOnline(false);
    
    // Update on nodeB while nodeC is offline.
    nodeB.put("failureKey", "updated");
    nodeB.synchronize([nodeA]);
    nodeA.synchronize([nodeB]);
    
    // NodeC remains outdated at this point.
    expect(nodeC.get("failureKey")).toBe("initial");
    
    // Recover nodeC and perform additional synchronization.
    nodeC.setOnline(true);
    nodeA.synchronize([nodeB, nodeC]);
    nodeB.synchronize([nodeA, nodeC]);
    nodeC.synchronize([nodeA, nodeB]);
    
    expect(nodeC.get("failureKey")).toBe("updated");
  });

  test('Multiple nodes eventually converge to a consistent state', () => {
    const nodeCount = 10;
    const nodes = [];
    
    for (let i = 0; i < nodeCount; i++) {
      nodes.push(new Node(`node${i}`));
    }
    
    // Update a common key on one node.
    nodes[0].put("commonKey", "startVal");
    
    // Simulate multiple rounds of full synchronization among all nodes.
    for (let round = 0; round < 5; round++) {
      nodes.forEach((node) => {
        const peers = nodes.filter(n => n !== node);
        node.synchronize(peers);
      });
    }
    
    nodes.forEach((node) => {
      expect(node.get("commonKey")).toBe("startVal");
    });
  });

  test('Multiple concurrent updates on same key eventually converge using LWW', () => {
    const nodeA = new Node('A');
    const nodeB = new Node('B');

    // First update on nodeA.
    nodeA.put("updateKey", "v1", 200);
    // Concurrent update on nodeB with a later timestamp.
    nodeB.put("updateKey", "v2", 201);
    // Another update on nodeA with an even later timestamp.
    nodeA.put("updateKey", "v3", 202);

    // Synchronize between both nodes.
    nodeA.synchronize([nodeB]);
    nodeB.synchronize([nodeA]);

    expect(nodeA.get("updateKey")).toBe("v3");
    expect(nodeB.get("updateKey")).toBe("v3");
  });
});