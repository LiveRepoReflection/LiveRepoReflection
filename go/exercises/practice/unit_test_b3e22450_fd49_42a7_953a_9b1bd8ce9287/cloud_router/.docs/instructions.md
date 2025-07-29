## Project Name

`CloudScaleRouter`

## Question Description

You are designing a distributed router system for a large cloud provider. This system needs to handle a massive number of routing rules and efficiently forward packets based on complex matching criteria.

Each router in the system receives packets. Each packet has a destination IP address and a set of arbitrary key-value attribute pairs (strings).

Each router also has a set of routing rules. Each rule consists of:

1.  **Matching Criteria:** A set of conditions that must be met for the rule to apply. Each condition is a key-value pair. A packet matches a rule if all the key-value conditions in the rule are present and have the same values in the packet's attributes. If a rule has no conditions, it matches all packets.

2.  **Forwarding Action:** A target router ID to forward the packet to.

When a router receives a packet, it must find the *highest priority* matching rule and forward the packet accordingly. Rule priority is defined by the number of matching criteria conditions. The rule with most matching criteria conditions has the highest priority. If multiple rules have the same highest number of matching criteria conditions, the rule that was added earliest has higher priority.

Your task is to implement a system that simulates this distributed router system.

Specifically, you need to implement the following:

*   `AddRule(routerID string, ruleID string, conditions map[string]string, targetRouterID string)`: Adds a new routing rule to the specified router. The conditions map specifies the matching criteria.
*   `RoutePacket(routerID string, destinationIP string, attributes map[string]string)`: Routes a packet through the specified router. It should return the ID of the next router to forward the packet to, according to the rules described above. If no rule matches, return an empty string.
*   `RemoveRule(routerID string, ruleID string)`: Removes a route from a specified router.

**Constraints:**

*   The system must handle a large number of routers (up to 10,000) and rules per router (up to 10,000).
*   The `RoutePacket` function must be highly performant, as it will be called frequently. Aim for O(log(n)) time complexity, where n is the number of rules in the router.
*   The number of attributes per packet will be limited (up to 10).
*   Router and Rule IDs are unique strings.
*   Conditions within a rule are also unique. There will be no conditions with the same key but different values in a rule.
*   You must consider concurrency safety and potential race conditions, as multiple routers may be processing packets simultaneously.
*   Assume that the system memory is limited, and avoid unnecessary memory allocations.
*   Assume there is no clock skew between router nodes.

**Example:**

```
AddRule("router1", "rule1", map[string]string{"color": "red", "size": "large"}, "router2")
AddRule("router1", "rule2", map[string]string{"color": "red"}, "router3")
AddRule("router1", "rule3", map[string]string{}, "router4") // Matches all

RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red", "size": "large", "shape": "circle"}) // Returns "router2"
RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red", "shape": "circle"}) // Returns "router3"
RoutePacket("router1", "1.2.3.4", map[string]string{"shape": "circle"}) // Returns "router4"
```

**Bonus:**

*   Implement a mechanism to dynamically update routing rules without interrupting packet forwarding.
*   Implement metrics to track the performance of the router system (e.g., packet forwarding rate, rule matching latency).
