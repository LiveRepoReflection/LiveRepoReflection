class Service {
  constructor(name, successRate = 1) {
    this.name = name;
    this.successRate = successRate;
    this.stagingArea = null; // Simulate a staging area
    this.committed = false;
  }

  async prepare(txid, data) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() <= this.successRate) {
          this.stagingArea = { ...data };
          console.log(`${this.name}: Prepared transaction ${txid}`);
          resolve(true);
        } else {
          console.error(`${this.name}: Failed to prepare transaction ${txid}`);
          reject(new Error(`${this.name}: Prepare failed`));
        }
      }, Math.random() * 100);
    });
  }

  async commit(txid) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() <= this.successRate) {
          if (this.stagingArea && !this.committed) {
            // Simulate committing changes
            this.data = { ...this.stagingArea };
            this.stagingArea = null;
            this.committed = true;
            console.log(`${this.name}: Committed transaction ${txid}`);
            resolve(true);
          } else {
            console.warn(`${this.name}: Already committed or no staging area for transaction ${txid}`);
            resolve(true); // Idempotent
          }
        } else {
          console.error(`${this.name}: Failed to commit transaction ${txid}`);
          reject(new Error(`${this.name}: Commit failed`));
        }
      }, Math.random() * 100);
    });
  }

  async abort(txid) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (Math.random() <= this.successRate) {
          this.stagingArea = null; // Discard changes
          this.committed = false;
          console.log(`${this.name}: Aborted transaction ${txid}`);
          resolve(true);
        } else {
          console.error(`${this.name}: Failed to abort transaction ${txid}`);
          reject(new Error(`${this.name}: Abort failed`));
        }
      }, Math.random() * 100);
    });
  }
}

module.exports = { Service };