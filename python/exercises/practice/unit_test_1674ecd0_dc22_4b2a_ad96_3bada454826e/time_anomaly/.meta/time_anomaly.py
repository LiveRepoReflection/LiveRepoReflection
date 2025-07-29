import math
from collections import deque

def anomaly_detector(data_stream, N, M, k):
    raw_window = deque()
    ewma_window = deque(maxlen=M)
    raw_sum = 0.0
    raw_sum_sq = 0.0
    current_ewma = None
    C = 10.0  # Constant for adaptive alpha calculation

    for data in data_stream:
        # Handle missing values by imputing with the previous EWMA or 0 if not available.
        if data is None:
            if current_ewma is None:
                current_ewma = 0.0
            # If not enough EWMA values, set threshold to infinity to avoid false anomaly detection.
            if len(ewma_window) < 2:
                threshold = float('inf')
            else:
                mean_ewma = sum(ewma_window) / len(ewma_window)
                var_ewma = (sum(x * x for x in ewma_window) / len(ewma_window)) - (mean_ewma * mean_ewma)
                if var_ewma < 0:
                    var_ewma = 0.0
                threshold = k * math.sqrt(var_ewma)
            yield (data, False, current_ewma, threshold)
            continue

        # Manage the sliding window for raw data.
        if len(raw_window) == N:
            old = raw_window.popleft()
            raw_sum -= old
            raw_sum_sq -= old * old
        raw_window.append(data)
        raw_sum += data
        raw_sum_sq += data * data

        n = len(raw_window)
        if n > 0:
            mean_raw = raw_sum / n
            variance = (raw_sum_sq / n) - (mean_raw * mean_raw)
            if variance < 0:
                variance = 0.0
        else:
            variance = 0.0

        # Adaptively compute the decay factor alpha.
        # A higher variance gives a smaller alpha (faster decay), and vice-versa.
        alpha = 1 - (variance / (variance + C))
        if alpha > 0.9:
            alpha = 0.9
        if alpha < 0.1:
            alpha = 0.1

        # Update the EWMA: initialize if necessary.
        if current_ewma is None:
            current_ewma = data
        else:
            current_ewma = alpha * data + (1 - alpha) * current_ewma

        ewma_window.append(current_ewma)

        # Compute the dynamic threshold using the standard deviation of the recent EWMA values.
        if len(ewma_window) < 2:
            threshold = float('inf')
        else:
            mean_ewma = sum(ewma_window) / len(ewma_window)
            var_ewma = (sum(x * x for x in ewma_window) / len(ewma_window)) - (mean_ewma * mean_ewma)
            if var_ewma < 0:
                var_ewma = 0.0
            sd = math.sqrt(var_ewma)
            threshold = k * sd

        # Determine if the current data point is anomalous.
        if threshold == float('inf'):
            is_anomaly = False
        else:
            is_anomaly = abs(data - current_ewma) > threshold

        yield (data, is_anomaly, current_ewma, threshold)