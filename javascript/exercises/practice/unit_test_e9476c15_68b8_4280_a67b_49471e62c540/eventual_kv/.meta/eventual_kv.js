class Node {
  constructor(name) {
    this.name = name;
    this.store = new Map();
    this.online = true;
    this.lastTimestamp = 0;
  }

  get(key) {
    const entry = this.store.get(key);
    return entry ? entry.value : undefined;
  }

  put(key, value, providedTimestamp) {
    let timestamp;
    if (providedTimestamp !== undefined) {
      timestamp = providedTimestamp;
    } else {
      const now = Date.now();
      timestamp = now > this.lastTimestamp ? now : this.lastTimestamp + 1;
    }
    this.lastTimestamp = timestamp;
    const current = this.store.get(key);
    if (!current || timestamp >= current.timestamp) {
      this.store.set(key, { value, timestamp });
    }
  }

  setOnline(status) {
    this.online = status;
  }

  synchronize(peers) {
    if (!this.online) return;

    for (const peer of peers) {
      if (!peer.online) continue;

      // Propagate this node's updates to the peer.
      for (const [key, entry] of this.store.entries()) {
        peer._applyUpdate(key, entry.value, entry.timestamp);
      }

      // Receive peer's updates into this node.
      for (const [key, entry] of peer.store.entries()) {
        this._applyUpdate(key, entry.value, entry.timestamp);
      }
    }
  }

  _applyUpdate(key, value, timestamp) {
    const current = this.store.get(key);
    if (!current || timestamp > current.timestamp) {
      this.store.set(key, { value, timestamp });
      if (timestamp > this.lastTimestamp) {
        this.lastTimestamp = timestamp;
      }
    }
  }
}

module.exports = { Node };