class Heap {
  constructor(comparator) {
    this.data = [];
    this.comparator = comparator;
  }

  size() {
    return this.data.length;
  }

  peek() {
    return this.data.length === 0 ? null : this.data[0];
  }

  push(value) {
    this.data.push(value);
    this._heapifyUp();
  }

  pop() {
    if (this.data.length === 0) return null;
    const top = this.data[0];
    const end = this.data.pop();
    if (this.data.length > 0) {
      this.data[0] = end;
      this._heapifyDown();
    }
    return top;
  }

  _heapifyUp() {
    let index = this.data.length - 1;
    while (index > 0) {
      let parentIndex = Math.floor((index - 1) / 2);
      if (this.comparator(this.data[index], this.data[parentIndex]) < 0) {
        [this.data[index], this.data[parentIndex]] = [this.data[parentIndex], this.data[index]];
        index = parentIndex;
      } else {
        break;
      }
    }
  }

  _heapifyDown() {
    let index = 0;
    const length = this.data.length;
    while (true) {
      let left = 2 * index + 1;
      let right = 2 * index + 2;
      let smallest = index;
      if (left < length && this.comparator(this.data[left], this.data[smallest]) < 0) {
        smallest = left;
      }
      if (right < length && this.comparator(this.data[right], this.data[smallest]) < 0) {
        smallest = right;
      }
      if (smallest !== index) {
        [this.data[index], this.data[smallest]] = [this.data[smallest], this.data[index]];
        index = smallest;
      } else {
        break;
      }
    }
  }
}

class MedianTracker {
  constructor() {
    // lower: max heap to store lower half values (invert comparator: larger numbers come first)
    this.lower = new Heap((a, b) => b - a);
    // upper: min heap to store upper half values
    this.upper = new Heap((a, b) => a - b);
  }

  addDataPoint(value) {
    if (this.lower.size() === 0 || value <= this.lower.peek()) {
      this.lower.push(value);
    } else {
      this.upper.push(value);
    }

    // Rebalance the heaps to ensure lower has equal or one more element than upper
    if (this.lower.size() > this.upper.size() + 1) {
      this.upper.push(this.lower.pop());
    } else if (this.upper.size() > this.lower.size()) {
      this.lower.push(this.upper.pop());
    }
  }

  getMedian() {
    const totalSize = this.lower.size() + this.upper.size();
    if (totalSize === 0) return null;
    if (totalSize % 2 === 1) {
      return this.lower.peek();
    } else {
      return (this.lower.peek() + this.upper.peek()) / 2;
    }
  }
}

module.exports = { MedianTracker };