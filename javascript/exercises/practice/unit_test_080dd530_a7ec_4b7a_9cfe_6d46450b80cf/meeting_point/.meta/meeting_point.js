'use strict';

class PriorityQueue {
  constructor() {
    this.heap = [];
  }
  
  push(element) {
    this.heap.push(element);
    this._bubbleUp(this.heap.length - 1);
  }
  
  pop() {
    if (this.heap.length === 0) return null;
    const top = this.heap[0];
    const bottom = this.heap.pop();
    if (this.heap.length > 0) {
      this.heap[0] = bottom;
      this._sinkDown(0);
    }
    return top;
  }
  
  _bubbleUp(n) {
    const element = this.heap[n];
    while (n > 0) {
      const parentN = Math.floor((n + 1) / 2) - 1;
      const parent = this.heap[parentN];
      if (element.distance >= parent.distance) break;
      this.heap[parentN] = element;
      this.heap[n] = parent;
      n = parentN;
    }
  }
  
  _sinkDown(n) {
    const length = this.heap.length;
    const element = this.heap[n];
    
    while (true) {
      const child2N = (n + 1) * 2;
      const child1N = child2N - 1;
      let swap = null;
      
      if (child1N < length) {
        const child1 = this.heap[child1N];
        if (child1.distance < element.distance) {
          swap = child1N;
        }
      }
      
      if (child2N < length) {
        const child2 = this.heap[child2N];
        if (
          (swap === null && child2.distance < element.distance) || 
          (swap !== null && child2.distance < this.heap[child1N].distance)
        ) {
          swap = child2N;
        }
      }
      
      if (swap === null) break;
      
      this.heap[n] = this.heap[swap];
      this.heap[swap] = element;
      n = swap;
    }
  }
  
  isEmpty() {
    return this.heap.length === 0;
  }
}

function dijkstra(graph, source, n) {
  const distances = new Array(n).fill(Infinity);
  distances[source] = 0;
  const pq = new PriorityQueue();
  pq.push({ node: source, distance: 0 });
  
  while (!pq.isEmpty()) {
    const current = pq.pop();
    const currentNode = current.node;
    const currentDistance = current.distance;
    
    if (currentDistance > distances[currentNode]) continue;
    
    const neighbors = graph[currentNode];
    for (let i = 0; i < neighbors.length; i++) {
      const [neighbor, weight] = neighbors[i];
      const newDistance = currentDistance + weight;
      if (newDistance < distances[neighbor]) {
        distances[neighbor] = newDistance;
        pq.push({ node: neighbor, distance: newDistance });
      }
    }
  }
  
  return distances;
}

function optimalMeetingPoint(n, roads, meetingParticipants) {
  // Build undirected graph as an adjacency list
  const graph = new Array(n);
  for (let i = 0; i < n; i++) {
    graph[i] = [];
  }
  
  for (let i = 0; i < roads.length; i++) {
    const [u, v, w] = roads[i];
    graph[u].push([v, w]);
    graph[v].push([u, w]);
  }
  
  // Initialize an array to store maximum congestion cost for each node.
  const maxCostAtNode = new Array(n).fill(0);
  // For each meeting participant, compute distances to all nodes.
  for (let i = 0; i < meetingParticipants.length; i++) {
    const source = meetingParticipants[i];
    const distances = dijkstra(graph, source, n);
    for (let j = 0; j < n; j++) {
      // If participant cannot reach this node, mark as Infinity.
      if (distances[j] === Infinity) {
        maxCostAtNode[j] = Infinity;
      } else if (maxCostAtNode[j] !== Infinity) {
        maxCostAtNode[j] = Math.max(maxCostAtNode[j], distances[j]);
      }
    }
  }
  
  // Find the meeting point that minimizes the maximum congestion cost.
  let optimalLocation = -1;
  let optimalCost = Infinity;
  
  for (let i = 0; i < n; i++) {
    if (maxCostAtNode[i] < optimalCost) {
      optimalCost = maxCostAtNode[i];
      optimalLocation = i;
    }
  }
  
  return optimalLocation;
}

module.exports = { optimalMeetingPoint };