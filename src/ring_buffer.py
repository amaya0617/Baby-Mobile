import numpy as np
import threading


class RingBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = np.zeros(capacity, dtype=np.float32)
        self.write_pos = 0
        self.size = 0
        self.lock = threading.Lock()

    def write(self, data: np.ndarray):
        """Write 1D float32 audio samples into the buffer."""
        data = data.astype(np.float32)
        n = len(data)

        with self.lock:
            if n >= self.capacity:
                # keep only the last 'capacity' samples
                self.buffer[:] = data[-self.capacity:]
                self.write_pos = 0
                self.size = self.capacity
                return

            end = self.write_pos + n
            if end <= self.capacity:
                self.buffer[self.write_pos:end] = data
            else:
                first = self.capacity - self.write_pos
                self.buffer[self.write_pos:] = data[:first]
                self.buffer[:end % self.capacity] = data[first:]

            self.write_pos = end % self.capacity
            self.size = min(self.capacity, self.size + n)

    def read_latest(self, n):
        """Read the latest n samples (returns fewer if not enough yet)."""
        with self.lock:
            n = min(n, self.size)
            start = (self.write_pos - n) % self.capacity
            if start + n <= self.capacity:
                return self.buffer[start:start+n].copy()
            else:
                first = self.capacity - start
                return np.concatenate(
                    (self.buffer[start:], self.buffer[:n-first])
                ).copy()
