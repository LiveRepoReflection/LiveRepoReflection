class RateLimiter {
  constructor(initialWeights, capacity, preservedState) {
    this.capacity = capacity;
    this.serviceWeights = { ...initialWeights };
    if (
      preservedState &&
      typeof preservedState === "object" &&
      preservedState.remainingCapacity !== undefined &&
      preservedState.serviceQuotas
    ) {
      this.remainingCapacity = preservedState.remainingCapacity;
      this.serviceQuotas = { ...preservedState.serviceQuotas };
    } else {
      this.resetWindow();
    }
  }

  resetWindow() {
    this.remainingCapacity = this.capacity;
    const totalWeight = Object.values(this.serviceWeights).reduce(
      (acc, w) => acc + w,
      0
    );
    this.serviceQuotas = {};
    let allocated = 0;
    const remainders = [];
    for (const service in this.serviceWeights) {
      const exact = (this.capacity * this.serviceWeights[service]) / totalWeight;
      const quota = Math.floor(exact);
      this.serviceQuotas[service] = quota;
      allocated += quota;
      remainders.push({ service, remainder: exact - quota });
    }
    let leftover = this.capacity - allocated;
    remainders.sort((a, b) => b.remainder - a.remainder);
    for (let i = 0; i < leftover; i++) {
      this.serviceQuotas[remainders[i].service] += 1;
    }
  }

  allowRequest(service) {
    if (!(service in this.serviceWeights)) return false;
    if (this.serviceQuotas[service] > 0) {
      this.serviceQuotas[service]--;
      this.remainingCapacity--;
      return true;
    }
    return false;
  }

  updateWeight(service, newWeight) {
    this.serviceWeights[service] = newWeight;
    const totalRemaining = this.remainingCapacity;
    const totalNewWeight = Object.values(this.serviceWeights).reduce(
      (acc, w) => acc + w,
      0
    );
    let allocated = 0;
    const newQuotas = {};
    const remainders = [];
    for (const svc in this.serviceWeights) {
      const exact = (totalRemaining * this.serviceWeights[svc]) / totalNewWeight;
      const quota = Math.floor(exact);
      newQuotas[svc] = quota;
      allocated += quota;
      remainders.push({ service: svc, remainder: exact - quota });
    }
    let leftover = totalRemaining - allocated;
    remainders.sort((a, b) => b.remainder - a.remainder);
    for (let i = 0; i < leftover; i++) {
      newQuotas[remainders[i].service] += 1;
    }
    this.serviceQuotas = newQuotas;
  }

  getState() {
    return {
      remainingCapacity: this.remainingCapacity,
      serviceQuotas: { ...this.serviceQuotas },
    };
  }
}

module.exports = { RateLimiter };