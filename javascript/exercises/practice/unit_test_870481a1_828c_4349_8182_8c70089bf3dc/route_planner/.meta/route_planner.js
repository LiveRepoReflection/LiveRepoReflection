class MinHeap {
  constructor() {
    this.heap = [];
  }

  push(item) {
    this.heap.push(item);
    this._bubbleUp(this.heap.length - 1);
  }

  pop() {
    if (this.heap.length === 0) return null;
    const top = this.heap[0];
    const end = this.heap.pop();
    if (this.heap.length > 0) {
      this.heap[0] = end;
      this._bubbleDown(0);
    }
    return top;
  }

  size() {
    return this.heap.length;
  }

  _bubbleUp(index) {
    while (index > 0) {
      const parentIdx = Math.floor((index - 1) / 2);
      if (this.heap[index].cost < this.heap[parentIdx].cost) {
        [this.heap[index], this.heap[parentIdx]] = [this.heap[parentIdx], this.heap[index]];
        index = parentIdx;
      } else {
        break;
      }
    }
  }

  _bubbleDown(index) {
    const length = this.heap.length;
    while (true) {
      let leftIdx = 2 * index + 1;
      let rightIdx = 2 * index + 2;
      let smallest = index;

      if (leftIdx < length && this.heap[leftIdx].cost < this.heap[smallest].cost) {
        smallest = leftIdx;
      }
      if (rightIdx < length && this.heap[rightIdx].cost < this.heap[smallest].cost) {
        smallest = rightIdx;
      }
      if (smallest !== index) {
        [this.heap[index], this.heap[smallest]] = [this.heap[smallest], this.heap[index]];
        index = smallest;
      } else {
        break;
      }
    }
  }
}

function dijkstra(graph, source, target) {
  const distances = {};
  const visited = {};
  const heap = new MinHeap();

  // Initialize distances
  for (const node in graph) {
    distances[node] = Infinity;
  }
  distances[source] = 0;
  heap.push({ node: source, cost: 0 });

  while (heap.size() > 0) {
    const current = heap.pop();
    const currentNode = current.node;
    const currentCost = current.cost;
    
    if (visited[currentNode]) continue;
    visited[currentNode] = true;
    
    if (currentNode === target) {
      return currentCost;
    }
    
    if (!graph[currentNode]) continue;
    for (const neighbor of graph[currentNode]) {
      const nextNode = neighbor.node;
      const pathCost = currentCost + neighbor.cost;
      if (pathCost < (distances[nextNode] || Infinity)) {
        distances[nextNode] = pathCost;
        heap.push({ node: nextNode, cost: pathCost });
      }
    }
  }
  return Infinity;
}

function calculateFastestRoute(edges, trafficData, deliveryPoints) {
  // Map traffic data for quick lookup, key format: "src-dest"
  const trafficMap = new Map();
  for (const [src, dest, factor] of trafficData) {
    const key = `${src}-${dest}`;
    trafficMap.set(key, factor);
  }
  
  // Build the graph
  const graph = {};
  for (const [src, dest, baseTime] of edges) {
    const key = `${src}-${dest}`;
    const factor = trafficMap.has(key) ? trafficMap.get(key) : 1;
    const cost = baseTime * factor;
    if (!graph[src]) {
      graph[src] = [];
    }
    graph[src].push({ node: dest, cost });
  }
  
  let totalCost = 0;
  // For each consecutive delivery point, calculate shortest path cost.
  for (let i = 0; i < deliveryPoints.length - 1; i++) {
    const source = deliveryPoints[i];
    const target = deliveryPoints[i + 1];
    const cost = dijkstra(graph, source, target);
    if (cost === Infinity) {
      return -1;
    }
    totalCost += cost;
  }
  
  return totalCost;
}

module.exports = { calculateFastestRoute };