class MinHeap {
  constructor() {
    this.heap = [];
  }

  push(item) {
    this.heap.push(item);
    this._siftUp(this.heap.length - 1);
  }

  pop() {
    if (this.heap.length === 0) return null;
    const top = this.heap[0];
    const end = this.heap.pop();
    if (this.heap.length > 0) {
      this.heap[0] = end;
      this._siftDown(0);
    }
    return top;
  }

  _siftUp(index) {
    let parent = Math.floor((index - 1) / 2);
    while (index > 0 && this.heap[index].totalCost < this.heap[parent].totalCost) {
      [this.heap[index], this.heap[parent]] = [this.heap[parent], this.heap[index]];
      index = parent;
      parent = Math.floor((index - 1) / 2);
    }
  }

  _siftDown(index) {
    const length = this.heap.length;
    while (true) {
      let left = 2 * index + 1;
      let right = 2 * index + 2;
      let smallest = index;
      if (left < length && this.heap[left].totalCost < this.heap[smallest].totalCost) {
        smallest = left;
      }
      if (right < length && this.heap[right].totalCost < this.heap[smallest].totalCost) {
        smallest = right;
      }
      if (smallest === index) break;
      [this.heap[index], this.heap[smallest]] = [this.heap[smallest], this.heap[index]];
      index = smallest;
    }
  }

  isEmpty() {
    return this.heap.length === 0;
  }
}

function findOptimalRoute(cityMap, start, end) {
  if (!cityMap[start] || (start === end && !(cityMap[start] && cityMap[start].length))) {
    return { totalTime: start === end ? 0 : -1, route: start === end ? [start] : [] };
  }

  // bestTimes records the earliest arrival time for each node.
  const bestTimes = {};
  // Priority queue element: { node, totalCost, currentTime, route }
  const heap = new MinHeap();
  heap.push({ node: start, totalCost: 0, currentTime: 0, route: [start] });
  bestTimes[start] = 0;

  while (!heap.isEmpty()) {
    const current = heap.pop();
    const { node, totalCost, currentTime, route } = current;

    // If we have already a better arrival time for this node, skip.
    if (bestTimes[node] < currentTime) {
      continue;
    }

    if (node === end) {
      return { totalTime: Number(totalCost.toFixed(2)), route: route };
    }

    const neighbors = cityMap[node] || [];
    for (const edge of neighbors) {
      const edgeCongestion = edge.congestionFunction(currentTime);
      const travelTime = edge.travelTime * edgeCongestion;
      const newCost = totalCost + travelTime;
      const newTime = currentTime + travelTime;
      const newRoute = route.concat(edge.to);

      if (bestTimes[edge.to] === undefined || newTime < bestTimes[edge.to]) {
        bestTimes[edge.to] = newTime;
        heap.push({ node: edge.to, totalCost: newCost, currentTime: newTime, route: newRoute });
      }
    }
  }

  return { totalTime: -1, route: [] };
}

module.exports = { findOptimalRoute };