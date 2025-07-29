import numpy as np

def generate_test_stream(length=1000, anomaly_rate=0.01, seasonality=False):
    if seasonality:
        base = np.sin(np.linspace(0, 10*np.pi, length))
        noise = np.random.normal(0, 0.2, length)
        data = base + noise
    else:
        data = np.random.normal(0, 1, length)
    
    anomalies = np.random.choice(length, int(length * anomaly_rate), replace=False)
    data[anomalies] += 10 * np.random.rand(len(anomalies))
    
    # Add some missing values
    missing = np.random.choice(length, int(length * 0.05), replace=False)
    data[missing] = None
    
    return iter(data.tolist())