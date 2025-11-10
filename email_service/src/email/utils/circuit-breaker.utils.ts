export class CircuitBreaker {
  private failureCount = 0;
  private successThreshold = 5;
  private failureThreshold = 3;
  private cooldownTime = 10000;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private lastFailureTime: number = 0;

  canRequest(): boolean {
    if (this.state === 'OPEN') {
      const now = Date.now();
      if (now - this.lastFailureTime > this.cooldownTime) {
        this.state = 'HALF_OPEN';
        return true;
      }
      return false;
    }
    return true;
  }

  recordSuccess(): void {
    if (this.state === 'HALF_OPEN') {
      this.failureCount = 0;
      this.state = 'CLOSED';
    }
  }

  recordFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}
