## Project Name

`ConsistentHashingLoadBalancer`

## Question Description

You are tasked with designing a consistent hashing load balancer for a distributed key-value store. The key-value store consists of multiple server nodes, and your load balancer needs to distribute incoming requests (identified by a unique key) across these nodes in a way that minimizes disruption when nodes are added or removed.

**Details:**

1.  **Consistent Hashing Ring:** Implement a consistent hashing ring. This ring should be represented as a sorted map (e.g., a `TreeMap` in Java), where the keys are hash values (integers) and the values are the server node identifiers (strings).

2.  **Virtual Nodes (Replicas):** To improve distribution and fault tolerance, each physical server node should be represented by multiple virtual nodes (replicas) on the ring. The number of virtual nodes per physical node is a configurable parameter.  The virtual node identifier should be constructed as `"{nodeId}-{replicaIndex}"`. For example, if server node "node1" has 3 virtual nodes, they would be "node1-0", "node1-1", and "node1-2".

3.  **Adding/Removing Nodes:** Implement methods to add and remove server nodes from the consistent hashing ring. When a node is added, its virtual nodes should be added to the ring. When a node is removed, all its virtual nodes should be removed from the ring.

4.  **Key Distribution:** Implement a method that, given a key, determines the server node responsible for handling that key. This is done by hashing the key, finding the smallest hash value on the ring that is greater than or equal to the key's hash value (the "ceiling" in the sorted map). If no such value exists (the key's hash is larger than all values in the ring), the key should be assigned to the node with the smallest hash value on the ring (wrapping around the ring).

5.  **Load Balancing:** Your load balancer should distribute requests across the server nodes as evenly as possible.  In other words, given a large number of random keys, the number of keys assigned to each node should be roughly proportional to the number of virtual nodes it has.

6.  **Minimizing Disruption:** When a node is added or removed, only a small fraction of the keys should be re-assigned to different nodes. This is the key benefit of consistent hashing.

7. **Hash Function:** Use a standard hash function like MurmurHash3 or SHA-256 to generate the hash values for keys and node identifiers.  The hash function should return a 32-bit integer.

**Constraints:**

*   The number of server nodes can vary dynamically.
*   The number of virtual nodes per server node is configurable.
*   The hash function should be efficient and produce a reasonably uniform distribution of hash values.
*   The load balancer should be thread-safe (consider concurrent access).
*   The key distribution method should be efficient (logarithmic time complexity is desired).
*   Minimize memory usage where possible.

**Requirements:**

1.  Implement a class named `ConsistentHashingLoadBalancer`.

2.  The `ConsistentHashingLoadBalancer` class should have the following methods:

    *   `ConsistentHashingLoadBalancer(int virtualNodes)`: Constructor that initializes the load balancer with the specified number of virtual nodes per physical node.
    *   `addNode(String nodeId)`: Adds a server node to the consistent hashing ring.
    *   `removeNode(String nodeId)`: Removes a server node from the consistent hashing ring.
    *   `getNode(String key)`: Returns the identifier of the server node responsible for handling the given key. Returns `null` if there are no nodes in the ring.
    *   `getRingSize()`: Returns the number of virtual nodes in the ring.

**Example:**

```java
ConsistentHashingLoadBalancer loadBalancer = new ConsistentHashingLoadBalancer(3); // 3 virtual nodes per node

loadBalancer.addNode("node1");
loadBalancer.addNode("node2");
loadBalancer.addNode("node3");

String key1 = "someKey";
String nodeForKey1 = loadBalancer.getNode(key1); // Returns "node1", "node2", or "node3" based on consistent hashing

loadBalancer.removeNode("node2");
String key2 = "anotherKey";
String nodeForKey2 = loadBalancer.getNode(key2); // Returns "node1" or "node3"

```
This problem challenges the solver to implement a core distributed systems component while considering efficiency, thread safety, and scalability. The virtual nodes and consistent hashing ring elements makes this a challenging coding problem.
