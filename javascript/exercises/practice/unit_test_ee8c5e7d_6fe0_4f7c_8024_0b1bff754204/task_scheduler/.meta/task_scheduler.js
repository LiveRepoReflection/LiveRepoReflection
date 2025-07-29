const EventEmitter = require('events');

class PriorityQueue {
  constructor(comparator) {
    this._heap = [];
    this._comparator = comparator;
  }
  
  size() {
    return this._heap.length;
  }
  
  isEmpty() {
    return this.size() === 0;
  }
  
  peek() {
    return this._heap[0];
  }
  
  push(value) {
    this._heap.push(value);
    this._siftUp();
  }
  
  pop() {
    const poppedValue = this.peek();
    const bottom = this.size() - 1;
    if (bottom > 0) {
      this._swap(0, bottom);
    }
    this._heap.pop();
    this._siftDown();
    return poppedValue;
  }
  
  _parent(index) {
    return Math.floor((index - 1) / 2);
  }
  
  _leftChild(index) {
    return index * 2 + 1;
  }
  
  _rightChild(index) {
    return index * 2 + 2;
  }
  
  _siftUp() {
    let nodeIndex = this.size() - 1;
    while (nodeIndex > 0) {
      const parentIndex = this._parent(nodeIndex);
      if (this._comparator(this._heap[nodeIndex], this._heap[parentIndex]) < 0) {
        this._swap(nodeIndex, parentIndex);
        nodeIndex = parentIndex;
      } else {
        break;
      }
    }
  }
  
  _siftDown() {
    let nodeIndex = 0;
    const length = this.size();
    while (this._leftChild(nodeIndex) < length) {
      let smallestChild = this._leftChild(nodeIndex);
      const rightChild = this._rightChild(nodeIndex);
      if (rightChild < length && this._comparator(this._heap[rightChild], this._heap[smallestChild]) < 0) {
        smallestChild = rightChild;
      }
      if (this._comparator(this._heap[smallestChild], this._heap[nodeIndex]) < 0) {
        this._swap(smallestChild, nodeIndex);
        nodeIndex = smallestChild;
      } else {
        break;
      }
    }
  }
  
  _swap(i, j) {
    [this._heap[i], this._heap[j]] = [this._heap[j], this._heap[i]];
  }
}

class TaskScheduler extends EventEmitter {
  constructor(workerNodes) {
    super();
    // Initialize workers: each worker is represented as an object with id and busy status.
    this.workers = workerNodes.map(id => ({ id, busy: false }));
    // Comparator for tasks: higher priority tasks come first.
    // If same priority, task with earlier deadline comes first.
    this.taskQueue = new PriorityQueue((taskA, taskB) => {
      if (taskA.priority !== taskB.priority) {
        // higher priority => lower comparator result
        return taskA.priority > taskB.priority ? -1 : 1;
      }
      if (taskA.deadline !== taskB.deadline) {
        return taskA.deadline < taskB.deadline ? -1 : 1;
      }
      return 0;
    });
    this._isRunning = false;
  }

  scheduleTask(task) {
    // Initialize attempt count if not already set.
    if (!task.attempt) {
      task.attempt = 1;
    }
    this.taskQueue.push(task);
  }
  
  start() {
    this._isRunning = true;
    this._scheduleLoop();
  }
  
  stop() {
    this._isRunning = false;
  }
  
  _getAvailableWorker() {
    return this.workers.find(worker => !worker.busy);
  }
  
  _scheduleLoop() {
    if (!this._isRunning) return;
    // While there are available workers and tasks in queue, assign tasks.
    let worker = this._getAvailableWorker();
    while (worker && !this.taskQueue.isEmpty()) {
      const task = this.taskQueue.pop();
      this._assignTask(task, worker);
      worker = this._getAvailableWorker();
    }
    // Continue loop in next tick.
    setTimeout(() => this._scheduleLoop(), 0);
  }
  
  _assignTask(task, worker) {
    worker.busy = true;
    this.emit('taskStarted', { taskId: task.taskId, workerId: worker.id, attempt: task.attempt });
    // Execute the task.
    Promise.resolve()
      .then(() => task.execute())
      .then(() => {
        this.emit('taskCompleted', { taskId: task.taskId, workerId: worker.id, attempt: task.attempt });
        worker.busy = false;
      })
      .catch((err) => {
        this.emit('taskFailed', { taskId: task.taskId, workerId: worker.id, attempt: task.attempt, error: err });
        worker.busy = false;
        // Increment attempt and requeue the task.
        task.attempt++;
        this.scheduleTask(task);
      });
  }
}

module.exports = {
  TaskScheduler
};